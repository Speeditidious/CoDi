import sys
sys.path.insert(0, '.')
import logging
import os
from global_utils import *
from character_agent_utils import *
from prompts.planner_agent_prompt import *

#### setup logger ####
log_file_path = os.path.join(os.environ['LOG_DIR'], 'planner_agent_utils.log')
logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)


####################################
####                            ####
####  Utils for initialization  ####
####                            ####
####################################

def preprocess_initial_setup(initial_setup):
    
    TYPE_FORMAT = '/* Types */'
    ENTITIES_FORMAT = '/* Entities */'
    INITIAL_STATE_FORMAT = '/* Initial State */'
    UTILITY_FORMAT = '/* Utilities */'
    
    format_map = {
        'Types': TYPE_FORMAT,
        'Entities': ENTITIES_FORMAT,
        'Initial State': INITIAL_STATE_FORMAT,
        'Utilities': UTILITY_FORMAT
    }
    
    preprocessed_initial_setup_lines = []
    character_names = set()
    character_names.add('narrative')
    for line in initial_setup.splitlines():
        stripped_line = line.strip()
        
        if '##' in stripped_line and 'Setup' in stripped_line:
            continue
        
        ## Wrong statement correction
        match = re.match(r'/\s*\*\s*(Types|Entities|Initial State|Utilities)\s*\*/', stripped_line)
        if match:
            section = match.group(1)
            preprocessed_initial_setup_lines.append(format_map[section])
        else:
            preprocessed_initial_setup_lines.append(line)

        ## Character entity name extraction
        entity_match = re.match(r"entity\s+([a-zA-Z0-9_ .']+?)\s*:\s*character\s*;", stripped_line)
        if entity_match:
            character_names.add(entity_match.group(1))
    
    ## Utility function argument format correction
    corrected_lines = []
    for line in preprocessed_initial_setup_lines:
        utility_match = re.match(r'\s*utility\s*\(\s*([^\)]+)\s*\)\s*:?', line)
        if utility_match:
            raw_name = utility_match.group(1)
            cleaned_name = re.sub(r'\s*(?::\s*character\s*;?|[:;])\s*$', '', raw_name).strip()

            if cleaned_name in character_names:
                corrected_lines.append(f"utility({cleaned_name}):")
            else:
                corrected_lines.append(line)
        else:
            corrected_lines.append(line)
 
    return '\n'.join(corrected_lines)

def generate_initial_setup(data, logger, args):
    
    initial_setup = None
    initial_setup_edit_cnt = 0
    
    if data.get('initialization', {}).get('initial_setup') is not None:
        
        logger.debug('===Initial Setup already exists. Loading...===')
        initial_setup = data['initialization']['initial_setup']
        initial_setup_edit_cnt = data['initialization']['initial_setup_edit_cnt']
        
    else:
        
        logger.info(f'({data["example_id"]}) Generating Initial Setup...')
        story_prompt = data['inputs']
        
        init_setup_prompt = build_init_setup_prompt(story_prompt=story_prompt)
        
        initital_setup_draft = run_llm(user_prompt=init_setup_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)
        
        logger.debug(f"===initial_setup_draft===\n{initital_setup_draft}")

        feedback_n = 0
        initial_setup_edited = initital_setup_draft
        while feedback_n < args.max_setup_feedback:
            logger.debug(f"...{feedback_n+1}' Edit In Progress...")
            init_setup_feedback_prompt = build_init_setup_feedback_prompt(
                story_prompt=story_prompt,
                initital_setup=initial_setup_edited)

            init_setup_feedback = run_llm(user_prompt=init_setup_feedback_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)

            logger.debug(f'===initial_setup_feedback_{feedback_n+1}===\n{init_setup_feedback}')

            init_setup_edit_prompt = build_init_setup_edit_prompt(
                story_prompt=story_prompt,
                feedback=init_setup_feedback,
                initital_setup=initial_setup_edited)

            initial_setup_edit_response = run_llm(user_prompt=init_setup_edit_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)

            if 'No Change' in initial_setup_edit_response:
                break

            initial_setup_edited = initial_setup_edit_response

            logger.debug(f'===initial_setup_edited_{feedback_n+1}===\n{initial_setup_edited}')

            feedback_n += 1
            
        initial_setup = preprocess_initial_setup(initial_setup_edited)
        initial_setup_edit_cnt = feedback_n
    
    logger.debug(f'===Returned Initial Setup===\n{initial_setup}')
    return initial_setup, initial_setup_edit_cnt

