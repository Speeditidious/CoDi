import sys
sys.path.insert(0, '.')
import logging
import argparse
import os
import re
from tqdm import tqdm

from global_utils import *
from character_agent_utils import hide_thought_of_others, extract_character_utility
from generation_utils import character_profiles_to_prompt
from prompts.evaluation_prompt import *

EVALUATOR_TEMP = 0.4

def parse_args():
    parser = argparse.ArgumentParser()
    ## Path to data to evaluate
    parser.add_argument('--data-file', type=str, required=True)
    ## Path to evaluation data to load
    parser.add_argument('--load-file', type=str, default='None')
    ## Directory of save evaluation result
    parser.add_argument('--out-dir', type=str, required=True)
    parser.add_argument('--out-dir-stat', type=str, required=True)
    ## B data for AB Test
    parser.add_argument('--data-file-b', type=str, default='None')
    ## Version of edition to evaluate (false(default): evaluate edit version)
    parser.add_argument('--evaluate-draft', action='store_true')
    ## What to evaluate
    parser.add_argument('--evaluate-plan', action='store_true')
    parser.add_argument('--evaluate-plan-theory', action='store_true')
    parser.add_argument('--evaluate-story-quality-ab', action='store_true')
    ## Base models of agents
    parser.add_argument('--evaluator-agent-base-model', type=str, default='None')
    
    args = parser.parse_args()
    
    return args

def log_evaluation_setting(logger, args):
    if args.evaluator_agent_base_model == 'None':
        raise Exception('Evaluator agent base model is not provided.')
    if args.evaluate_story_quality_ab:
        if args.data_file_b == 'None':
            raise Exception('AB Test mode On. However, B data is not provided.')
    
    logger.info('===Evaluation Settings===')
    logger.info(f'Data File: {args.data_file}')
    logger.info(f'Data File B: {args.data_file_b}')
    logger.info(f'Loaded Evaluation File: {args.load_file}')
    logger.info(f'Out Directory: {args.out_dir}')
    logger.info(f'Out Directory (Stat): {args.out_dir_stat}')
    if args.evaluate_draft:
        logger.info(f'Evaluation Target: Draft Version')
    else:
        logger.info(f'Evaluation Target: Edit Version')
    what_to_evaluate_list = []
    if args.evaluate_plan:
        what_to_evaluate_list.append('Plan')
    if args.evaluate_plan_theory:
        what_to_evaluate_list.append('Plan Theory')
    if args.evaluate_story_quality_ab:
        what_to_evaluate_list.append('Story Quality AB Test')
    what_to_evaluate = ', '.join(what_to_evaluate_list)
    logger.info(f'What to Evaluate: {what_to_evaluate}')
    logger.info(f'Evaluator agent base model: {args.evaluator_agent_base_model}')

def save_evaluation_result(in_data, out_dataset, logger, args):
    if any(out_data['example_id'] == in_data['example_id'] for out_data in out_dataset):
        
        for i, out_data in enumerate(out_dataset):
            if out_data['example_id'] == in_data['example_id']:
                out_dataset[i] = in_data
                break
    else:
        
        out_dataset.append(in_data)
    
    gen_data_file_name = args.data_file.split('/')[-1]
    save_file_name = gen_data_file_name.replace('gen', 'eval', 1)
    save_path = os.path.join(args.out_dir, save_file_name)
    
    save_json(out_dataset, save_path)
    logger.debug(f'===Saved {save_path}===')
    
    return save_path

def preprocess_story_segment(story_segment, hide_thoughts, target_character):
    ignore_keywords = ['###', 'END']
    
    if hide_thoughts or target_character != None:
        story_segment = hide_thought_of_others(story_segment, target_character)
    story_segment = '\n'.join([s.strip() for s in story_segment.splitlines() if all(k not in s for k in ignore_keywords)])

    return story_segment

