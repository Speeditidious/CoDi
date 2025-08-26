import sys
sys.path.insert(0, '.')
import logging
import argparse
import os
import re
import copy
import tiktoken
import numpy as np
from tqdm import tqdm
from collections import Counter

from global_utils import *
from generation_utils import is_character_reaction

story_ab_categories = ["Plot", "Development", "Language Use", "Anthropomorphism", "Character Fidelity", "Overall"]
story_ab_categories_vs_gold = ["Plot", "Creativity", "Development", "Language Use", "Overall"]

def parse_args():
    parser = argparse.ArgumentParser()
    ## Path to gen data to stat
    parser.add_argument('--gen-data-file', type=str, required=True)
    ## Path to eval data to stat
    parser.add_argument('--eval-data-file', type=str, required=True)
    ## Directory of save stat result
    parser.add_argument('--out-dir', type=str, required=True)
    
    args = parser.parse_args()
    args.data_file = args.gen_data_file
    
    return args
    
def log_stat_setting(logger, args):
    logger.info('===Stat Settings===')
    logger.info(f'Generated Data File: {args.gen_data_file}')
    logger.info(f'Evaluated Data File: {args.eval_data_file}')
    logger.info(f'Out Directory: {args.out_dir}')

def estimate_word_count(text):
    return len(text.split())

def estimate_token_count(text):
    enc = tiktoken.encoding_for_model("gpt-4o")
    return len(enc.encode(text))

def estimate_turn_count(text):
    return len(text.splitlines())

def estimate_turn_count_dramatron(text):
    return(len(text.split('\n\n')))

def estimate_character_reaction_count(text):
    character_reaction_cnt = 0
    for line in text.splitlines():
        if is_character_reaction([line]):
            character_reaction_cnt += 1
    return character_reaction_cnt

def append_story_ab_result(llm_response_ab, llm_response_ba, logger, is_vs_gold=False):
    def extract_story_ab_result(llm_response, logger, is_vs_gold=False):
        
        llm_response = llm_response.replace('*', '')
        llm_response_lines = llm_response.splitlines()
            
        result = {}
        
        if is_vs_gold:
            category_list = story_ab_categories_vs_gold
        else:
            category_list = story_ab_categories
            
        for category in category_list:
            found = False
            
            ## {category}: ?Story A|B|Same
            for line in llm_response_lines:
                summary_pattern = rf"{category}\s*:\s*(?:Story\s*)?(A|B|Same)"
                summary_pattern_match = re.search(summary_pattern, line, re.IGNORECASE)
                
                if summary_pattern_match:
                    result[category.lower().replace(" ", "_")] = summary_pattern_match.group(1).capitalize()
                    found = True
                    break
            
            ## {category} & ?Story A|B|Same in one line
            if not found:
                for line in llm_response_lines:
                    if re.search(r'(A|B)\s*:', line):
                        continue
                    if re.search(re.escape(category), line, re.IGNORECASE) and re.search(r'\b(Same|A|B)\b', line, re.IGNORECASE):
                        match = re.search(r'\b(Same|A|B)\b', line, re.IGNORECASE)
                        if match:
                            result[category.lower().replace(" ", "_")] = match.group(1).capitalize()
                            found = True
                            break
                        
            ## {category} \n ... \n Better Story: A|B|Same
            LOOK_UP_LINE_MAX = 5
            if not found:
                for idx, line in enumerate(llm_response_lines):
                    if re.search(re.escape(category), line, re.IGNORECASE):
                        for offset in range(1, LOOK_UP_LINE_MAX+1):
                            if idx + offset < len(llm_response_lines):
                                target_line = llm_response_lines[idx + offset]
                                if "better" in target_line.lower() and re.search(r'\b(Same|A|B)\b', target_line, re.IGNORECASE):
                                    match = re.search(r'\b(Same|A|B)\b', target_line, re.IGNORECASE)
                                    result[category.lower().replace(" ", "_")] = match.group(1).capitalize()
                                    found = True
                                    break
                        if found:
                            break
            
            if not found:
                result[category.lower().replace(" ", "_")] = 'SAME'
            
        return result
    
    result_ab = extract_story_ab_result(llm_response_ab, logger, is_vs_gold)
    result_ba = extract_story_ab_result(llm_response_ba, logger, is_vs_gold)
    
    if result_ab is None:
        logger.debug(f'Invalid Format while extracting Story AB result.\n{llm_response_ab}')
    if result_ba is None:
        logger.debug(f'Invalid Format while extracting Story BA result.\n{llm_response_ba}')
    
    story_ab_result = {}
    for k, _ in result_ab.items():
        if result_ab[k] != result_ba[k]:
            if 'S' in result_ab[k].upper() or 'SAME' in result_ab[k].upper():
                if 'A' in result_ba[k].upper():
                    story_ab_result[k] = 'B'
                elif 'B' in result_ba[k].upper():
                    story_ab_result[k] = 'A'
                else:
                    story_ab_result[k] = 'DRAW'
            else:
                story_ab_result[k] = copy.deepcopy(result_ab[k].upper())
        else:
            story_ab_result[k] = "DRAW"
        
    return story_ab_result

