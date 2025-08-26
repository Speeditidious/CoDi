import copy

from global_utils import *
from planner_agent_utils import *
from character_agent_utils import *
from prompts.planner_agent_prompt import *


#################################
####                         ####
####  Utils for saving data  ####
####                         ####
#################################

def out_file_name(args):
    
    out_file_name = "gen"
    
    if args.no_intervention:
        out_file_name += '_nointervention'
        
    if args.no_description:
        out_file_name += '_nodescription'
    
    if args.plan_mode:
        out_file_name += '_plan'
    
    if args.act_seq_mode:
        out_file_name += '_actseq'
    
    if args.plan_mode or args.act_seq_mode:
        out_file_name += f'_p_{args.planner_agent_base_model}'

    out_file_name += f'_d_{args.director_agent_base_model}_c_{args.character_agent_base_model}'
    
    out_file_name += '.json'
    
    return out_file_name


def save_wip_data(wip_data, out_dataset, logger, args):
    
    if any(out_data['example_id'] == wip_data['example_id'] for out_data in out_dataset):
        
        for i, out_data in enumerate(out_dataset):
            if wip_data['example_id'] == out_data['example_id']:
                out_dataset[i] = wip_data
                break
        
    else:
        
        out_dataset.append(wip_data)
    
    save_path = os.path.join(args.out_dir, out_file_name(args))
    
    save_json(out_dataset, save_path)
    logger.debug(f'===Saved {save_path}===')

def preprocess_story_segment(story_segment, hide_thoughts, target_character):
    ignore_keywords = ['###', 'END']
    
    if hide_thoughts or target_character != None:
        story_segment = hide_thought_of_others(story_segment, target_character)
    story_segment = '\n'.join([s.strip() for s in story_segment.splitlines() if all(k not in s for k in ignore_keywords)])

    return story_segment

def out_file_name_story(data, args):
    
    out_file_name = data['example_id']
    
    if args.no_intervention:
        out_file_name += '_nointervention'
        
    if args.no_description:
        out_file_name += '_nodescription'
    
    if args.plan_mode:
        out_file_name += '_plan'
    
    if args.act_seq_mode:
        out_file_name += '_actseq'
    
    if args.plan_mode or args.act_seq_mode:
        out_file_name += f'_p_{args.planner_agent_base_model}'

    out_file_name += f'_d_{args.director_agent_base_model}_c_{args.character_agent_base_model}'
    
    if args.reformat_novel:
        out_file_name += '_novel'
    else:
        out_file_name += '_screenplay'
    
    out_file_name += '.txt'
    
    return out_file_name

def output_story(data, args):
    if args.reformat_novel:
        format_key = 'story_progress_novel'
    else:
        format_key = 'story_progress_screenplay'
        
    story = ''
    
    part_storytelling = 1
    while data.get('edited_narrative', {}).get(f'part_{part_storytelling}') is not None:
        act_storytelling = 1
        while data.get('edited_narrative', {}).get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
            act_story = data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][format_key]
            if act_story != '':
                story += act_story + '\n\n'
            
            act_storytelling += 1
            
        if act_storytelling == 1:
            part_story = data['edited_narrative'][f'part_{part_storytelling}'][format_key]
            story += part_story + '\n\n'
            
        part_storytelling += 1
        
    if part_storytelling == 1:
        story = data['edited_narrative'][format_key]
        
    save_path = os.path.join(args.out_dir, out_file_name_story(data, args))
    
    save_txt(story.strip(), save_path)
    logger.debug(f'===Saved {save_path}===')

################################
####                        ####
####  Utils for preprocess  ####
####                        ####
################################

def character_summarized_profiles_to_prompt(character_agent_list):
    '''
    Transform Characters' Summarized Profiles for prompting
    '''
    character_profiles_text = ''
    for character_agent in character_agent_list:
        name = character_agent['name']
        role = character_agent['role']
        summarized_profile = character_agent['summarized_profile']
        character_profiles_text += f"### {name}'s Profile (role: {role})\n" + summarized_profile + '\n'
    
    return character_profiles_text.strip()