def read_story_draft(target_data, args, hide_thoughts=False, target_character=None):
    story = ''
    structured_story = {}
    
    if 'plan' and 'actseq' in args.data_file:
        part_storytelling = 1
        while target_data.get('narrative', {}).get(f'part_{part_storytelling}') is not None:
            act_storytelling = 1
            structured_story[f'part_{part_storytelling}'] = {}
            while target_data.get('narrative', {}).get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
                turn_storytelling = 1
                structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'] = ''
                while target_data.get('narrative', {}).get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                    story_segment = target_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                    story_segment = preprocess_story_segment(story_segment, hide_thoughts, target_character)
                    story += story_segment + '\n'
                    structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'] += story_segment + '\n'
                    
                    turn_storytelling += 1
                structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'] = structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'].strip()
                act_storytelling += 1
            part_storytelling += 1
    elif 'plan' in args.data_file:
        part_storytelling = 1
        while target_data.get('narrative', {}).get(f'part_{part_storytelling}') is not None:
            turn_storytelling = 1
            structured_story[f'part_{part_storytelling}'] = ''
            while target_data.get('narrative', {}).get(f'part_{part_storytelling}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                story_segment = target_data['narrative'][f'part_{part_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                story_segment = preprocess_story_segment(story_segment, hide_thoughts, target_character)
                story += story_segment + '\n'
                structured_story[f'part_{part_storytelling}'] += story_segment + '\n'
                
                turn_storytelling += 1
            structured_story[f'part_{part_storytelling}'] = structured_story[f'part_{part_storytelling}'].strip()
            part_storytelling += 1
    elif 'actseq' in args.data_file:
        raise NotImplementedError
    else:
        turn_storytelling = 1
        while target_data.get('narrative', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
            story_segment = target_data['narrative'][f'turn_{turn_storytelling}']['story_progress']
            story_segment = preprocess_story_segment(story_segment, hide_thoughts, target_character)
            story += story_segment + '\n'
            
            turn_storytelling += 1
            
    return story.strip(), structured_story

def read_story_edit(target_data, format_key, args):
    story = ''
    structured_story = {}
    
    part_storytelling = 1
    while target_data.get('edited_narrative', {}).get(f'part_{part_storytelling}') is not None:
        act_storytelling = 1
        structured_story[f'part_{part_storytelling}'] = {}
        while target_data.get('edited_narrative', {}).get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
            structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'] = ''
            act_story = target_data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][format_key]
            if act_story != '':
                story += act_story + '\n\n'
                structured_story[f'part_{part_storytelling}'][f'act_{act_storytelling}'] = act_story
            
            act_storytelling += 1
            
        if act_storytelling == 1:
            part_story = target_data['edited_narrative'][f'part_{part_storytelling}'][format_key]
            story += part_story + '\n\n'
            structured_story[f'part_{part_storytelling}'] = part_story
            
        part_storytelling += 1
        
    if part_storytelling == 1:
        story = target_data['edited_narrative'][format_key]
            
    return story.strip(), structured_story

def read_story_hollmwood(target_data):
    story = ''
    for tag, act_history in target_data['narrative'].items():
        cleaned_act_history = re.sub(r'</?[^>]+>', '', act_history)
        story += cleaned_act_history + '\n'
    
    story = re.sub(r'\n+', '\n\n', story)
    return story.strip()

def read_story(target_data, args, hide_thoughts=False, target_character=None, story_b_mode=False, format_key='story_progress_screenplay'):
    """ Read story for evaluation.
    Ours: Hide **thought** of characters if necessary.
    Returns
    ----------
    story : str
        preprocessed narrative
    structured_story : dict
        preprocessed narrative is divided into parts or acts.
    """
    ## HoLLMwood
    if 'hollmwood' in args.data_file or (story_b_mode and 'hollmwood' in args.data_file_b):
        return read_story_hollmwood(target_data), {}
    
    ## Ours
    ## Read Draft Version
    if args.evaluate_draft:
        return read_story_draft(target_data, args, hide_thoughts, target_character)
    ## Read Edit Version
    else:
        return read_story_edit(target_data, format_key, args)
    

def read_plan(target_data, args):
    
    narrative_utility_list = []
    if 'plan' and 'actseq' in args.data_file:
        plan_json = target_data['initialization']['plan']
        part = 1
        while plan_json.get(f'part_{part}_act_seq') is not None:
            for act in plan_json[f'part_{part}_act_seq']:
                act_plan = [v for v in act.values()][0]
                narrative_utility_list.append('.'.join([line for line in act_plan.split('.') if 'Constraints' not in line]))
            part += 1
    elif 'plan' in args.data_file:
        plan_json = target_data['initialization']['plan']
        part = 1
        while plan_json.get(f'part_{part}') is not None:
            narrative_utility_list.extend([line.strip() for line in plan_json[f'part_{part}'].split('\n') if 'utility(narrative)' not in line])
            part += 1
    elif 'actseq' in args.data_file:
        raise NotImplementedError
    else:
        narrative_utility_text = extract_character_utility(target_data['initialization']['initial_setup'], character='narrative')
        narrative_utility_list.extend([line.strip() for line in narrative_utility_text.split('\n') if 'utility(narrative)' not in line])
        
    return '\n'.join(narrative_utility_list)

def extract_final_score(llm_response):
    llm_response = llm_response.replace('*', '')
    pattern = r"(?:#+\s*)?\s*\**\s*Final Score\s*\**\s*:?\s*\**[\s\n]*\**\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*\**"
    match = re.search(pattern, llm_response, re.IGNORECASE | re.DOTALL)
    if match:
        return float(match.group(1)), float(match.group(2))
    else:
        return None, None
    
def validate_plan_adherence_response(llm_response):
    try:
        if not isinstance(llm_response, dict):
            return False
        
        for k, v in llm_response.items():
            if not isinstance(v, dict) or 'evaluations' not in v:
                return False
            
            if not isinstance(v['evaluations'], list):
                return False

            for f in v['evaluations']:
                if not isinstance(f, dict):
                    return False
                
                if f.get('achievement', None) is None:
                    f['achievement'] = 1

        return llm_response
    except:
        return False

def evaluate_plan_adherence(target_data, logger, args):
    RETRY_N_MAX = 3
    
    final_result = {}
    
    plan = read_plan(target_data, args)
    story, _ = read_story(target_data, args)
    
    retry_n = 0
    while retry_n < RETRY_N_MAX:
        evaluate_plan_adherence_prompt = build_plan_adherence_prompt(story, plan)
        llm_response = run_llm(user_prompt=evaluate_plan_adherence_prompt, model=args.evaluator_agent_base_model, temperature=max(0, EVALUATOR_TEMP - retry_n*0.1))
        logger.debug(f"===Plan Adherence Response==={llm_response}")
        
        try:
            llm_response = validate_plan_adherence_response(llm_response)
            if llm_response == False:
                retry_n += 1
            else:
                for key in llm_response:
                    final_result[key] = llm_response[key]
                break
        except:
            retry_n += 1
            
        logger.debug(f"Unexpected response format while evaluating Plan Adherence")
        logger.debug(f"Retrying... Count:{retry_n}")
    
    return final_result


def evaluate_plan_theory_adherence(target_data, logger, args):
    RETRY_N_MAX = 3
    
    final_result = {}
    
    from prompts.planner_agent_prompt import PART1_DESCRIPTION, PART2_DESCRIPTION, PART3_DESCRIPTION, PART4_DESCRIPTION
    
    plan_theory_text = PART1_DESCRIPTION + '\n\n' + PART2_DESCRIPTION + '\n\n' + PART3_DESCRIPTION + '\n\n' + PART4_DESCRIPTION
    story, _ = read_story(target_data, args)
    
    retry_n = 0
    while retry_n < RETRY_N_MAX:
        evaluate_plan_theory_adherence_prompt = build_plan_theory_adherence_prompt(story, plan_theory_text)
        llm_response = run_llm(user_prompt=evaluate_plan_theory_adherence_prompt, model=args.evaluator_agent_base_model, temperature=max(0, EVALUATOR_TEMP - retry_n*0.1))
        logger.debug(f"===Plan Theory Adherence Response==={llm_response}")
        
        try:
            llm_response = validate_plan_adherence_response(llm_response)
            if llm_response == False:
                retry_n += 1
            else:
                for key in llm_response:
                    final_result[key] = llm_response[key]
                break
        except:
            retry_n += 1
            
        logger.debug(f"Unexpected response format while evaluating Plan Adherence")
        logger.debug(f"Retrying... Count:{retry_n}")
    
    return final_result


def evaluate_story_ab(target_data_a, target_data_b, logger, args):
    
    format_key = 'story_progress_screenplay'
    if target_data_b.get('targets') is not None:
        format_key = 'story_progress_novel'

    story_a, _ = read_story(target_data_a, args, format_key=format_key)
    
    if target_data_b.get('targets') is not None:
        story_b = target_data_b['targets'].strip()
    else:
        story_b, _ = read_story(target_data_b, args, story_b_mode=True, format_key=format_key)
        
    character_agent_list = target_data_a['initialization']['character_agent_list']
    character_profiles_text = character_profiles_to_prompt(character_agent_list)
    
    if target_data_b.get('targets') is not None:
        prompt_ab = EVALUATE_STORY_AB_PROMPT_VS_GOLD.format(story_a=story_a, story_b=story_b)
    else:
        prompt_ab = EVALUATE_STORY_AB_PROMPT.format(character_profiles=character_profiles_text, story_a=story_a, story_b=story_b)
    llm_response_ab = run_llm(user_prompt=prompt_ab, model=args.evaluator_agent_base_model, temperature=EVALUATOR_TEMP)
    logger.debug(f"===Story AB Test Response==={llm_response_ab}")
    
    if target_data_b.get('targets') is not None:
        prompt_ba = EVALUATE_STORY_AB_PROMPT_VS_GOLD.format(story_a=story_b, story_b=story_a)
    else:
        prompt_ba = EVALUATE_STORY_AB_PROMPT.format(character_profiles=character_profiles_text, story_a=story_b, story_b=story_a)
    llm_response_ba = run_llm(user_prompt=prompt_ba, model=args.evaluator_agent_base_model, temperature=EVALUATOR_TEMP)
    logger.debug(f"===Story BA Test Response==={llm_response_ba}")
    
    final_result = {}
    
    final_result['llm_response_ab'] = llm_response_ab
    final_result['llm_response_ba'] = llm_response_ba
    
    return final_result
    
def main():
    
    #### setup logger ####
    log_file_path = os.path.join(os.environ['LOG_DIR'], 'evaluation.log')
    logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)
    
    #### args ####
    args = parse_args()
    log_evaluation_setting(logger=logger, args=args)
    
    #### load ####
    target_data_list = read_json(args.data_file)
    
    loaded_eval_list = []
    if args.load_file != 'None':
        loaded_eval_list = read_json(args.load_file)
    else:
        try:
            temp_load_file_name = args.data_file.replace('generation', 'evaluation').replce('gen_', 'eval_')
            loaded_eval_list = read_json(temp_load_file_name)
        except:
            logger.info('Could not find any files to load. Evaluate without Load File.')
    
    #### evaluate ####
    out_eval_json_list = []
    for target_data in target_data_list:
        example_id = target_data['example_id']
        loaded_data = {}
        for loaded_eval in loaded_eval_list:
            if loaded_eval['example_id'] == example_id:
                out_eval_json_list.append(loaded_eval)
                break
    
    for target_data in tqdm(target_data_list):
        example_id = target_data['example_id']
        if args.evaluate_draft:
            version_key = 'draft'
        else:
            version_key = 'edit'
        
        ## Load
        eval_json = {}
        for out_eval_json in out_eval_json_list:
            if out_eval_json['example_id'] == example_id:
                eval_json = out_eval_json
                break
        
        ## Load data not exist. Create new one.
        if eval_json == {}:
            eval_json = {'example_id': example_id}
            eval_json[version_key] = {}
        
        ## Load data exists. But the edit version does not exist.
        if eval_json.get(version_key) is None:
            eval_json[version_key] = {}
            
        def evaluate_metrics(metric_key, evaluate_func, reevaluate=False):
            logger.debug(f"==={eval_json['example_id']}... {metric_key}===")

            if loaded_data.get(version_key, {}).get(metric_key) is None or reevaluate:
                eval_json[version_key][metric_key] = evaluate_func(target_data, logger, args)
                    
            return save_evaluation_result(eval_json, out_eval_json_list, logger, args)
        
        if args.evaluate_plan:
            
            _ = evaluate_metrics('plan_adherence', evaluate_plan_adherence)
            
        if args.evaluate_plan_theory:
            
            _ = evaluate_metrics('plan_theory_adherence', evaluate_plan_theory_adherence)
            
        if args.evaluate_story_quality_ab:
            
            if 'gen' in args.data_file_b:
                target_data_b_list = read_json(args.data_file_b)
                generation_mode = 'gen'
                if 'hollmwood' in args.data_file_b:
                    generation_mode += '_hollmwood'
                else:
                    if 'nointervention' in args.data_file_b:
                        generation_mode += '_nointervention'
                    if 'nodescription' in args.data_file_b:
                        generation_mode += '_nodescription'
                    if 'plan' in args.data_file_b:
                        generation_mode += '_plan'
                    if 'actseq' in args.data_file_b:
                        generation_mode += '_actseq'
            else:
                target_data_b_list = read_jsonl(args.data_file_b)
                generation_mode = 'gold'
                
            target_data_b = None
            for target_data_b_candidate in target_data_b_list:
                if target_data_b_candidate['example_id'] == example_id:
                    target_data_b = target_data_b_candidate
                    break

            if loaded_data.get(version_key, {}).get('story_quality_ab', {}).get(f'vs_{generation_mode}') is None or 'gold' in generation_mode:
                logger.debug(f"==={eval_json['example_id']}... Evaluating Story Quality AB Test... B: {generation_mode}===")
                if eval_json.get(version_key, {}).get('story_quality_ab') is None:
                    eval_json[version_key]['story_quality_ab'] = {}
                eval_json[version_key]['story_quality_ab'][f'vs_{generation_mode}'] = evaluate_story_ab(target_data, target_data_b, logger, args)
            
            _ = save_evaluation_result(eval_json, out_eval_json_list, logger, args)
        
        _ = save_evaluation_result(eval_json, out_eval_json_list, logger, args)
        
    eval_save_path = save_evaluation_result(eval_json, out_eval_json_list, logger, args)
    
    #### stat ####
    from score_stat import stat_from_eval, save_stat_result, summarize_stat
    generated_json_list = read_json(args.data_file)
    evaluated_json_list = read_json(eval_save_path)
    
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
    
    save_stat_result(stat_json_list, logger, out_dir_stat=args.out_dir_stat, eval_data_path=eval_save_path)
    
if __name__ == "__main__":
    main()