def save_stat_result(out_data, logger, out_dir_stat, eval_data_path):
    eval_data_file_name = eval_data_path.split('/')[-1]
    save_file_name = eval_data_file_name.replace('eval', 'stat', 1)
    save_path = os.path.join(out_dir_stat, save_file_name)
    
    save_json(out_data, save_path)
    logger.debug(f'===Saved {save_path}===')

def stat_from_eval(gen_data, eval_data, logger, args):
    from score_evaluation import read_story_draft, read_story_reformat
    
    stat_result = {}
    stat_result['example_id'] = eval_data['example_id']
    
    #### Gen Stat ####
    ## Initial Setup Edit Cnt
    stat_result['initial_setup_edit_cnt'] = gen_data['initialization']['initial_setup_edit_cnt']
    ## Character Information
    character_agent_list = gen_data['initialization']['character_agent_list']
    stat_result['character_cnt'] = len(character_agent_list)
    stat_result['role_cnt'] = dict(Counter(char['role'] for char in character_agent_list))
    ## Story Stat for Draft Version (Length, Force Quit, Description Pass)
    story, structured_story = read_story_draft(gen_data, args)
    part_storytelling = 1
    description_pass_cnt = 0
    while structured_story.get(f'part_{part_storytelling}') is not None:
        stat_result[f'part_{part_storytelling}'] = {}
        if isinstance(structured_story[f'part_{part_storytelling}'], str):
            stat_result[f'part_{part_storytelling}']['force_quit'] = gen_data['narrative'][f'part_{part_storytelling}']['turn_-1']['force_quit']
            story_segment = structured_story[f'part_{part_storytelling}']
            stat_result[f'part_{part_storytelling}']['word_cnt'] = estimate_word_count(story_segment)
            stat_result[f'part_{part_storytelling}']['token_cnt'] = estimate_token_count(story_segment)
            stat_result[f'part_{part_storytelling}']['turn_cnt'] = estimate_turn_count(story_segment)
            stat_result[f'part_{part_storytelling}']['character_reaction_cnt'] = estimate_character_reaction_count(story_segment)
            turn_story_telling = 1
            while gen_data['narrative'][f'part_{part_storytelling}'].get(f'turn_{turn_story_telling}') is not None:
                if gen_data['narrative'][f'part_{part_storytelling}'][f'turn_{turn_story_telling}'].get('direct_response_pass') is not None:
                    description_pass_cnt += 1
                turn_story_telling += 1
        else:
            act_storytelling = 1
            while structured_story.get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
                story_segment = structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}']
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}'] = {}
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['force_quit'] = gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}']['turn_-1']['force_quit']
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['word_cnt'] = estimate_word_count(story_segment)
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['token_cnt'] = estimate_token_count(story_segment)
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['turn_cnt'] = estimate_turn_count(story_segment)
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['character_reaction_cnt'] = estimate_character_reaction_count(story_segment)
                turn_story_telling = 1
                while gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'].get(f'turn_{turn_story_telling}') is not None:
                    if gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][f'turn_{turn_story_telling}'].get('direct_response_pass') is not None:
                        description_pass_cnt += 1
                    turn_story_telling += 1
                act_storytelling += 1
            stat_result[f'part_{part_storytelling}']['word_cnt'] = sum(v['word_cnt'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
            stat_result[f'part_{part_storytelling}']['token_cnt'] = sum(v['token_cnt'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
            stat_result[f'part_{part_storytelling}']['turn_cnt'] = sum(v['turn_cnt'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
            stat_result[f'part_{part_storytelling}']['character_reaction_cnt'] = sum(v['character_reaction_cnt'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
        part_storytelling += 1
    if part_storytelling == 1:
        stat_result['force_quit'] = gen_data['narrative']['turn_-1']['force_quit']
        stat_result['word_cnt'] = estimate_word_count(story)
        stat_result['token_cnt'] = estimate_token_count(story)
        stat_result['turn_cnt'] = estimate_turn_count(story)
        stat_result['character_reaction_cnt'] = estimate_character_reaction_count(story)
        turn_story_telling = 1
        while gen_data['narrative'].get(f'turn_{turn_story_telling}') is not None:
            if gen_data['narrative'][f'turn_{turn_story_telling}'].get('direct_response_pass') is not None:
                description_pass_cnt += 1
            turn_story_telling += 1
    else:
        stat_result['word_cnt'] = sum(stat_result[f'part_{part+1}']['word_cnt'] for part in range(part_storytelling-1))
        stat_result['token_cnt'] = sum(stat_result[f'part_{part+1}']['token_cnt'] for part in range(part_storytelling-1))
        stat_result['turn_cnt'] = sum(stat_result[f'part_{part+1}']['turn_cnt'] for part in range(part_storytelling-1))
        stat_result['character_reaction_cnt'] = sum(stat_result[f'part_{part+1}']['character_reaction_cnt'] for part in range(part_storytelling-1))
    character_reaction_cnt = stat_result['character_reaction_cnt']
    stat_result['description_pass_cnt'] = description_pass_cnt
    if character_reaction_cnt <= 0:
        stat_result['description_percentage'] = 50
    else:
        stat_result['description_percentage'] = round((character_reaction_cnt - description_pass_cnt) / character_reaction_cnt * 100, 2)

    ## Story Stat for Edit Version (Length)
    format_key = 'story_progress_novel'
    story, structured_story = read_story_reformat(gen_data, format_key, args)
    story, structured_story = '', {}
    part_storytelling = 1
    while structured_story.get(f'part_{part_storytelling}') is not None:
        if isinstance(structured_story[f'part_{part_storytelling}'], str):
            story_segment = structured_story[f'part_{part_storytelling}']
            stat_result[f'part_{part_storytelling}']['word_cnt_edited_narrative'] = estimate_word_count(story_segment)
            stat_result[f'part_{part_storytelling}']['token_cnt_edited_narrative'] = estimate_token_count(story_segment)
        else:
            act_storytelling = 1
            while structured_story.get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
                story_segment = structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}']
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['word_cnt_edited_narrative'] = estimate_word_count(story_segment)
                stat_result[f'part_{part_storytelling}'][f'act_{act_storytelling}']['token_cnt_edited_narrative'] = estimate_token_count(story_segment)
                act_storytelling += 1
            stat_result[f'part_{part_storytelling}']['word_cnt_edited_narrative'] = sum(v['word_cnt_edited_narrative'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
            stat_result[f'part_{part_storytelling}']['token_cnt_edited_narrative'] = sum(v['token_cnt_edited_narrative'] for v in stat_result[f'part_{part_storytelling}'].values() if isinstance(v, dict))
        part_storytelling += 1
    if part_storytelling == 1:
        stat_result['word_cnt_edited_narrative'] = estimate_word_count(story)
        stat_result['token_cnt_edited_narrative'] = estimate_token_count(story)
    else:
        stat_result['word_cnt_edited_narrative'] = sum(stat_result[f'part_{part+1}']['word_cnt_edited_narrative'] for part in range(part_storytelling-1))
        stat_result['token_cnt_edited_narrative'] = sum(stat_result[f'part_{part+1}']['token_cnt_edited_narrative'] for part in range(part_storytelling-1))

        
    #### Eval Stat ####
    if eval_data.get('draft') is None and eval_data.get('edit') is None:
        version_key_list = ['no_version']
    else:
        version_key_list = ['draft', 'edit']
        
    for version_key in version_key_list:
        stat_result[version_key] = {}
        
        ## Plan Adherence
        if version_key == 'no_version':
           plan_adherence_data = eval_data.get('plan_adherence') 
        else:
           plan_adherence_data = eval_data.get(version_key, {}).get('plan_adherence')
           
        if plan_adherence_data is not None:
            for dimension_name, v in plan_adherence_data.items():
                achievement_list = []
                for k, evaluation_list in v.items():
                    for evaluation in evaluation_list:
                        achievement_list.append(evaluation["achievement"])
                
                stat_result[version_key]['plan_adherence'] = {
                    'achievement_list': achievement_list,
                    'score': round(sum([max(0, min(1, a)) for a in achievement_list]) / len(achievement_list) * 100, 2)
                }
        ## Plan Theory Adherence
        if version_key == 'no_version':
           plan_theory_adherence_data = eval_data.get('plan_theory_adherence') 
        else:
           plan_theory_adherence_data = eval_data.get(version_key, {}).get('plan_theory_adherence')
           
        if plan_theory_adherence_data is not None:
            for dimension_name, v in plan_theory_adherence_data.items():
                achievement_list = []
                for k, evaluation_list in v.items():
                    for evaluation in evaluation_list:
                        achievement_list.append(evaluation["achievement"])
                
                stat_result[version_key]['plan_theory_adherence'] = {
                    'achievement_list': achievement_list,
                    'score': round(sum([max(0, min(1, a)) for a in achievement_list]) / len(achievement_list) * 100, 2)
                }

        ## Story Quality (AB Test)
        if version_key == 'no_version':
           story_quality_ab_data = eval_data.get('story_quality_ab') 
        else:
           story_quality_ab_data = eval_data.get(version_key, {}).get('story_quality_ab')
        
        if story_quality_ab_data is not None:
            stat_result[version_key]['story_quality_ab'] = {}
            for k, v in story_quality_ab_data.items():
                stat_result[version_key]['story_quality_ab'][k] = {}
                v = append_story_ab_result(v['llm_response_ab'], v['llm_response_ba'], logger, is_vs_gold=('gold' in k))
                for category, story_quality_ab_result in v.items():
                    stat_result[version_key]['story_quality_ab'][k][category] = story_quality_ab_result
    
    return stat_result

def summarize_stat(stat_json_list, args):
    ## Gen Stat
    initial_setup_edit_cnt_agg = []
    character_cnt_agg = []
    role_cnt_agg = {'main': [], 'side': [], 'villain': []}
    story_length_agg = {'force_quit': [], 'word_cnt': [], 'token_cnt': [], 'turn_cnt': [], 'word_cnt_edited_narrative': [], 'token_cnt_edited_narrative': []}
    description_analysis_agg = {'character_reaction_cnt': [], 'description_pass_cnt': [], 'description_percentage': []}
    
    ## Eval Stat
    plan_adherence_agg = {}
    plan_theory_adherence_agg = {}
    plan_adherence_achievement_agg = {}
    plan_theory_adherence_achievement_agg = {}
    story_quality_ab_agg = {}
    
    if stat_json_list[0].get('draft') is None and stat_json_list[0].get('edit') is None:
        version_key_list = ['no_version']
    else:
        version_key_list = ['draft', 'edit']
    
    for version_key in version_key_list:
        plan_adherence_agg[version_key] = []
        plan_theory_adherence_agg[version_key] = []
        plan_adherence_achievement_agg[version_key] = {}
        plan_theory_adherence_achievement_agg[version_key] = {}
        story_quality_ab_agg[version_key] = {}
    
    ## Aggregate
    for stat_json in stat_json_list:
        character_cnt_agg.append(stat_json['character_cnt'])
        initial_setup_edit_cnt_agg.append(stat_json['initial_setup_edit_cnt'])
        if stat_json['role_cnt'].get('main') is not None:
            role_cnt_agg['main'].append(stat_json['role_cnt']['main'])
        if stat_json['role_cnt'].get('side') is not None:
            role_cnt_agg['side'].append(stat_json['role_cnt']['side'])
        if stat_json['role_cnt'].get('villain') is not None:
            role_cnt_agg['villain'].append(stat_json['role_cnt']['villain'])

        part_storytelling = 1
        while stat_json.get(f'part_{part_storytelling}') is not None:
            if story_length_agg.get(f'part_{part_storytelling}') is None:
                story_length_agg[f'part_{part_storytelling}'] = {'force_quit': [], 'word_cnt': [], 'token_cnt': [], 'turn_cnt': [], 'word_cnt_edited_narrative': [], 'token_cnt_edited_narrative': []}
            for key in ['word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
                if 'edited_narrative' in key:
                    continue
                story_length_agg[f'part_{part_storytelling}'][key].append(stat_json[f'part_{part_storytelling}'][key])
            act_storytelling = 1
            while stat_json.get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
                if story_length_agg.get(f'part_{part_storytelling}', {}).get('act') is None:
                    story_length_agg[f'part_{part_storytelling}']['act'] = {'force_quit': [], 'word_cnt': [], 'token_cnt': [], 'turn_cnt': [], 'word_cnt_edited_narrative': [], 'token_cnt_edited_narrative': []}
                for key in ['force_quit', 'word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
                    if 'edited_narrative' in key:
                        continue
                    story_length_agg[f'part_{part_storytelling}']['act'][key].append(stat_json[f'part_{part_storytelling}'][f'act_{act_storytelling}'][key])
                act_storytelling += 1
            if act_storytelling == 1:
                story_length_agg[f'part_{part_storytelling}']['force_quit'].append(stat_json[f'part_{part_storytelling}']['force_quit'])
            part_storytelling += 1
        if part_storytelling == 1:
            story_length_agg['force_quit'].append(stat_json['force_quit'])
        for key in ['word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
            if 'edited_narrative' in key:
                continue
            story_length_agg[key].append(stat_json[key])
        description_analysis_agg['character_reaction_cnt'].append(stat_json['character_reaction_cnt'])
        description_analysis_agg['description_pass_cnt'].append(stat_json['description_pass_cnt'])
        description_analysis_agg['description_percentage'].append(stat_json['description_percentage'])

        for version_key in version_key_list:
            
            if stat_json.get(version_key, {}).get('plan_adherence') is not None:
                plan_adherence_agg[version_key].append(stat_json[version_key]['plan_adherence']['score'])
                plan_adherence_achievement_list = stat_json[version_key]['plan_adherence']['achievement_list']
                for achievement in plan_adherence_achievement_list:
                    if 0 <= achievement <= 1:
                        key = f"{achievement:.1f}"
                        if key not in plan_adherence_achievement_agg[version_key]:
                            plan_adherence_achievement_agg[version_key][key] = 0
                        plan_adherence_achievement_agg[version_key][key] += 1
                
            if stat_json.get(version_key, {}).get('plan_theory_adherence') is not None:
                plan_theory_adherence_agg[version_key].append(stat_json[version_key]['plan_theory_adherence']['score'])
                plan_theory_adherence_achievement_list = stat_json[version_key]['plan_theory_adherence']['achievement_list']
                for achievement in plan_theory_adherence_achievement_list:
                    if 0 <= achievement <= 1:
                        key = f"{achievement:.1f}"
                        if key not in plan_theory_adherence_achievement_agg[version_key]:
                            plan_theory_adherence_achievement_agg[version_key][key] = 0
                        plan_theory_adherence_achievement_agg[version_key][key] += 1
                
            if stat_json.get(version_key, {}).get('story_quality_ab') is not None:
                if story_quality_ab_agg.get(version_key, {}).get('story_quality_ab') is None:
                    story_quality_ab_agg[version_key]['story_quality_ab'] = {}
                for k, v in stat_json[version_key]['story_quality_ab'].items():
                    if story_quality_ab_agg.get(version_key, {}).get('story_quality_ab', {}).get(k) is None:
                        story_quality_ab_agg[version_key]['story_quality_ab'][k] = {}
                    for category, story_quality_ab_result in v.items():
                        if story_quality_ab_agg.get(version_key, {}).get('story_quality_ab', {}).get(k, {}).get(category.lower().replace(" ", "_")) is None:
                            story_quality_ab_agg[version_key]['story_quality_ab'][k][category.lower().replace(" ", "_")] = []
                        story_quality_ab_agg[version_key]['story_quality_ab'][k][category].append(story_quality_ab_result)
    
    ## Stat
    agg_stat = {'example_id': 'agg'}
    
    agg_stat['character_cnt'] = {}
    agg_stat['character_cnt']['agg'] = character_cnt_agg
    agg_stat['character_cnt']['min'] = int(np.min(character_cnt_agg))
    agg_stat['character_cnt']['max'] = int(np.max(character_cnt_agg))
    agg_stat['character_cnt']['avg'] = float(np.mean(character_cnt_agg))
    agg_stat['character_cnt']['median'] = int(np.median(character_cnt_agg))
    
    if 'dramatron' not in args.data_file:
        agg_stat['initial_setup_edit_cnt'] = {}
        agg_stat['initial_setup_edit_cnt']['agg'] = initial_setup_edit_cnt_agg
        agg_stat['initial_setup_edit_cnt']['min'] = int(np.min(initial_setup_edit_cnt_agg))
        agg_stat['initial_setup_edit_cnt']['max'] = int(np.max(initial_setup_edit_cnt_agg))
        agg_stat['initial_setup_edit_cnt']['avg'] = float(np.mean(initial_setup_edit_cnt_agg))
        agg_stat['initial_setup_edit_cnt']['median'] = int(np.median(initial_setup_edit_cnt_agg))
    
        agg_stat['role_cnt'] = {}
        for k, v in role_cnt_agg.items():
            agg_stat['role_cnt'][k] = {}
            agg_stat['role_cnt'][k]['agg'] = role_cnt_agg[k]
            agg_stat['role_cnt'][k]['min'] = int(np.min(v))
            agg_stat['role_cnt'][k]['max'] = int(np.max(v))
            agg_stat['role_cnt'][k]['avg'] = float(np.mean(v))
            agg_stat['role_cnt'][k]['median'] = int(np.median(v))
    
    agg_stat['story_length'] = {}
    if 'dramatron' in args.data_file:
        for key in ['word_cnt', 'token_cnt', 'turn_cnt']:
            agg_stat['story_length'][key] = {}
            agg_stat['story_length'][key]['agg'] = story_length_agg[key]
            agg_stat['story_length'][key]['min'] = int(np.min(story_length_agg[key]))
            agg_stat['story_length'][key]['max'] = int(np.max(story_length_agg[key]))
            agg_stat['story_length'][key]['avg'] = int(np.mean(story_length_agg[key]))
    else:
        part_storytelling = 1
        while story_length_agg.get(f'part_{part_storytelling}') is not None:
            agg_stat['story_length'][f'part_{part_storytelling}'] = {}
            if story_length_agg.get(f'part_{part_storytelling}', {}).get('act') is not None:
                agg_stat['story_length'][f'part_{part_storytelling}']['act'] = {}
                agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit'] = {}
                agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['agg'] = story_length_agg[f'part_{part_storytelling}']['act']['force_quit']
                agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['true_cnt'] = sum(story_length_agg[f'part_{part_storytelling}']['act']['force_quit'])
                agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['false_cnt'] = len(story_length_agg[f'part_{part_storytelling}']['act']['force_quit']) - agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['true_cnt']
                agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['true_percentage'] = round(agg_stat['story_length'][f'part_{part_storytelling}']['act']['force_quit']['true_cnt'] / len(story_length_agg[f'part_{part_storytelling}']['act']['force_quit']), 2)
                for key in ['word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
                    agg_stat['story_length'][f'part_{part_storytelling}']['act'][key] = {}
                    agg_stat['story_length'][f'part_{part_storytelling}']['act'][key]['agg'] = story_length_agg[f'part_{part_storytelling}']['act'][key]
                    agg_stat['story_length'][f'part_{part_storytelling}']['act'][key]['min'] = int(np.min(story_length_agg[f'part_{part_storytelling}']['act'][key]))
                    agg_stat['story_length'][f'part_{part_storytelling}']['act'][key]['max'] = int(np.max(story_length_agg[f'part_{part_storytelling}']['act'][key]))
                    agg_stat['story_length'][f'part_{part_storytelling}']['act'][key]['avg'] = int(np.mean(story_length_agg[f'part_{part_storytelling}']['act'][key]))
            else:
                agg_stat['story_length'][f'part_{part_storytelling}']['force_quit'] = {}
                agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['agg'] = story_length_agg[f'part_{part_storytelling}']['force_quit']
                agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['true_cnt'] = sum(story_length_agg[f'part_{part_storytelling}']['force_quit'])
                agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['false_cnt'] = len(story_length_agg[f'part_{part_storytelling}']['force_quit']) - agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['true_cnt']
                agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['true_percentage'] = round(agg_stat['story_length'][f'part_{part_storytelling}']['force_quit']['true_cnt'] / len(story_length_agg[f'part_{part_storytelling}']['force_quit']), 2)
            
            for key in ['word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
                if 'edited_narrative' in key:
                    continue
                agg_stat['story_length'][f'part_{part_storytelling}'][key] = {}
                agg_stat['story_length'][f'part_{part_storytelling}'][key]['agg'] = story_length_agg[f'part_{part_storytelling}'][key]
                agg_stat['story_length'][f'part_{part_storytelling}'][key]['min'] = int(np.min(story_length_agg[f'part_{part_storytelling}'][key]))
                agg_stat['story_length'][f'part_{part_storytelling}'][key]['max'] = int(np.max(story_length_agg[f'part_{part_storytelling}'][key]))
                agg_stat['story_length'][f'part_{part_storytelling}'][key]['avg'] = int(np.mean(story_length_agg[f'part_{part_storytelling}'][key]))
            
            part_storytelling += 1

        if part_storytelling == 1:
            agg_stat['story_length']['force_quit'] = {}
            agg_stat['story_length']['force_quit']['agg'] = story_length_agg['force_quit']
            agg_stat['story_length']['force_quit']['true_cnt'] = sum(story_length_agg['force_quit'])
            agg_stat['story_length']['force_quit']['false_cnt'] = len(story_length_agg['force_quit']) - agg_stat['story_length']['force_quit']['true_cnt']
            agg_stat['story_length']['force_quit']['true_percentage'] = round(agg_stat['story_length']['force_quit']['true_cnt'] / len(story_length_agg['force_quit']), 2)
        
        for key in ['word_cnt', 'token_cnt', 'turn_cnt', 'word_cnt_edited_narrative', 'token_cnt_edited_narrative']:
            if 'edited_narrative' in key:
                continue
            agg_stat['story_length'][key] = {}
            agg_stat['story_length'][key]['agg'] = story_length_agg[key]
            agg_stat['story_length'][key]['min'] = int(np.min(story_length_agg[key]))
            agg_stat['story_length'][key]['max'] = int(np.max(story_length_agg[key]))
            agg_stat['story_length'][key]['avg'] = int(np.mean(story_length_agg[key]))
            
        agg_stat['description_analysis'] = {}
        for key in ['description_percentage', 'character_reaction_cnt', 'description_pass_cnt']:
            agg_stat['description_analysis'][key] = {}
            agg_stat['description_analysis'][key]['agg'] = description_analysis_agg[key]
            agg_stat['description_analysis'][key]['min'] = float(np.min(description_analysis_agg[key]))
            agg_stat['description_analysis'][key]['max'] = float(np.max(description_analysis_agg[key]))
            agg_stat['description_analysis'][key]['avg'] = float(np.mean(description_analysis_agg[key]))
    
    
    for version_key in version_key_list:
        agg_stat[version_key] = {}
        
        if plan_adherence_agg.get(version_key) != []:
            agg_stat[version_key]['plan_adherence'] = {}
            agg_stat[version_key]['plan_adherence']['agg'] = plan_adherence_agg[version_key]
            agg_stat[version_key]['plan_adherence']['min'] = float(np.min(plan_adherence_agg[version_key]))
            agg_stat[version_key]['plan_adherence']['max'] = float(np.max(plan_adherence_agg[version_key]))
            agg_stat[version_key]['plan_adherence']['avg'] = float(np.mean(plan_adherence_agg[version_key]))
            agg_stat[version_key]['plan_adherence']['median'] = float(np.median(plan_adherence_agg[version_key]))
            
        if plan_adherence_achievement_agg.get(version_key) != {}:
            agg_stat[version_key]['plan_adherence_count'] = dict(
                sorted(
                    plan_adherence_achievement_agg[version_key].items(),
                    key=lambda x: float(x[0])
                )
            )
            
        if plan_theory_adherence_agg.get(version_key) != []:
            agg_stat[version_key]['plan_theory_adherence'] = {}
            agg_stat[version_key]['plan_theory_adherence']['agg'] = plan_theory_adherence_agg[version_key]
            agg_stat[version_key]['plan_theory_adherence']['min'] = float(np.min(plan_theory_adherence_agg[version_key]))
            agg_stat[version_key]['plan_theory_adherence']['max'] = float(np.max(plan_theory_adherence_agg[version_key]))
            agg_stat[version_key]['plan_theory_adherence']['avg'] = float(np.mean(plan_theory_adherence_agg[version_key]))
            agg_stat[version_key]['plan_theory_adherence']['median'] = float(np.median(plan_theory_adherence_agg[version_key]))
            
        if plan_theory_adherence_achievement_agg.get(version_key) != {}:
            agg_stat[version_key]['plan_theory_adherence_count'] = dict(
                sorted(
                    plan_theory_adherence_achievement_agg[version_key].items(),
                    key=lambda x: float(x[0])
                )
            )
        
        if story_quality_ab_agg.get(version_key) != {}:
            agg_stat[version_key]['story_quality_ab'] = {}
            for k, v in story_quality_ab_agg[version_key]['story_quality_ab'].items():
                agg_stat[version_key]['story_quality_ab'][k] = {}
                for category, value_list in v.items():
                    agg_stat[version_key]['story_quality_ab'][k][category] = {}
                    story_ab_result_count = dict(Counter(value_list))
                    agg_stat[version_key]['story_quality_ab'][k][category]['count'] = story_ab_result_count
                    agg_stat[version_key]['story_quality_ab'][k][category]['win_ratio'] = round(story_ab_result_count['A'] / (story_ab_result_count['A'] + story_ab_result_count['B']) * 100, 2)
            
    stat_json_list.insert(0, agg_stat)
                
    return stat_json_list
                
def main():
    
    #### setup logger ####
    log_file_path = os.path.join(os.environ['LOG_DIR'], 'stat.log')
    logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)
    
    #### args ####
    args = parse_args()
    log_stat_setting(logger=logger, args=args)
    
    #### load ####
    generated_json_list = read_json(args.data_file)
    evaluated_json_list = read_json(args.eval_data_file)
    
    #### stat ####
    stat_json_list = []
    for target_eval_json in tqdm(evaluated_json_list):
        target_example_id = target_eval_json['example_id']
        
        target_gen_json = None
        for gen_json in generated_json_list:
            if gen_json['example_id'] == target_example_id:
                target_gen_json = gen_json
                
        if target_gen_json is None:
            logger.error(f"{target_example_id} data not found in the gen data")
            raise Exception(f"{target_example_id} data not found in the gen data")
        
        stat_json_list.append(stat_from_eval(target_gen_json, target_eval_json, logger, args))
    
    stat_json_list = summarize_stat(stat_json_list, args)
    
    save_stat_result(stat_json_list, logger, args.out_dir, args.eval_data_file)
    
if __name__ == "__main__":
    main()