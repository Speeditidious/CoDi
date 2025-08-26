import sys
sys.path.insert(0, '.')
import re
import os
import logging
import copy
from global_utils import *
from director_agent_utils import remove_utility_information
from prompts.character_agent_prompt import *

#### setup logger ####
log_file_path = os.path.join(os.environ['LOG_DIR'], 'character_agent_utils.log')
logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)

### Extract required information from Setup ###
def extract_character_utility(setup, character):
    """ Extract character utility function from Setup text.
    Parameters
    ----------
    setup : str
            Setup text
    character : str
            character's name to extract
    """
    
    escaped_character = re.escape(character)
    utility_pattern = rf"""
        utility\(
            (?:
                "{escaped_character}"
                |'{escaped_character}'
                |{escaped_character}(?:\s+\([^)]+\))?
                |{escaped_character}\s*:\s*\w+
                |{escaped_character}
            )
        \):
        .*?(?=\n\n|\nutility\(|\Z)
    """
    match = re.search(utility_pattern, setup, flags=re.DOTALL | re.MULTILINE | re.VERBOSE)
    
    if match:
        return match.group(0).strip()
    
    for sub_name in character.split():
        escaped_sub_name = re.escape(sub_name)
        utility_pattern = rf"""
            utility\(
                (?:
                    "{escaped_sub_name}"
                    |'{escaped_sub_name}'
                    |{escaped_sub_name}(?:\s+\([^)]+\))?
                    |{escaped_sub_name}\s*:\s*\w+
                    |{escaped_character}
                )
            \):
            .*?(?=\n\n|\nutility\(|\Z)
        """
        match = re.search(utility_pattern, setup, flags=re.DOTALL | re.MULTILINE | re.VERBOSE)
        
        if match:
            return match.group(0).strip()
    
    logger.debug(f"Could not extract utility of {character} from response (will be resolved after updating character utility).\n===Response===\n{setup}")
    return None


### Remove unnecessary information from Setup ###
def remove_utility_information_of_others(setup, character):
    """ Remove other characters' utility function from Setup text.
    Parameters
    ----------
    setup : str
            Setup text
    character : str
            character's name to remain
    """
    character_utility = extract_character_utility(setup, character)
    
    setup_without_utility = re.sub(r"(/\* Utilities \*/)(.*)", r"\1", setup, flags=re.DOTALL)
    
    cleaned_text = setup_without_utility + '\n' + character_utility
    
    return cleaned_text.strip()

def remove_and_extract_utility_information(setup, character):
    """ Remove and extract a specific character's utility function from Setup text.
    Parameters
    ----------
    setup : str
            Setup text
    character : str
            character's name to remove and extract
    """
    character_utility = extract_character_utility(setup, character)
    
    cleaned_setup = re.sub(re.escape(character_utility), '', setup, count=1)
    
    return cleaned_setup.strip(), character_utility.strip()

def remove_summarized_character_profiles(setup):
    """ Remove summarized character profiles to hide other characters' information.
    Parameters
    ----------
    setup : str
            Setup text
    """
    
    pattern = r'/\* Character Profiles \*/.*?(?=(/\*|$))'
    cleaned_text = re.sub(pattern, '', setup, flags=re.DOTALL)
    
    return cleaned_text.strip()


### Update information of Setup ###
def validate_updated_character_utility(updated_character_utility_response, name):
    """ Check whether the agents' response in chracter utility update phase is valid.
    1. the format of the response should be dictionary
    2. key: utility(name), value: list
    Parameters
    ----------
    updated_character_utility_response : str
            agents' response (character utility function)
    name : str
            character's name
    """
    
    try:
        if not isinstance(updated_character_utility_response, dict):
            return False
        
        for k, v in updated_character_utility_response.items():
            if not isinstance(v, list) or f'utility({name})' not in k:
                return False
        
        return updated_character_utility_response
    except:
        return False
    
def preprocess_updated_character_utility(updated_character_utility_response):
    """ Preprocess agents' response in character utility update phase.
    response -> utility function
    Parameters
    ----------
    updated_character_utility_response : str
            agents' response (character utility function)
    """
    
    preprocess_updated_character_utility = ""
    for k, v in updated_character_utility_response.items():
        preprocess_updated_character_utility += str(k) + ':'
        for goal in v:
            preprocess_updated_character_utility += f'\n\t{goal}'
    return preprocess_updated_character_utility