def preprocess_character_profile(profile):
    return profile.replace('## Profile', '').strip()

def generate_character_agents(data, logger, args):
    
    character_agent_list = None
    
    if data.get('initialization', {}).get('character_agent_list') is not None:
        
        logger.debug('===Character Agents already exists. Loading...===')
        character_agent_list = data['initialization']['character_agent_list']
        updated_initial_setup = data['initialization']['initial_setup']
        
    else:
        
        logger.info(f'({data["example_id"]}) Generating Character Agents...')
        
        initial_setup = data['initialization']['initial_setup']
        
        role_classification_prompt = ROLE_CLASSIFICATION_PROMPT.format(
            initital_setup=initial_setup)
        
        character_agent_list = run_llm(user_prompt=role_classification_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)

        logger.debug(f'===character_agent_classification===\n{character_agent_list}')
        
        for character_agent_json in character_agent_list:
            name = character_agent_json['name']
            role = character_agent_json['role']
            if role == 'main':
                profile_format = PROFILE_FORMAT_MAIN
            elif role == 'villain':
                profile_format = PROFILE_FORMAT_VILLAIN
            elif role == 'side':
                profile_format = PROFILE_FORMAT_SIDE
            else:
                logger.error(f"ERROR: Unexpected Role {role}")
                raise ValueError
                
            init_character_agent_prompt = INIT_CHARACTER_AGENT_PROMPT.format(
                name=name,
                initital_setup=initial_setup,
                profile_format=profile_format
            )
            
            profile = run_llm(user_prompt=init_character_agent_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)
            profile = preprocess_character_profile(profile)
            character_agent_json['profile'] = profile
            
            character_utility = extract_character_utility(initial_setup, name)
   
            character_agent_json['character_utility'] = character_utility
            
            summarize_character_agent_prompt = SUMMARIZE_CHARACTER_AGENT_PROMPT.format(
                name=name,
                profile=profile
            )
            
            summarized_profile = run_llm(user_prompt=summarize_character_agent_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model)
            character_agent_json['summarized_profile'] = summarized_profile

        ## Initialize Character Utility Functions from the each character's viewpoint.
        for character_agent_json in character_agent_list:
   
            updated_character_utility = update_character_utility(
                setup=initial_setup,
                target_character_agent=character_agent_json,
                story_progress_list=[],
                args=args)

            character_agent_json['character_utility'] = updated_character_utility
    
        ## Update Initial Setup accordingly
        updated_initial_setup = update_setup_character_utility(initial_setup, character_agent_list)
    
    logger.debug(f"===Returned Character Agents===\n{character_agent_list}")
    return updated_initial_setup, character_agent_list


##############################
####                      ####
####  Utils for planning  ####
####                      ####
##############################

def character_profiles_to_prompt(character_agent_list):
    '''
    Transform Characters' Profiles for prompting
    '''
    character_profiles_text = ''
    for character_agent in character_agent_list:
        name = character_agent['name']
        role = character_agent['role']
        profile = character_agent['profile']
        
        if role != None:
            character_profiles_text += f"### {name}'s Profile (role: {role})\n" + profile + '\n'
        else:
            character_profiles_text += f"### {name}'s Profile (role: Not Assigned)\n" + profile + '\n'
    
    return character_profiles_text.strip()

def validate_plan(plan_response):
    try:
        if not isinstance(plan_response, dict):
            return False
        
        for k, v in plan_response.items():
            if not isinstance(v, list) or 'utility(narrative)' not in k:
                return False
        
        return plan_response
    except:
        return False

def preprocess_plan(plan_response):
    preprocessed_plan = ""
    for k, v in plan_response.items():
        preprocessed_plan += str(k) + ':'
        for goal in v:
            preprocessed_plan += f'\n\t{goal}'
    return preprocessed_plan

def validate_act_sequence(sequence_of_acts_response):
    try:
        if not isinstance(sequence_of_acts_response, list):
            return False
        
        json.dumps(sequence_of_acts_response)
        
        return sequence_of_acts_response
    except:
        return False

