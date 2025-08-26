import sys
sys.path.insert(0, '.')
import logging
import argparse
import os
import copy

from global_utils import *
from generation_utils import *
from director_agent_utils import *
from character_agent_utils import *
from planner_agent_utils import *
from editor_agent_utils import *
from prompts.planner_agent_prompt import *
from prompts.director_agent_prompt import *
from prompts.character_agent_prompt import *

def parse_args():
    
    parser = argparse.ArgumentParser()
    ## Path to data to use
    parser.add_argument('--data-file', type=str, required=True)
    ## Directory of save data
    parser.add_argument('--out-dir', type=str, required=True)
    ## Path to data for using the same initial settings (Setup, Character Agents, Plan, Start of narrative)
    parser.add_argument('--setting-file', type=str, default='None')
    ## Path to load data (in case the experiment was interrupted)
    parser.add_argument('--load-file', type=str, default='None')
    ## Whether to use planning
    parser.add_argument('--plan-mode', action='store_true')
    ## Whether to convert utility(narrative) to a sequence of acts
    parser.add_argument('--act-seq-mode', action='store_true')
    ## Ablation Study
    parser.add_argument('--no-intervention', action='store_true')
    parser.add_argument('--no-description', action='store_true')
    ## Reformatting Format (default = screenplay)
    parser.add_argument('--reformat-novel', action='store_true')
    ## Maximum number of feedbacks during the Setup construction
    parser.add_argument('--max-setup-feedback', type=int, default=3)
    ## Maximum number of turns allowed
    parser.add_argument('--max-turn', type=int, default=200)
    parser.add_argument('--max-turn-part', type=int, default=200)
    parser.add_argument('--max-turn-act', type=int, default=50)
    ## Base models of agents
    parser.add_argument('--planner-agent-base-model', type=str, default='None')
    parser.add_argument('--director-agent-base-model', type=str, default='None')
    parser.add_argument('--editor-agent-base-model', type=str, default='None')
    parser.add_argument('--character-agent-base-model', type=str, default='None')
    
    args = parser.parse_args()
    
    return args


def log_generation_setting(logger, args):
    
    logger.info('===Generation Settings===')
    logger.info(f'Data File: {args.data_file}')
    logger.info(f'Out Directory: {args.out_dir}')
    logger.info(f'Setting Data File: {args.setting_file}')
    logger.info(f'Load Data File: {args.load_file}')
    if args.plan_mode or args.act_seq_mode:
        if args.planner_agent_base_model == 'None':
            logger.error('Plan or Act seq mode is enabled, but the planner-agent-base-model is not defined.')
            raise ValueError
        logger.info(f'Planner agent base model: {args.planner_agent_base_model}')
    if args.director_agent_base_model == 'None' or args.character_agent_base_model == 'None':
        logger.error('director-agent-base-model or character-agent-base-model is not defined.')
        raise ValueError
    logger.info(f'Director agent base model: {args.director_agent_base_model}')
    logger.info(f'Character agent base model: {args.character_agent_base_model}')
    logger.info(f'Editor agent base model: {args.editor_agent_base_model}')
    logger.info(f'Plan mode: {args.plan_mode}')
    logger.info(f'Act seq mode: {args.act_seq_mode}')
    logger.info(f'Maximum setup feedback: {args.max_setup_feedback}')
    if args.act_seq_mode:
        logger.info(f'Maximum turn per Act: {args.max_turn_act}')
    elif args.plan_mode:
        logger.info(f'Maximum turn per Part: {args.max_turn_part}')
    else:
        logger.info(f'Maximum turn: {args.max_turn}') 
    if args.reformat_novel:
        logger.info(f'Narrative Format: Novel')
    else:
        logger.info(f'Narrative Format: Screenplay')

