import tiktoken

from global_utils import *
from generation_utils import *
from character_agent_utils import remove_and_extract_utility_information
from director_agent_utils import remove_initial_state_information, remove_utility_information
from prompts.director_agent_prompt import PART_SUMMARY_PROMPT
from prompts.editor_agent_prompt import *

EDITOR_AGENT_TEMP = 0.4
NO_FUTURE_CONTEXT_SENTENCE = "No Future Context. The story ends in the Simulated Narrative."

def split_story_by_chunks(story, max_tokens=1024, min_tokens_last_chunk=256):
    
    enc = tiktoken.encoding_for_model('gpt-4o')
    
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    lines = story.splitlines()
    for line in lines:
        tokens = len(enc.encode(line))
        if current_tokens + tokens > max_tokens:
            chunks.append('\n'.join(current_chunk).strip())
            current_chunk = [line]
            current_tokens = tokens
        else:
            current_chunk.append(line)
            current_tokens += tokens
    
    if current_chunk:
        if len(enc.encode('\n'.join(current_chunk))) < min_tokens_last_chunk and chunks:
            chunks[-1] += '\n' + '\n'.join(current_chunk)
        else:
            chunks.append('\n'.join(current_chunk).strip())

    return chunks

def build_previous_context_editor(edit_data, format_key, logger, args):
    previous_context_list = []

    current_part = 1
    while edit_data.get(f'part_{current_part+1}') is not None:
        current_part += 1
    
    for part in range(current_part-2):
        previous_context_list.append(f'### PART {part+1} summary')
        previous_context_list.append(edit_data[f'part_{part+1}']['part_summary'])
    
    if current_part >= 2:
        previous_context_list.append(f'### PART {current_part-1}')
        
        if args.act_seq_mode:
            act_storytelling = 1
            while edit_data.get(f'part_{current_part-1}', {}).get(f'act_{act_storytelling}') is not None:
                previous_context_list.append(edit_data[f'part_{current_part-1}'][f'act_{act_storytelling}'][format_key])
                previous_context_list.append('')
                act_storytelling += 1
        else:
            previous_context_list.append(edit_data[f'part_{current_part-1}'][format_key])
    
    return '\n'.join(previous_context_list).strip()