def generate_plan(data, logger, args):
    
    plan = None
    
    if data.get('initialization', {}).get('plan') is not None:
        
        logger.debug('===Plan already exists. Loading...===')
        plan = data['initialization']['plan']
        
    else:
        
        logger.info(f'({data["example_id"]}) Generating Plan...')
        
        plan = {}
        inputs = data['inputs']
        initial_setup = data['initialization']['initial_setup']
        character_agent_list = data['initialization']['character_agent_list']
        
        character_profiles_text = character_profiles_to_prompt(character_agent_list)
        cleaned_setup, utility_narrative = remove_and_extract_utility_information(setup=initial_setup, character='narrative')
        
        MAX_RETRY = 3
        last_part_n = 4
        previous_plans = []
        for i in range(last_part_n):
            logger.debug(f"===Generating Narrative Goals for PART {i+1}===")
            
            is_last_part = False
            if i+1 >= last_part_n:
                is_last_part = True
                
            plan_prompt = build_plan_prompt(
                initial_setup=cleaned_setup,
                character_profiles=character_profiles_text,
                utility_narrative=utility_narrative,
                story_prompt=inputs,
                part_n=i+1,
                previous_plans=previous_plans,
                is_last_part=is_last_part
            )
            
            retry_n = 0
            while retry_n < MAX_RETRY:
                plan_response = run_llm(user_prompt=plan_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model, temperature= 1 - (0.1 * retry_n))
                plan_response = validate_plan(plan_response)
                
                if plan_response == False:
                    retry_n += 1
                else:
                    break
            
            logger.debug(f"===Planned Narrative Goals for PART 1===\n{plan_response}")
        
            plan[f'part_{i+1}'] = preprocess_plan(plan_response)
            previous_plans.append(plan_response)
    
        ## Convert utility(narrative) of each part to a sequence of acts
        if args.act_seq_mode:
            last_part = 1
            while plan.get(f'part_{last_part+1}') is not None:
                last_part += 1
            
            part_n = 1
            previous_acts=[]
            while plan.get(f'part_{part_n}') is not None:
                logger.debug(f"===Converting Narrative Goals for PART {part_n} to a sequence of acts===")
                cleaned_setup, utility_narrative = remove_and_extract_utility_information(setup=initial_setup, character='narrative')
                utility_narrative_part = plan[f'part_{part_n}']
                convert_narrative_utility_to_act_prompt = build_convert_narrative_utility_to_act_prompt(
                    initial_setup=cleaned_setup,
                    utility_narrative=utility_narrative_part,
                    plan_mode=True,
                    part_n=part_n,
                    previous_acts=previous_acts,
                    is_last_part=(part_n >= last_part)
                )
                
                retry_n = 0
                while retry_n < MAX_RETRY:
                    sequence_of_acts_response = run_llm(user_prompt=convert_narrative_utility_to_act_prompt, system_prompt=PLANNER_AGENT_SYSTEM_PROMPT, model=args.planner_agent_base_model, temperature= 1 - (0.1 * retry_n))
                    
                    sequence_of_acts_response = validate_act_sequence(sequence_of_acts_response)
                    
                    if sequence_of_acts_response == False:
                        retry_n += 1
                    else:
                        break
                
                logger.debug(f"===Sequence of acts for PART {part_n}===\n{sequence_of_acts_response}")
                plan[f'part_{part_n}_act_seq'] = sequence_of_acts_response
                
                previous_acts.append(str(sequence_of_acts_response))
                part_n += 1
    
    logger.debug(f"===Returned Plan===\n{plan}")
    return plan


#### Update information of Setup ####
def update_narrative_utility(setup, narrative_utility):
    """ Update utility(narrative) in Setup.
    Replace utility(narrative) to current PART's utility(narrative).
    Parameters
    ----------
    setup : str
            Setup text (including Types, Entities, Initial State, etc.)
    narrative_utility : str
            planner agent's response of current PART's utility(narrative)
    """
    
    # Handle output format issue.
    if f"utility(narrative)" not in narrative_utility:
        narrative_utility = f"utility(narrative):\n" + "\t" + narrative_utility + "\n"
        
    original_narrative_utility = extract_character_utility(setup, 'narrative')
    return setup.replace(original_narrative_utility, narrative_utility)