def generate_narrative(data, setting_data, out_dataset, logger, args):
    
    logger.info(f"({data['example_id']}) Simulating narrative... (Refer ./log/generation.log file for the simulation details)")
    
    # Initialization
    example_id = data['example_id']
    setup = data['initialization']['initial_setup']
    character_agent_list = data['initialization']['character_agent_list']
    plan = data['initialization'].get('plan')

    data = init_narrative_generation(data, setting_data, args)

    # Determine Part Iteration
    part_iterations = [None]  # For no-plan mode, loop once with part=None
    last_part = 0
    if args.plan_mode:
        last_part = 1
        while plan.get(f'part_{last_part + 1}') is not None:
            last_part += 1
        part_iterations = range(1, last_part + 1)

    # Part-level Loop
    for part in part_iterations:
        story_progress_list = []
        part_force_quit = False
        if args.plan_mode:
            # Check if part is already completed
            if data.get('narrative', {}).get(f'part_{part}', {}).get('turn_-1', {}).get('part_summary') is not None:
                logger.debug(f'...({example_id}) Part {part}... already ended')
                character_agent_list = data['narrative'][f'part_{part}']['turn_-1']['character_agent_list']
                setup = data['narrative'][f'part_{part}']['turn_-1']['setup']
                continue

            story_progress_list = build_context_start_of_new_part(data, part, args)
            
            if data.get('narrative', {}).get(f'part_{part}') is None:
                data['narrative'][f'part_{part}'] = {}
            
            part_narrative_utility = plan[f'part_{part}']
            setup = update_narrative_utility(setup, part_narrative_utility).strip()

        # Determine Act Iteration
        act_iterations = [(None, None)]  # For modes without acts, loop once
        act_sequence = []
        if args.act_seq_mode:
            act_sequence = [list(act.values())[0] for act in plan[f'part_{part}_act_seq']]
            act_iterations = enumerate(act_sequence, 1)

        # Act-level Loop
        for act, current_act in act_iterations:
            
            # Turn Loop Setup
            turn = 1
            is_description_decided = False
            MAX_RESOLUTION_RETRY = 3
            cnt_retry = 0
            resolve_wrong_character_choice_mode = False
            wrong_direct_response = ''
            force_quit = False
            
            # Determine turn loop parameters based on mode
            if args.act_seq_mode:
                max_turn = args.max_turn_act
                is_last_act = ((act >= len(act_sequence)) and (part >= last_part))
                end_phrase = "STORY ENDS" if is_last_act else "ACT ENDS"
                data_path_keys = ['narrative', f'part_{part}', f'act_{act}']
                log_prefix = f'({example_id}) Part {part} Act {act}'
            elif args.plan_mode:
                max_turn = args.max_turn_part
                is_last_part = (part >= last_part)
                end_phrase = f'PART {part} ENDS' if not is_last_part else 'STORY ENDS'
                data_path_keys = ['narrative', f'part_{part}']
                log_prefix = f'({example_id}) Part {part}'
            else:  # no plan
                max_turn = args.max_turn
                end_phrase = 'STORY ENDS'
                data_path_keys = ['narrative']
                log_prefix = f'({example_id})'

            # Turn-level Loop
            while turn <= max_turn:
                # Check for existing data
                turn_data_parent = data
                for key in data_path_keys:
                    turn_data_parent = turn_data_parent.get(key, {})
                
                turn_data = turn_data_parent.get(f'turn_{turn}', {})

                if turn_data.get('story_progress') is not None:
                    if end_phrase in turn_data['story_progress']:
                        logger.debug(f'...{log_prefix} ended in Turn {turn}...')
                        story_progress_list.append(turn_data['story_progress'])
                        break
                    logger.debug(f'...{log_prefix} Trun {turn}... already exist')
                    story_progress_list.append(turn_data['story_progress'])
                    turn += 1
                    continue
                
                # Create parent dict to record narrative simulation based on the modes (no plan, plan, act etc.)
                turn_parent_dict = data
                for key in data_path_keys:
                    if key not in turn_parent_dict: turn_parent_dict[key] = {}
                    turn_parent_dict = turn_parent_dict[key]
                if f'turn_{turn}' not in turn_parent_dict:
                    turn_parent_dict[f'turn_{turn}'] = {}
                
                # Build context
                cleaned_setup = remove_initial_state_information(setup=setup)
                cleaned_setup, utility_narrative = remove_and_extract_utility_information(setup=cleaned_setup, character='narrative')
                cleaned_setup = preprocess_setup(cleaned_setup)
                cleaned_setup = add_summarized_profiles(cleaned_setup, character_agent_list)
                story_progress_text = preprocess_story_progress_list(story_progress_list)
                
                # Build director prompt
                is_beginning = (turn == 1) and (part is None or (part == 1 and (act is None or act == 1)))
                
                if is_beginning:
                    cleaned_setup_for_beginning = remove_utility_information(setup)
                    cleaned_setup_for_beginning = preprocess_setup(cleaned_setup_for_beginning)
                    cleaned_setup_for_beginning = add_summarized_profiles(cleaned_setup_for_beginning, character_agent_list)
                    direct_prompt = build_beginning_prompt(
                        setup=cleaned_setup_for_beginning,
                        story_prompt=data['inputs'],
                        utility_narrative=utility_narrative if not args.act_seq_mode else None,
                        current_act=current_act if args.act_seq_mode else None)
                elif turn == max_turn:
                    logger.debug(f'...{log_prefix} Trun {turn}... Force concluding the story because turn reached to its maximum turn.')
                    force_quit = True
                    direct_prompt = build_quit_direct_prompt(
                        setup=cleaned_setup,
                        story_progress=story_progress_text,
                        utility_narrative=utility_narrative,
                        no_intervention=args.no_intervention,
                        plan_mode=args.plan_mode,
                        part_n=part,
                        is_last_part=(args.plan_mode and is_last_part),
                        act_seq_mode=args.act_seq_mode,
                        current_act=current_act,
                        is_last_act=(args.act_seq_mode and is_last_act))
                elif is_character_reaction(story_progress_list) and not is_description_decided and not args.no_description:
                    story_progress_tom = hide_thought_of_others(story_progress=story_progress_text)
                    direct_prompt = build_description_prompt(
                        setup=cleaned_setup,
                        story_progress=story_progress_tom,
                        utility_narrative=utility_narrative,
                        plan_mode=args.plan_mode,
                        part_n=part,
                        act_seq_mode=args.act_seq_mode,
                        current_act=current_act)
                else:
                    if resolve_wrong_character_choice_mode:
                        direct_prompt = build_direct_prompt_resolve_wrong_character_choice(
                            setup=cleaned_setup,
                            story_progress=story_progress_text,
                            utility_narrative=utility_narrative,
                            wrong_direct_response=wrong_direct_response,
                            plan_mode=args.plan_mode,
                            part_n=part)
                    else:
                        direct_prompt = build_direct_prompt(
                            setup=cleaned_setup,
                            story_progress=story_progress_text,
                            utility_narrative=utility_narrative,
                            no_intervention=args.no_intervention,
                            plan_mode=args.plan_mode,
                            part_n=part,
                            part_end_phrase=end_phrase if args.plan_mode and not args.act_seq_mode else None,
                            is_last_part=(args.plan_mode and is_last_part),
                            act_seq_mode=args.act_seq_mode,
                            current_act=current_act,
                            act_end_phrase=end_phrase if args.act_seq_mode else None,
                            is_last_act=(args.act_seq_mode and is_last_act))

                direct_response = run_llm(user_prompt=direct_prompt, system_prompt=DIRECTOR_AGENT_SYSTEM_PROMPT, model=args.director_agent_base_model)
                
                logger.debug(f'==={log_prefix} Trun {turn} direct===\n{direct_response}')
                turn_parent_dict[f'turn_{turn}']['direct_response'] = direct_response

                # Process direct_response
                if is_beginning:
                    beginning_record_story_progress = preprocess_beginning_story(direct_response)
                    logger.debug(f'==={log_prefix} Trun {turn}==={beginning_record_story_progress}')
                    turn_parent_dict[f'turn_{turn}']['story_progress'] = beginning_record_story_progress
                    story_progress_list.append(beginning_record_story_progress)
                elif turn < max_turn and is_character_reaction(story_progress_list) and not is_description_decided and not args.no_description: # Director Agent decided to use Description
                    is_description_decided = True
                    description_choice, description_content = extract_description(direct_response)
                    if 'Pass' in description_choice:
                        turn_parent_dict[f'turn_{turn}']['direct_response_pass'] = direct_response
                        turn -= 1 # Redo the turn
                    else:
                        logger.debug(f'==={log_prefix} Trun {turn}==={description_content}')
                        turn_parent_dict[f'turn_{turn}']['story_progress'] = description_content
                        story_progress_list.append(description_content)
                elif resolve_wrong_character_choice_mode: # Director Agent chose a character not in the setup. Utilize Intervention to generate temporary NPC response
                    is_description_decided = False
                    intervention_record_story_progress = extract_intervention(direct_response)
                    logger.debug(f'==={log_prefix} Trun {turn}==={intervention_record_story_progress}')
                    turn_parent_dict[f'turn_{turn}']['story_progress'] = intervention_record_story_progress
                    story_progress_list.append(intervention_record_story_progress)
                else:
                    is_description_decided = False
                    directing_instruction, directing_choice = extract_directing_decision(direct_response)
                    
                    if end_phrase in directing_choice or 'end' in directing_choice.lower(): # Director Agent: End
                        logger.debug(f'==={log_prefix} Trun {turn}==={end_phrase}')
                        story_progress_list.append(end_phrase)
                        turn_parent_dict[f'turn_{turn}']['story_progress'] = end_phrase
                        save_wip_data(wip_data=data, out_dataset=out_dataset, logger=logger, args=args)
                        break
                    elif 'intervention' in directing_choice.lower(): # Director Agent: Intervention
                        cleaned_setup_for_intervention = remove_utility_information(cleaned_setup)
                        story_progress_text_for_intervention = preprocess_story_progress_list(story_progress_list)
                        intervention_prompt = build_intervention_prompt(
                            setup=cleaned_setup_for_intervention,
                            story_progress=story_progress_text_for_intervention,
                            utility_narrative=utility_narrative,
                            instruction=directing_instruction,
                            plan_mode=args.plan_mode,
                            part_n=part,
                            is_last_part=(args.plan_mode and is_last_part),
                            act_seq_mode=args.act_seq_mode,
                            current_act=current_act)
                        
                        intervention_response = run_llm(user_prompt=intervention_prompt, system_prompt=DIRECTOR_AGENT_SYSTEM_PROMPT, model=args.director_agent_base_model)
                        intervention_record_story_progress = extract_intervention(intervention_response)
                        logger.debug(f'==={log_prefix} Trun {turn}==={intervention_record_story_progress}')
                        turn_parent_dict[f'turn_{turn}']['story_progress'] = intervention_record_story_progress
                        story_progress_list.append(intervention_record_story_progress)
                    else: # Director Agent: Character Reaction
                        instruction = directing_instruction + ' Interpret this instruction in a way that fits your persona. Then react accordingly.'
                        chosen_character_name, chosen_character_location = extract_chosen_character_information(directing_choice)

                        chosen_character_agent = None
                        for character_agent in character_agent_list:
                            if character_agent['name'].lower() == chosen_character_name.lower():
                                chosen_character_agent = character_agent
                                break
                        
                        if chosen_character_agent is None:
                            logger.debug(f'Error while Inferring Character Reaction: {chosen_character_name}')
                            cnt_retry += 1
                            if cnt_retry <= MAX_RESOLUTION_RETRY:
                                logger.debug(f'Retrying... count: {cnt_retry}')
                                continue
                            else:
                                logger.debug(f'Retry limit exceeded: {MAX_RESOLUTION_RETRY}. Resolve Wrong Character Choice Mode On.')
                                resolve_wrong_character_choice_mode = True
                                wrong_direct_response = direct_response
                                continue
                        
                        story_progress_tom = hide_thought_of_others(story_progress=story_progress_text, character=chosen_character_agent['name'])
                        setup_tom = remove_utility_information(setup=cleaned_setup)
                        setup_tom = remove_summarized_character_profiles(setup=setup_tom)

                        character_agent_system_prompt = CHARACTER_AGENT_SYSTEM_PROMPT.format(name=chosen_character_agent['name'])
                            
                        generate_character_reaction_prompt = GENERATE_CHARACTER_REACTION_PROMPT.format(
                            profile=chosen_character_agent['profile'],
                            character_utility=chosen_character_agent['character_utility'],
                            setup=setup_tom,
                            story_progress=story_progress_tom,
                            instruction=instruction)
                        
                        generate_character_reaction_response = run_llm(user_prompt=generate_character_reaction_prompt, system_prompt=character_agent_system_prompt, model=args.character_agent_base_model)
                        
                        character_reaction = {'name': chosen_character_agent['name'], 'location': chosen_character_location, 'reaction': generate_character_reaction_response}
                        
                        character_reaction_text = preprocess_character_reaction(character_reaction)
                        logger.debug(f'==={log_prefix} Trun {turn}===\n{character_reaction_text}')
                        turn_parent_dict[f'turn_{turn}']['story_progress'] = character_reaction_text
                        story_progress_list.append(character_reaction_text)
                
                # Update dynamic attributes every 100'th turn
                if turn % 100 == 0:
                    # Update character agents' dynamic attribute
                    updated_character_agent_list = copy.deepcopy(character_agent_list)
                    for updated_character_agent in updated_character_agent_list:
                        name = updated_character_agent['name']
                        updated_character_utility = update_character_utility(
                            setup=setup,
                            target_character_agent=updated_character_agent,
                            story_progress_list=story_progress_list,
                            args=args)
                        updated_character_agent['character_utility'] = updated_character_utility
                        logger.debug(f'===({example_id}) Turn {turn} Update utility({name})===' + updated_character_utility)
                    
                    setup = update_setup_character_utility(setup, updated_character_agent_list)
                    logger.debug(f'===({example_id}) Turn {turn} Update Setup===' + setup)
                    
                    turn_parent_dict[f'turn_{turn}']['character_agent_list'] = updated_character_agent_list
                    turn_parent_dict[f'turn_{turn}']['setup'] = setup

                save_wip_data(wip_data=data, out_dataset=out_dataset, logger=logger, args=args)
                
                cnt_retry = 0 
                resolve_wrong_character_choice_mode = False
                wrong_direct_response = ''
                
                turn += 1
            
            # After Turn Loop (Act Level)
            if args.act_seq_mode:
                act_summary_dict_parent = data['narrative'][f'part_{part}']
                if f'act_{act}' not in act_summary_dict_parent: act_summary_dict_parent[f'act_{act}'] = {}
                act_summary_dict = act_summary_dict_parent[f'act_{act}']
                if 'turn_-1' not in act_summary_dict: act_summary_dict['turn_-1'] = {}
                act_summary_dict['turn_-1']['force_quit'] = force_quit
            
            part_force_quit = force_quit

        # After Act Loop (Part Level)
        if args.plan_mode:
            data['narrative'][f'part_{part}']['turn_-1'] = {}
            data['narrative'][f'part_{part}']['turn_-1']['force_quit'] = part_force_quit
            
            # Update character agents' dynamic attribute
            updated_character_agent_list = copy.deepcopy(character_agent_list)
            for updated_character_agent in updated_character_agent_list:
                name = updated_character_agent['name']
                updated_character_utility = update_character_utility(
                    setup=setup,
                    target_character_agent=updated_character_agent,
                    story_progress_list=story_progress_list,
                    args=args)
                updated_character_agent['character_utility'] = updated_character_utility
                logger.debug(f'===({example_id}) PART {part} Update utility({name})===' + updated_character_utility)
            
            setup = update_setup_character_utility(setup, updated_character_agent_list)
            logger.debug(f'===({example_id}) PART {part} Update Setup===' + setup)
                
            data['narrative'][f'part_{part}']['turn_-1']['character_agent_list'] = updated_character_agent_list
            data['narrative'][f'part_{part}']['turn_-1']['setup'] = setup
            
            # PART Summary
            setup_without_utility = remove_utility_information(setup)
            story_progress_text_for_summary = preprocess_story_progress_list(story_progress_list)
            part_summary_prompt = PART_SUMMARY_PROMPT.format(
                part_n=part,
                setup=setup_without_utility,
                story_progress=story_progress_text_for_summary)
            part_summary_response = run_llm(user_prompt=part_summary_prompt, model=args.director_agent_base_model)
            part_summary = part_summary_response.strip()
            
            data['narrative'][f'part_{part}']['turn_-1']['part_summary'] = part_summary
            logger.debug(f'===({example_id}) PART {part} Summary===' + part_summary)
            
            save_wip_data(wip_data=data, out_dataset=out_dataset, logger=logger, args=args)

    # After Part Loop (Overall)
    if not args.plan_mode:
        data['narrative']['turn_-1'] = {}
        data['narrative']['turn_-1']['force_quit'] = part_force_quit

    return data