def preprocess_setup(setup):
    """ Preprocess Setup to generate narrative
    1. Remove unncessary texts like '## Setup'.
    2. Add some necessary comments.
    3. Remove annotations for character entities.
    4. Remove multiple line breaks
    Parameters
    ----------
    setup : str
        setup text
    """
    
    ## Remove lines with '##' and 'Setup'
    setup_lines = setup.splitlines()
    cleaned_setup_lines = [line for line in setup_lines if not ('##' in line and 'Setup' in line)]
    
    ## Add comment for Utility
    cleaned_setup_lines_with_comments = []
    for line in cleaned_setup_lines:
        cleaned_setup_lines_with_comments.append(line)
        if "/* Utilities */" in line:
            cleaned_setup_lines_with_comments.append("utility(character) represents the character's goals and desires.")
            
    ## Replace annotations for character entities to summarized profile.
    cleaned_setup_lines_without_character_entity_annotation = []
    for line in cleaned_setup_lines_with_comments:
        cleaned_line = line
        if 'entity' in line and (': character' in line or ':character' in line):
            cleaned_line = re.sub(r'//.*', '', line).strip()
        cleaned_setup_lines_without_character_entity_annotation.append(cleaned_line)
    
    cleaned_setup = '\n'.join(cleaned_setup_lines_without_character_entity_annotation)
    
    ## 3 or more line breaks -> \n\n
    cleaned_setup = re.sub(r'(\n\s*){3,}', '\n\n', cleaned_setup)
    
    return cleaned_setup

def add_summarized_profiles(setup, character_agent_list):
    """ Add summarized profiles per each character entity.
    Parameters
    ----------
    setup : str
        setup text
    """
    character_summarized_profiles_text = character_summarized_profiles_to_prompt(character_agent_list)
    cleaned_setup = re.sub(r'(/\* Utilities \*/)', f'/* Character Profiles */\n{character_summarized_profiles_text}\n\n\\1', setup)
    
    cleaned_setup = re.sub(r'(\n\s*){3,}', '\n\n', cleaned_setup)
    
    return cleaned_setup

def preprocess_story_progress_list(story_progress_list):
    """ Preprocess story_progress_list to Story Progress text for prompting
    Parameters
    ----------
    story_progress_list : list
        list of Story Progress segments
    """
    
    if story_progress_list == []:
        return "This is the start of the story."
    
    last_story_progress_phrase = "### Latest Story Progress"
    story_progress_list_copy = story_progress_list.copy()
    if '### PART' in story_progress_list_copy[-1] and 'PART 1' not in story_progress_list_copy[-1]:
        story_progress_list_copy.insert(-2, last_story_progress_phrase)
    else:
        story_progress_list_copy.insert(-1, last_story_progress_phrase)
    
    return '\n'.join(story_progress_list_copy)


def preprocess_beginning_story(response):
    """ Preprocess LLM response of beginning generation to record it to story progress
    Parameters
    ----------
    response : str
        LLM response
    """
    ignore_keywords = ['##', 'Initial State', 'Current Act', 'Narrative Goal', 'Setting the Scene']
    return '\n'.join([paragraph.strip() for paragraph in response.splitlines() if all(k not in paragraph for k in ignore_keywords)])


def preprocess_negotiation_chat(negotiation_chat, character_name, character_location):
    """ Preprocess a message in the negotation table to record it in negotation table chat log.
    return {character}: {negotiation_chat}
    Parameters
    ----------
    negotiation_chat : str
            director agent's instruction or character agent's opinion
    character_name : str
            speaker's name of the given negotitation_chat (**Director** if he/she is a director agent)
    character_location : str
            speaker's location of the given negotitation_chat (None if he/she is a director agent)
    """

    if character_location == None:
        prefix = f"{character_name}:"
    else:
        prefix = f"{character_name} (at {character_location}):"
        
    if negotiation_chat.strip().startswith(prefix):
        negotiation_chat = negotiation_chat.strip()[len(prefix):].lstrip()
    
    negotiation_chat = re.sub(r'\s*\n\s*', ' ', negotiation_chat).strip()
    
    return prefix + ' ' + negotiation_chat


########################################
####                                ####
####  Utils for generation setting  ####
####                                ####
########################################

def unify_narrative_start(data, setting_data, args):
    setting_turn_1 = (
        setting_data.get('narrative', {}).get('turn_1') or
        setting_data.get('narrative', {}).get('part_1', {}).get('turn_1') or
        setting_data.get('narrative', {}).get('part_1', {}).get('act_1', {}).get('turn_1')
    )
    if setting_turn_1 is not None:
        if args.plan_mode and args.act_seq_mode:
            if data.get('narrative', {}).get('part_1', {}).get('act_1') is None:
                data['narrative']['part_1'] = {}
                data['narrative']['part_1']['act_1'] = {}
            data['narrative']['part_1']['act_1']['turn_1'] = copy.deepcopy(setting_turn_1)
        elif args.plan_mode:
            if data.get('narrative', {}).get('part_1') is None:
                data['narrative']['part_1'] = {}
            data['narrative']['part_1']['turn_1'] = copy.deepcopy(setting_turn_1)
        elif args.act_seq_mode:
            if data.get('narrative', {}).get('act_1') is None:
                data['narrative']['act_1'] = {}
            data['narrative']['act_1']['turn_1'] = copy.deepcopy(setting_turn_1)
        else:
            data['narrative']['turn_1'] = copy.deepcopy(setting_turn_1)
    
    return data


