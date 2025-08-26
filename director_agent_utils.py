import sys
sys.path.insert(0, '.')
import re
import ast
import logging
import os
from global_utils import setup_logger

#### setup logger ####
log_file_path = os.path.join(os.environ['LOG_DIR'], 'director_agent_utils.log')
logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)


### Extract required information from response ###
def extract_directing_decision(response):
    """ Extract directing decision information from director agent's response.
    Parameters
    ----------
    response : str
            director agent's response
    """
    instruction_pattern = r"Instruction:\s*([^\n\r]+)"
    instruction_match = re.search(instruction_pattern, response)
        
    choice_pattern = r"Choice:\s*([^\n\r]+)"
    choice_match = re.search(choice_pattern, response)
    
    if instruction_match and choice_match:
        return instruction_match.group(1).strip(), choice_match.group(1).strip()
    else:
        if choice_match:
            return "No instruction.", choice_match.group(1).strip()
        logger.error(f"Unexpected response format while extracting directing decision.\n===Response===\n{response}")
        raise Exception("Unexpected response format while extracting directing decision.")

def extract_chosen_character_information(choice):
    """ Extract chosen character information from director agent's choice.
    Parameters
    ----------
    response : str
            director agent's choice.
            Format: Act(Character's name, Character's location)
    """
    chosen_character_pattern = r"(?:Act\()?\s*([^\n\r,()]+)\s*,?\s*\(?(?:at\s+)?([^)]+)\)?\)?"
    chosen_character_match = re.search(chosen_character_pattern, choice)
    
    if chosen_character_match:
        return chosen_character_match.group(1).strip(), chosen_character_match.group(2).strip()
    else:
        logger.error(f"Unexpected response format while extracting chosen character information.\n===Response==={choice}")
        raise Exception("Unexpected response format while extracting chosen character information.")

def extract_intervention(response):
    """ Extract intervention from director agent's response.
    Parameters
    ----------
    response : str
            director agent's response
    """
    intervention_pattern = r"Intervention:\s*([^\n\r]+)"
    intervention_match = re.search(intervention_pattern, response)
    
    if intervention_match:
        return re.sub(r'\s*\n\s*', ' ', intervention_match.group(1)).strip()
    else:
        logger.error(f"Unexpected response format while extracting intervention.\n===Response===\n{response}")
        raise Exception("Unexpected response format while extracting intervention.")
    
def extract_description(response):
    """ Extract description from director agent's response.
    Parameters
    ----------
    response : str
            director agent's response
    """
    choice_pattern = r"Choice:\s*([^\n\r]+)"
    choice_match = re.search(choice_pattern, response)
    if choice_match:
        if 'Pass' in choice_match.group(1):
            return 'Pass', 'Pass'
        
        description_pattern = r"Description:\s*([^\n\r]+)"
        description_match = re.search(description_pattern, response)
        
        if description_match:
            return 'Describe', re.sub(r'\s*\n\s*', ' ', description_match.group(1)).strip()
        else:
            logger.error(f"Unexpected response format while extracting description.\n===Response===\n{response}")
            raise Exception("Unexpected response format while extracting description.")
    else:
        logger.error(f"Unexpected response format while extracting Choice in description response.\n===Response===\n{response}")
        raise Exception("Unexpected response format while extracting Choice in description response. Check director_agent_utils.log")
    

### Remove unnecessary information from Setup ###
def remove_utility_information(setup):
    """ Remove /* Utilities */ information from Setup.
    Use when utility function information is unnecessary or noisy.
    Parameters
    ----------
    setup : str
            Setup text (including Types, Entities, Initial State, etc.)
    """
    util_start = setup.find("/* Utilities */")
    if util_start == -1:
        logger.error(f"Could not find /* Utilities */\n===Setup==={setup}")
        raise Exception('Could not find /* Utilities */')
    
    next_block = setup.find("/*", util_start + len("/* Utilities */"))
    if next_block == -1:
        return setup[:util_start]
    else:
        return setup[:util_start] + setup[next_block:]