def build_future_context_editor(gen_data, logger, args, part=0, act=0):
    future_context_list = []
    
    MAX_FUTURE_CONTEXT_TURN = 10
    if args.plan_mode and args.act_seq_mode:
        part_storytelling = part
        act_storytelling = act + 1
        while len(future_context_list) < MAX_FUTURE_CONTEXT_TURN and gen_data['narrative'].get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is not None:
            turn_storytelling = 1
            while len(future_context_list) < MAX_FUTURE_CONTEXT_TURN and gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'].get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                turn_narrative = gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                if 'ENDS' in turn_narrative:
                    break
                if args.hierarchical_mode:
                    for t in turn_narrative.splitlines():
                        if t.strip() == '':
                            continue
                        future_context_list.append(t.strip())
                        if len(future_context_list) >= MAX_FUTURE_CONTEXT_TURN * 2:
                            break
                elif args.one_man_show_mode:
                    future_context_list.extend([t.strip() for t in turn_narrative.splitlines() if t.strip() != ''])
                else:
                    future_context_list.append(turn_narrative)
                turn_storytelling += 1
            act_storytelling += 1
            if gen_data['narrative'].get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}') is None:
                part_storytelling += 1
                act_storytelling = 1
    elif args.plan_mode:
        part_storytelling = part + 1
        while len(future_context_list) < MAX_FUTURE_CONTEXT_TURN and gen_data['narrative'].get(f'part_{part_storytelling}') is not None:
            turn_storytelling = 1
            while len(future_context_list) < MAX_FUTURE_CONTEXT_TURN and gen_data['narrative'][f'part_{part_storytelling}'].get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                turn_narrative = gen_data['narrative'][f'part_{part_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                if 'ENDS' in turn_narrative:
                    break
                if args.hierarchical_mode:
                    for t in turn_narrative.splitlines():
                        if t.strip() == '':
                            continue
                        future_context_list.append(t.strip())
                        if len(future_context_list) >= MAX_FUTURE_CONTEXT_TURN * 2:
                            break
                elif args.one_man_show_mode:
                    future_context_list.extend([t.strip() for t in turn_narrative.splitlines() if t.strip() != ''])
                else:
                    future_context_list.append(turn_narrative)
                turn_storytelling += 1
            part_storytelling += 1
    
    if len(future_context_list) <= 0:
        return NO_FUTURE_CONTEXT_SENTENCE
    else:
        return '\n'.join(future_context_list)

def build_story_progress_for_part_summary_editor(edit_data, format_key):
    story_progress_list = []
    
    summary_part = 1
    while edit_data.get(f'part_{summary_part+1}') is not None:
        summary_part += 1
        
    part_storytelling = 1
    while edit_data.get(f'part_{part_storytelling}') is not None:
        if part_storytelling <= (summary_part-2):
            story_progress_list.append(f'### PART {part_storytelling} summary')
            story_progress_list.append(edit_data[f'part_{part_storytelling}']['part_summary'])
        else:
            story_progress_list.append(f'### PART {part_storytelling}')
            
            act_storytelling = 1
            while edit_data.get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}', {}).get(format_key) is not None:
                act_story = edit_data[f'part_{part_storytelling}'][f'act_{act_storytelling}'][format_key]
                if act_story != '':
                    story_progress_list.append(act_story)
                    story_progress_list.append('')
                act_storytelling += 1
                
            if act_storytelling == 1:
                story_progress_list.append(edit_data[f'part_{part_storytelling}'][format_key])
        
        part_storytelling += 1
    
    return '\n'.join(story_progress_list).strip()

def preprocess_edited_narrative(edited_narrative):
    ## Remove html tags
    edited_narrative = re.sub(r"</?[^>]+>", "", edited_narrative)
    
    ## Remove unnecessary lines
    ignore_keywords = ['PART', 'ACT', 'SCENE', 'START', 'END', 'STARTS', 'ENDS']
    preprocessed_narrative = '\n'.join([s.strip() for s in edited_narrative.splitlines() if all(k not in s for k in ignore_keywords)])
    
    return preprocessed_narrative.strip()