def update_character_utility(setup, target_character_agent, args, story_progress_list=[]):
    """ Update character utility function.
    Find the character's utility function and update and return the function.
    Parameters
    ----------
    setup : str
            Setup text
    target_character_agent : json
            target character agent
    story_progress_list : list
            story progress list
    """
    
    name = target_character_agent['name']
    profile = target_character_agent['profile']
    current_character_utility = target_character_agent['character_utility']
    
    if current_character_utility is None:
        current_character_utility = f"utility({name}):\n\tNo current goals or desires specified."
    
    logger.debug(f"===Before Updating Character Utility for {name}===\n{current_character_utility}")
    
    if story_progress_list == []:
        ## Start of the narrative. Provide Inisital Setup without others' utility fucntions.
        story_progress_tom = remove_utility_information(setup)
    else:
        from generation_utils import preprocess_story_progress_list
        story_progress_text = preprocess_story_progress_list(story_progress_list)
        story_progress_tom = hide_thought_of_others(story_progress=story_progress_text, character=name)
    
    character_agent_system_prompt = CHARACTER_AGENT_SYSTEM_PROMPT.format(name=name)
    update_character_utility_prompt = UPDATE_CHARACTER_UTILITY_PROMPT.format(
        name=name,
        profile=profile,
        character_utility=current_character_utility,
        story_progress=story_progress_tom)
    
    MAX_RETRY = 3
    retry_n = 0
    updated_character_utility = None
    while retry_n < MAX_RETRY:
        updated_character_utility_response = run_llm(user_prompt=update_character_utility_prompt, system_prompt=character_agent_system_prompt, model=args.character_agent_base_model, temperature=1-(0.1*retry_n))
        updated_character_utility_response = validate_updated_character_utility(updated_character_utility_response, name)
        
        logger.debug(f"===Update Character Utility: {retry_n+1}'s try===\n{updated_character_utility_response}")
        
        if updated_character_utility_response == False:
            retry_n += 1
        else:
            updated_character_utility = preprocess_updated_character_utility(updated_character_utility_response)
            break
    
    if updated_character_utility is None:
        logger.debug('===Returning the original character utility===')
        return current_character_utility

    logger.debug(f'===Updated Character Utility for {name}===\n{updated_character_utility}')
    
    return updated_character_utility

def update_setup_character_utility(setup, character_agent_list):
    """ Update character utility function string in setup text.
    Find the character's utility functions and replace it to updated one.
    Parameters
    ----------
    setup : str
            Setup text
    character_agent_list : list
            character agent list to update
    """
    
    logger.debug(f"===Before Setup Update (Character Utility)===\n{setup}")
    updated_setup = copy.deepcopy(setup)
    for character_agent in character_agent_list:
        name = character_agent['name']
        updated_character_utility = character_agent['character_utility']
        
        # Find the character's utility function and replace it to updated one.
        character_utility = extract_character_utility(setup, name)
        if character_utility is None:
            updated_setup = setup + '\n\n' + updated_character_utility
        else:
            updated_setup = setup.replace(character_utility, updated_character_utility)
    
    logger.debug(f"===After Setup Update (Character Utility)===\n{updated_setup}")
    return updated_setup

### Preprocess ###
def preprocess_character_reaction(character_reaction):
    """ Preprocess character_reaction to record it to Story Progress.
    Preprocess Format - {character_name} (at {character_location}): {character_reaction}
    Parameters
    character_reaction : dictionary
                        character_reaction['name']: {character_name}
                        character_reaction['location']: {character_location}
                        character_reaction['reaction']: {character_reaction}
    """
    name_prefix = f"{character_reaction['name']} (at {character_reaction['location']}):"
    reaction = character_reaction['reaction']
    
    pattern_reasoning = r'\*\*Reasoning\*\*:.*'
    reaction = re.sub(pattern_reasoning, '', reaction, flags=re.DOTALL)
    
    if reaction.strip().startswith(name_prefix):
        reaction = reaction.strip()[len(name_prefix):].lstrip()
    
    reaction = ' '.join(reaction.split('\n')).strip()
    
    return name_prefix + ' ' + reaction

def hide_thought_of_others(story_progress, character=None):
    """ Hide **thought** information of other characters in character agent's reaction response.
    Hide **thought** information. Characters cannot see other characters' thoughts.
    Parameters
    ----------
    story_progress : str
                    story_progress
    character : str
                character's name
                None = hide **thought** of all of the characters
    """
    think_pattern = r"\[.*?\]"
    
    paragraphs = story_progress.split('\n')
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        if paragraph == '':
            continue
        
        paragraph_character = paragraph.split(':')[0]
        # Do not hide the selected character's **thought**
        if character != None:
            if character in paragraph_character:
                cleaned_paragraphs.append(paragraph)
                continue
        
        cleaned_paragraph = re.sub(think_pattern, '', paragraph)
        cleaned_paragraph = re.sub(r'\s+', ' ', cleaned_paragraph).strip()
        cleaned_paragraphs.append(cleaned_paragraph)
    
    return '\n'.join([cleaned_paragraph for cleaned_paragraph in cleaned_paragraphs if cleaned_paragraph != ''])