def remove_initial_state_information(setup):
    """ Remove /* Initial State */ information from Setup.
    Parameters
    ----------
    setup : str
            Setup text (including Types, Entities, Initial State, etc.)
    """
    initial_state_start = setup.find("/* Initial State */")
    if initial_state_start == -1:
        logger.error(f"Could not find /* Initial State */\n===Setup==={setup}")
        raise Exception('Could not find /* Initial State */')
    
    next_block = setup.find("/*", initial_state_start + len("/* Initial State */"))
    if next_block == -1:
        return setup[:initial_state_start]
    else:
        return setup[:initial_state_start] + setup[next_block:]


#### Update information of Setup ####
def update_types_entities(setup, updated_types_entities):
    """ Update /* Types */ and /* Entities */ in Setup.
    Replace /* Types */ and /* Entities */ to updated ones.
    Parameters
    ----------
    setup : str
            Setup text (including Types, Entities, Initial State, etc.)
    updated_types_entities : str
            director agent's response toward /* Types */ and /* Entities */ to replace those in Setup text
    """
    # Remain only /* Types */ and /* Entities */ from updated_types_entities
    initial_state_start = updated_types_entities.find("/* Initial State */")
    if initial_state_start != -1:
        updated_types_entities = updated_types_entities[:initial_state_start].strip()
    
    # Find pattern of /* Types */ and /* Entities */ + Replace
    pattern = r'/\* Types \*/\s*(.*?)\s*/\* Entities \*/\s*(.*)'
    match = re.search(pattern, updated_types_entities, re.DOTALL)
    
    updated_setup = setup
    if match:
        types_to_add = match.group(1).strip()
        entities_to_add = match.group(2).strip()
        
        if 'No Change' not in types_to_add:
            types_start = updated_setup.find("/* Types */")
            if types_start == -1:
                raise Exception('Could not find /* Types */')
            
            types_section_start = types_start + len("/* Types */")
            types_next_block = updated_setup.find("/*", types_section_start)
            if types_next_block == -1:
                updated_setup += '\n' + types_to_add
            else:
                types_section_body = updated_setup[types_section_start:types_next_block]
                types_section_body = types_section_body.rstrip()
                types_to_add = types_to_add.strip()
                if types_section_body:
                    types_section_body = types_section_body + '\n' + types_to_add + '\n\n'
                else:
                    types_section_body = types_to_add + '\n\n'
                
                updated_setup = updated_setup[:types_section_start] + types_section_body + updated_setup[types_next_block:]
            
        if 'No Change' not in entities_to_add:
            entities_start = updated_setup.find("/* Entities */")
            if entities_start == -1:
                raise Exception('Could not find /* Entities */')
            
            entities_section_start = entities_start + len("/* Entities */")
            entities_next_block = updated_setup.find("/*", entities_section_start)
            if entities_next_block == -1:
                updated_setup += '\n' + entities_to_add
            else:
                entities_section_body = updated_setup[entities_section_start:entities_next_block]
                entities_section_body = entities_section_body.rstrip()
                entities_to_add = entities_to_add.strip()
                if entities_section_body:
                    entities_section_body = entities_section_body + '\n' + entities_to_add + '\n\n'
                else:
                    entities_section_body = entities_to_add + '\n\n'
                
                updated_setup = updated_setup[:entities_section_start] + entities_section_body + updated_setup[entities_next_block:]
    
    return updated_setup

def update_initial_state(setup, updated_initial_state):
    """ Update /* Initial State */ in Setup.
    Replace /* Initial State */ to updated ones.
    Parameters
    ----------
    setup : str
            Setup text (including Types, Entities, Initial State, etc.)
    updated_initial_state : str
            director agent's response toward /* Initial State */ to replace those in Setup text
    """
    
    # Nothing to update. Return origianl Setup text.
    if 'No Change' in updated_initial_state:
        return setup
    
    # Director agent responsed with out /* Initial State */ text. Append it.
    if "/* Initial State */" not in updated_initial_state:
        updated_initial_state = "/* Initial State */\n\n" + updated_initial_state
    
    # Replace
    initial_state_start = setup.find("/* Initial State */")
    if initial_state_start == -1:
        logger.error(f"Could not find /* Initial State */ from Setup.\n===Setup===\n{setup}")
        raise Exception('Could not find /* Initial State */ from Setup.')
    
    next_block = setup.find("/*", initial_state_start + len("/* Initial State */"))
    if next_block == -1:
        return setup[:initial_state_start] + updated_initial_state
    else:
        return setup[:initial_state_start] + updated_initial_state + '\n\n' + setup[next_block:]