def edit_simulated_narrative(gen_data, out_dataset, logger, args):
    """ Edit the simulated narrative in the form of screenplay
    """
    
    logger.info(f"({gen_data['example_id']}) Editing the simulated narrative...")
    
    if args.reformat_novel:
        format_key = 'story_progress_novel'
    else:
        format_key = 'story_progress_screenplay'

    ## Regenerate Edit Phase
    gen_data['edited_narrative'] = {}

    if gen_data.get('edited_narrative') is None:
        gen_data['edited_narrative'] = {}
    
    example_id = gen_data['example_id']
    
    if args.plan_mode and args.act_seq_mode:
        
        plan = gen_data['initialization']['plan']
        
        last_part = 1
        while plan.get(f'part_{last_part+1}') is not None:
            last_part += 1
        
        part_storytelling = 1
        while gen_data.get('narrative', {}).get(f'part_{part_storytelling}') is not None:
            ## Pass if already edited part
            if gen_data['edited_narrative'].get(f'part_{part_storytelling}', {}).get('part_summary') is not None:
                part_storytelling += 1
                continue
            
            ## Edit
            if gen_data['edited_narrative'].get(f'part_{part_storytelling}') is None:
                gen_data['edited_narrative'][f'part_{part_storytelling}'] = {}
            act_sequence = [list(act.values())[0] for act in plan[f'part_{part_storytelling}_act_seq']]
            
            act_storytelling = 1
            while gen_data.get('narrative', {}).get(f'part_{part_storytelling}').get(f'act_{act_storytelling}') is not None:
                if gen_data['edited_narrative'].get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}', {}).get('story_progress') is not None:
                    act_storytelling += 1
                    continue
                
                gen_data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'] = {}
                is_last_act = ((act_storytelling >= len(act_sequence)))
                
                act_story_list = []
                turn_storytelling = 1
                while gen_data.get('narrative', {}).get(f'part_{part_storytelling}', {}).get(f'act_{act_storytelling}').get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                    story_segment = gen_data['narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                    act_story_list.append(story_segment)
                    turn_storytelling += 1
                act_story = '\n'.join(act_story_list)
                
                if len(act_story_list) <= 1 and not args.hierarchical_mode:
                    gen_data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}']['story_progress'] = ''
                    gen_data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}']['story_progress_before_feedback'] = ''
                    act_storytelling += 1
                    continue
                
                if part_storytelling == 1 and act_storytelling == 1:
                    previous_context = "The simulated narrative is the start of the story."
                else:
                    previous_context = build_previous_context_editor(gen_data['edited_narrative'], format_key, logger, args)
                    
                future_context = build_future_context_editor(gen_data, logger, args, part=part_storytelling, act=act_storytelling)
                
                edit_narrative_prompt = build_edit_narrative(
                    previous_context=previous_context,
                    story_segment=act_story,
                    plan_segment=list(plan[f'part_{part_storytelling}_act_seq'][act_storytelling-1].values())[0],
                    plan_mode=True,
                    act_seq_mode=True,
                    is_last_part=(part_storytelling >= last_part),
                    is_last_act=is_last_act,
                    format_key=format_key
                )
                edited_narrative_response = run_llm(user_prompt=edit_narrative_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
                edited_narrative = preprocess_edited_narrative(edited_narrative_response)
                
                logger.debug(f"===({example_id}) Edited PART {part_storytelling} Act {act_storytelling}===\n{edited_narrative}")
                
                edit_inner_thoughts_prompt = build_edit_inner_thoughts(edited_narrative)
                edited_inner_thoughts_response = run_llm(user_prompt=edit_inner_thoughts_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
                edited_narrative = preprocess_edited_narrative(edited_inner_thoughts_response)
                
                logger.debug(f"===({example_id}) Edited PART {part_storytelling} Act {act_storytelling} (inner thoughts edit)===\n{edited_narrative}")
                
                gen_data['edited_narrative'][f'part_{part_storytelling}'][f'act_{act_storytelling}'][format_key] = edited_narrative
                
                save_wip_data(wip_data=gen_data, out_dataset=out_dataset, logger=logger, args=args)
                
                act_storytelling += 1
                
            ## Summary
            character_agent_list = gen_data['narrative'][f'part_{part_storytelling}']['turn_-1']['character_agent_list']
            setup = gen_data['narrative'][f'part_{part_storytelling}']['turn_-1']['setup']
            cleaned_setup = remove_initial_state_information(setup)
            cleaned_setup = remove_utility_information(cleaned_setup)
            cleaned_setup = preprocess_setup(cleaned_setup)
            cleaned_setup = add_summarized_profiles(cleaned_setup, character_agent_list)
            
            story_progress = build_story_progress_for_part_summary_editor(gen_data['edited_narrative'], format_key)
            part_summary_prompt = PART_SUMMARY_PROMPT.format(
                part_n=part_storytelling,
                setup=cleaned_setup,
                story_progress=story_progress
            )
            
            part_summary_response = run_llm(user_prompt=part_summary_prompt, model=args.editor_agent_base_model)
            part_summary = part_summary_response.strip()
            
            gen_data['edited_narrative'][f'part_{part_storytelling}']['part_summary'] = part_summary
            
            logger.debug(f"===({example_id}) PART {part_storytelling} Summary===\n{part_summary}")
            
            save_wip_data(wip_data=gen_data, out_dataset=out_dataset, logger=logger, args=args)
            
            part_storytelling += 1
            
        return gen_data
            
    elif args.plan_mode:
        
        plan = gen_data['initialization']['plan']
        
        last_part = 1
        while plan.get(f'part_{last_part+1}') is not None:
            last_part += 1
        
        part_storytelling = 1
        while gen_data.get('narrative', {}).get(f'part_{part_storytelling}') is not None:
            ## Pass if already edited part
            if gen_data['edited_narrative'].get(f'part_{part_storytelling}', {}).get('part_summary') is not None:
                part_storytelling += 1
                continue
            
            ## Edit
            gen_data['edited_narrative'][f'part_{part_storytelling}'] = {}
            part_story_list = []
            part_story_list.append(f'### PART {part_storytelling}')
            turn_storytelling = 1
            while gen_data.get('narrative', {}).get(f'part_{part_storytelling}', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
                story_segment = gen_data['narrative'][f'part_{part_storytelling}'][f'turn_{turn_storytelling}']['story_progress']
                part_story_list.append(story_segment)
                turn_storytelling += 1
            part_story = '\n'.join(part_story_list)
            
            if len(part_story_list) < 1:
                gen_data['edited_narrative'][f'part_{part_storytelling}']['story_progress_before_feedback'] = ''
                gen_data['edited_narrative'][f'part_{part_storytelling}']['part_summary'] = ''
                continue
            
            ## story length exceeds the output token length -> split to chunks
            story_chunks = split_story_by_chunks(part_story)
            
            edited_chunks = []
            for i, chunk in enumerate(story_chunks):
                ## Previous chunk exists -> Use the previous chunk as the previous context
                if i > 0:
                    previous_context = edited_chunks[i-1]
                ## Otherwise, Use default previous context
                else:
                    if part_storytelling == 1:
                        previous_context = "The simulated narrative is the start of the story."
                    else:
                        previous_context = build_previous_context_editor(gen_data['edited_narrative'], format_key, logger, args)
                
                ## Next chunk exists -> Use the next chunk as the future context
                if i+1 < len(story_chunks):
                    future_context = story_chunks[i+1]
                ## Otherwise, Use default future context
                else:
                    future_context = build_future_context_editor(gen_data, logger, args, part=part_storytelling)
                    
            
                edit_narrative_prompt = build_edit_narrative(
                    previous_context=previous_context,
                    story_segment=chunk,
                    plan_segment=plan[f'part_{part_storytelling}'],
                    plan_mode=True,
                    is_last_part=(part_storytelling >= last_part),
                    format_key=format_key
                )
            
                edited_narrative_response = run_llm(user_prompt=edit_narrative_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
                edited_narrative = preprocess_edited_narrative(edited_narrative_response)
                
                logger.debug(f"===({example_id}) Edited PART {part_storytelling} ({i+1}'s chunk)===\n{edited_narrative}")
                
                edit_inner_thoughts_prompt = build_edit_inner_thoughts(edited_narrative)
                edited_inner_thoughts_response = run_llm(user_prompt=edit_inner_thoughts_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
                edited_narrative = preprocess_edited_narrative(edited_inner_thoughts_response)
                
                logger.debug(f"===({example_id}) Edited PART {part_storytelling} (inner thoughts edit) ({i+1}'s chunk)===\n{edited_narrative}")
                
                edited_chunks.append(edited_narrative)
            
            gen_data['edited_narrative'][f'part_{part_storytelling}'][format_key] = "\n\n".join(edited_chunks)
            gen_data['edited_narrative'][f'part_{part_storytelling}']['chunk_num'] = len(story_chunks)
            
            ## Summary
            character_agent_list = gen_data['narrative'][f'part_{part_storytelling}']['turn_-1']['character_agent_list']
            setup = gen_data['narrative'][f'part_{part_storytelling}']['turn_-1']['setup']
            cleaned_setup = remove_initial_state_information(setup)
            cleaned_setup = remove_utility_information(cleaned_setup)
            cleaned_setup = preprocess_setup(cleaned_setup)
            cleaned_setup = add_summarized_profiles(cleaned_setup, character_agent_list)
            
            story_progress = build_story_progress_for_part_summary_editor(gen_data['edited_narrative'], format_key)
            part_summary_prompt = PART_SUMMARY_PROMPT.format(
                part_n=part_storytelling,
                setup=cleaned_setup,
                story_progress=story_progress
            )
            part_summary_response = run_llm(user_prompt=part_summary_prompt, model=args.editor_agent_base_model)
            part_summary = part_summary_response.strip()
            
            gen_data['edited_narrative'][f'part_{part_storytelling}']['part_summary'] = part_summary
            
            logger.debug(f"===({example_id}) PART {part_storytelling} Summary===\n{part_summary}")
            
            save_wip_data(wip_data=gen_data, out_dataset=out_dataset, logger=logger, args=args)
            
            part_storytelling += 1
        
        return gen_data
    
    elif args.act_seq_mode:
        
        raise NotImplementedError
    
    else:
        ## Pass if already edited
        if gen_data['edited_narrative'].get(format_key) is not None:
            return gen_data
        
        setup = gen_data['initialization']['initial_setup']
        cleaned_setup = remove_initial_state_information(setup=setup)
        cleaned_setup, utility_narrative = remove_and_extract_utility_information(setup=cleaned_setup, character='narrative')
        
        ## Edit
        story = ''
        turn_storytelling = 1
        while gen_data.get('narrative', {}).get(f'turn_{turn_storytelling}', {}).get('story_progress') is not None:
            story_segment = gen_data['narrative'][f'turn_{turn_storytelling}']['story_progress']
            story += story_segment + '\n'
            turn_storytelling += 1
        story = story.strip()
        
        ## story length exceeds the output token length -> split to chunks
        story_chunks = split_story_by_chunks(story)
        
        edited_chunks = []
        for i, chunk in enumerate(story_chunks):
            ## Previous chunk exists -> Use the previous chunk as the previous context
            if i > 0:
                previous_context = edited_chunks[i-1]
            ## Otherwise, None
            else:
                previous_context = None
        
            ## Next chunk exists -> Use the next chunk as the future context
            if i+1 < len(story_chunks):
                future_context = story_chunks[i+1]
            ## Otherwise, no future context
            else:
                future_context = build_future_context_editor(gen_data, logger, args)

            edit_narrative_prompt = build_edit_narrative(
                previous_context=previous_context,
                story_segment=chunk,
                plan_segment=utility_narrative,
                format_key=format_key
            )
            
            edited_narrative_response = run_llm(user_prompt=edit_narrative_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
            edited_narrative = preprocess_edited_narrative(edited_narrative_response)
            
            logger.debug(f"===({example_id}) Edited Narrative ({i+1}'s chunk)===\n{edited_narrative}")
            
            edit_inner_thoughts_prompt = build_edit_inner_thoughts(edited_narrative)
            edited_inner_thoughts_response = run_llm(user_prompt=edit_inner_thoughts_prompt, system_prompt=EDITOR_AGENT_SYSTEM_PROMPT, model=args.editor_agent_base_model, temperature=EDITOR_AGENT_TEMP)
            edited_narrative = preprocess_edited_narrative(edited_inner_thoughts_response)
            
            logger.debug(f"===({example_id}) Edited Narrative (inner thoughts edit) ({i+1}'s chunk)===\n{edited_narrative}")
            
            edited_chunks.append(edited_narrative)
        
        gen_data['edited_narrative'][format_key] = "\n\n".join(edited_chunks)
        gen_data['edited_narrative']['chunk_num'] = len(story_chunks)
        
        save_wip_data(wip_data=gen_data, out_dataset=out_dataset, logger=logger, args=args)
        
        return gen_data