def init_narrative_generation(data, setting_data, args):
    if data.get('narrative') is None:
        data['narrative'] = {}
    
    ## Use setting_data's first turn for reducing experimental variance
    data = unify_narrative_start(data, setting_data, args)
    
    return data


def build_context_start_of_new_part(data, part, args):
    story_progress_list = []
    
    for part_n in range(part-2):
        story_progress_list.append(f'### PART {part_n+1} summary')
        story_progress_list.append(data['narrative'][f'part_{part_n+1}']['turn_-1']['part_summary'])
        
    if part >= 2:
        story_progress_list.append(f'### PART {part-1}')
    
        if args.act_seq_mode:
            act_storytelling = 1
            while data.get('narrative', {}).get(f'part_{part-1}', {}).get(f'act_{act_storytelling}') is not None:
                turn_storytelling = 1
                while data.get('narrative', {}).get(f'part_{part-1}', {}).get(f'act_{act_storytelling}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                    story_progress_segment = data['narrative'][f'part_{part-1}'][f'act_{act_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                    if 'ACT ENDS' not in story_progress_segment:
                        story_progress_list.append(story_progress_segment)
                    turn_storytelling += 1
                act_storytelling += 1
        else:
            turn_storytelling = 1
            while data.get('narrative', {}).get(f'part_{part-1}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                story_progress_list.append(data['narrative'][f'part_{part-1}'][f'turn_{turn_storytelling}']['story_progress'])
                turn_storytelling += 1
                
    story_progress_list.append(f'### PART {part}')
    
    return story_progress_list


#####################################
####                             ####
####  Utils for condition check  ####
####                             ####
#####################################

def count_turn_current_segment(data, args):
    turn_cnt = 0
    if args.act_seq_mode:
        current_part_n = 1
        while data.get('narrative', {}).get(f'part_{current_part_n}') is not None:
            current_part_n += 1
        current_part_n -= 1
        
        current_act_n = 1
        while data.get('narrative', {}).get(f'part_{current_part_n}').get(f'act_{current_act_n}') is not None:
            current_act_n += 1
        current_act_n -= 1
        
        turn_storytelling = 1
        while data.get('narrative', {}).get(f'part_{current_part_n}', {}).get(f'act_{current_act_n}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
            if turn_storytelling == 1:
                turn_cnt += 1
            else:
                turn_cnt += len([l for l in data['narrative'][f'part_{current_part_n}'][f'act_{current_act_n}'][f'turn_{turn_storytelling}']['story_progress'].splitlines() if l != ''])
            turn_storytelling += 1
        
    elif args.plan_mode:
        current_part_n = 1
        while data.get('narrative', {}).get(f'part_{current_part_n}') is not None:
            current_part_n += 1
        current_part_n -= 1
        
        turn_storytelling = 1
        while data.get('narrative', {}).get(f'part_{current_part_n}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
            if turn_storytelling == 1:
                turn_cnt += 1
            else:
                turn_cnt += len([l for l in data['narrative'][f'part_{current_part_n}'][f'turn_{turn_storytelling}']['story_progress'].splitlines() if l != ''])
            turn_storytelling += 1
        
    else:
        turn_storytelling = 1
        while data.get('narrative', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
            if turn_storytelling == 1:
                turn_cnt += 1
            else:
                turn_cnt += len([l for l in data['narrative'][f'turn_{turn_storytelling}']['story_progress'].splitlines() if l != ''])
            turn_storytelling += 1
            
    return turn_cnt


def is_character_reaction(story_progress_list):
    """ Checks if the Latest Story Progress follows the 'Character (at Location): Content' format.
    Parameters
    ----------
    story_progress_list : list
        list of Story Progress segments
    """
    if story_progress_list == []:
        return False

    return bool(re.match(r"^[^:]+(?: \([^)]+\))?: .+", story_progress_list[-1]))