def main():
    
    #### setup logger ####
    log_file_path = os.path.join(os.environ['LOG_DIR'], 'generation.log')
    logger = setup_logger(__name__, log_file_path, level=logging.INFO, verbose=False)
    
    #### args ####
    args = parse_args()
    log_generation_setting(logger=logger, args=args)
    
    #### load ####
    tmas_dataset = read_jsonl(args.data_file)
    
    out_dataset = []
    if args.load_file != 'None':
        out_dataset = read_json(args.load_file)
    
    setting_dataset = []
    if args.setting_file != 'None':
        setting_dataset = read_json(args.setting_file)
    
    #### generate narrative ####
    for i, tmas_data in enumerate(tmas_dataset):
        example_id = tmas_data['example_id']
        inputs = tmas_data['inputs']

        ## Remove this annotation block to regenerate Edit Phase
        """
        if any(out_data['example_id'] == example_id and out_data['edit_state'] == 'finished' for out_data in out_dataset):
            for out_data in out_dataset:
                if out_data['example_id'] != example_id:
                    continue
                out_data['edit_state'] = 'wip'
        """
        
        if any(out_data['example_id'] == example_id and out_data['generation_state'] == 'finished' and out_data['edit_state'] == 'finished' for out_data in out_dataset):
            logger.debug(f'==={example_id} already finished... ({i+1}/{len(tmas_dataset)})===')
            continue
        
        wip_data = {'example_id': example_id, 'inputs': inputs, 'generation_state': 'wip', 'edit_state': 'wip'}
        for out_data in out_dataset:
            if out_data['example_id'] != example_id:
                continue
            wip_data = copy.deepcopy(out_data)
        
        target_setting_data = {}
        for setting_data in setting_dataset:
            if setting_data['example_id'] != example_id:
                continue
            target_setting_data = setting_data
        
        ## Initialization (Setup, Character Agents, Plan)
        if args.setting_file != 'None' and target_setting_data.get('initialization') is not None:
            wip_data['initialization'] = copy.deepcopy(target_setting_data['initialization'])
        
        if wip_data.get('initialization') is None:
            wip_data['initialization'] = {}
            
        initial_setup, initial_setup_edit_cnt = generate_initial_setup(data=wip_data, logger=logger, args=args)
        wip_data['initialization']['initial_setup'] = initial_setup
        wip_data['initialization']['initial_setup_edit_cnt'] = initial_setup_edit_cnt
        
        updated_initial_setup, character_agent_list = generate_character_agents(data=wip_data, logger=logger, args=args)
        if updated_initial_setup == False or character_agent_list == False:
            logger.error(f'({example_id}) Error while Character Agent Creation. Maybe Initial Setup format issue.')
            continue
        wip_data['initialization']['initial_setup'] = updated_initial_setup
        wip_data['initialization']['character_agent_list'] = character_agent_list
        
        save_wip_data(wip_data=wip_data, out_dataset=out_dataset, logger=logger, args=args)
        
        if args.plan_mode:
            plan = generate_plan(data=wip_data, logger=logger, args=args)
            wip_data['initialization']['plan'] = plan
            save_wip_data(wip_data=wip_data, out_dataset=out_dataset, logger=logger, args=args)
        
        if not args.plan_mode and args.act_seq_mode:
            raise Exception("No Plan to Act Seq is not implemented")
        
        wip_data = generate_narrative(data=wip_data, setting_data=target_setting_data, out_dataset=out_dataset, logger=logger, args=args)
        
        wip_data['generation_state'] = 'finished'
        save_wip_data(wip_data=wip_data, out_dataset=out_dataset, logger=logger, args=args)

        ## Edit Phase
        edit_simulated_narrative(gen_data=wip_data, out_dataset=out_dataset, logger=logger, args=args)
        wip_data['edit_state'] = 'finished'
        save_wip_data(wip_data=wip_data, out_dataset=out_dataset, logger=logger, args=args)
        
        ## Output the story
        output_story(wip_data, args)
    
if __name__ == "__main__":
    main()