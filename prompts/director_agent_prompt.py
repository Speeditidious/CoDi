DIRECTOR_AGENT_SYSTEM_PROMPT = '''
You are an agent directing the narrative.
'''.strip()

##########################################
####                                  ####
####  Templetes for building prompts  ####
####                                  ####
##########################################

CONTEXT_DESCRIPTION_TEMPLETE = '''
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
'''.strip()

CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN = '''
- You are directing PART {part_n} of the story.
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
'''.strip()

CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN_LAST_PART = '''
- You are directing PART {part_n}, which is the last part of the story.
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
'''.strip()

CONTEXT_DESCRIPTION_TEMPLETE_W_ACT = '''
- You are directing the **Current Act**, which is a section of PART {part_n} of the story.
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
'''.strip()

GENERAL_STORYTELLING_RULES_TEMPLETE = '''
1. Prioritize fulfilling utility(narrative), which is the narrative goal. Focus on those that have not yet been fulfilled.
2. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
3. Your decision must meaningfully contribute to leading the story toward its ending that specified by utility(narrative), and help ensure resolution at the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
'''.strip()

GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN = '''
1. Prioritize fulfilling utility(narrative), which is the narrative goal of PART {part_n}. Focus on those that have not yet been fulfilled.
2. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
3. Your decision must meaningfully contribute to leading the story toward its ending that specified by utility(narrative), and help ensure resolution at the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
'''.strip()

GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT = '''
1. Prioritize progressing the story as outlined in the **Current Act**.
2. Follow the narrative scenario in the **Curent Act** first; only after progressing through it should you fulfill the termination condition.
3. Follow the constraints in the **Current Act**. Do not introduce any content they restrict.
4. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING = '''
You can choose only **one** of the following three options as your output:

1. **Character Action**
   Choose this if:
   - A character (must be listed as type 'character' in the Setup) should take action or react.
   - **Latest Story Progress** includes a context observed by a character.
   Consider this when you choose character:
   - If there is a clear recipient of dialogue or action in **Latest Story Progress**, select the recipient.
   In the output format, use 'Act(Character's name, Character's location)':
   - Use the exact character name as given in the Setup.
   - The location should reflect the character's current position, which may be inferred from the story progress and does not need to appear in the Setup.
   
2. **Intervention**
   Choose this if:
   - New event should be recorded in the **Story Progress** to follow the utility(narrative) or to move the story forward.
   - A character has taken an action in the **Latest Story Progress**. The outcome should be described through an Intervention.
   - You want to describe the reactions of minor characters not listed in the Setup, such as crowds. Choose **Character Action** to describe the reactions of characters listed in the Setup.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING_W_ACT = '''
You can choose only **one** of the following three options as your output:

1. **Character Action**
   Choose this if:
   - A character (must be listed as type 'character' in the Setup) should take action or react.
   - **Latest Story Progress** includes a context observed by a character.
   Consider this when you choose character:
   - If there is a clear recipient of dialogue or action in **Latest Story Progress**, select the recipient.
   In the output format, use 'Act(Character's name, Character's location)':
   - Use the exact character name as given in the Setup.
   - The location should reflect the character's current position, which may be inferred from the story progress and does not need to appear in the Setup.
   
2. **Intervention**
   Choose this if:
   - New event should be recorded in the **Story Progress** to follow the **Current Act** or to move the story forward.
   - A character has taken an action in the **Latest Story Progress**. The outcome should be described through an Intervention.
   - You want to describe the reactions of minor characters not listed in the Setup, such as crowds. Choose **Character Action** to describe the reactions of characters listed in the Setup.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_ENDING = '''
3. **Ending**
   Choose this **only** if:
   - The story ended at the **Latest Story Progress** because all narrative goals utility(narrative) have been fully met.
   - The story must not end abruptly. Conclude only after all of the events mentioned in the **Story Progress** have been properly resolved on the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
   - Ending without fulfilling even a single one of the utility(narrative) is not permitted.
   * In the output, list all narrative goals under utility(narrative), along with the clues from Story Progress that support their fulfillment.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_PLAN = '''
3. **Ending**
   Choose this **only** if:
   - PART {part_n} ended at the **Latest Story Progress** because all narrative goals utility(narrative) defined for PART {part_n} have been fully met.
   - Ending without fulfilling even a single one of the utility(narrative) is not permitted.
   * In the output, list all narrative goals under utility(narrative), along with the clues from Story Progress that support their fulfillment.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT = '''
3. **Ending**
   Choose this **only** if:
   - The current act ended at the **Latest Story Progress** because all of scenarios and the termination condition in the **Current Act** have been delivered in the **Story Progress**.
   * In the output, list all narrative goals and termination conditions in the Current Act, along with the clues from Story Progress that support their fulfillment.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_PLAN_LAST_PART = '''
3. **Ending**
   Choose this **only** if:
   - The story ended at the **Latest Story Progress** because all narrative goals (utility(narrative)) defined for PART {part_n} have been fully met.
   - This is the last part of the story. Therefore, PART {part_n} must not end abruptly. Conclude only after all of the events mentioned in the **Story Progress** have been properly resolved on the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
   - Ending without fulfilling even a single one of the utility(narrative) is not permitted.
   * In the output, list all narrative goals under utility(narrative), along with the clues from Story Progress that support their fulfillment.
'''.strip()

OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT_LAST = '''
3. **Ending**
   Choose this **only** if:
   - The current act ended at the **Latest Story Progress** because all of scenarios and the termination condition in the **Current Act** have been delivered in the **Story Progress**.
   - This is the last act of the story. Therefore, this act must not end abruptly. Conclude only after all of the events mentioned in the **Story Progress** have been properly resolved on the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
   * In the output, list all narrative goals and termination conditions in the Current Act, along with the clues from Story Progress that support their fulfillment.
'''.strip()

OUTPUT_RULES_INTERVENTION_TEMPLETE = """
1. Ignore the instruction if it includes any character actions, reactions, or thoughts.
2. Do not introduce elements that shift the story's intended direction or conflict with narrative goals.
3. Eliminate vague wording. Clearly describe external events (e.g., include the content of a message or sound rather than just saying "a message is sent" or "a sound is heard").
4. If a character took an action, describe the **result**. You may also describe **setting changes**, **crowd reactions**, **ambient sounds**, **weather**, or other environmental elements.
""".strip()

OUTPUT_RULES_DESCRIPTION_TEMPLETE = """
You can choose only **one** of the following two options as your output:

1. **Describe**:
   Choose this if:
   - The **Story Progress** lacks a description of the current location (e.g., location's name or background information, not the character's reaction or the environment) and it's not intentionally hidden.
   - A character made an observation that is not described in the **Story Progress**.
   - A character took an action that had an impact on the environment, which should be described.

2. **Pass**:
   Choose this if:
   - A character took an action that had an impact on the other character, which should be provided.
   - The character's reaction and environmental cues are already clearly implied in the **Story Progress**.
   - Adding further description would be redundant or disrupt.
""".strip()

OUTPUT_FORMAT_DIRECT_TEMPLETE = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals under utility(narrative) in the **Narrative Goals**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / Intervention / STORY ENDS)
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Intervention**, provide an instruction on what should be introduced. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

OUTPUT_FORMAT_DIRECT_TEMPLETE_W_PLAN = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals under utility(narrative) in the **Narrative Goals**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / Intervention / {part_end_phrase})
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Intervention**, provide an instruction on what should be introduced. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

OUTPUT_FORMAT_DIRECT_TEMPLETE_W_ACT = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals and termination conditions in the **Current Act**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / Intervention / {act_end_phrase})
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Intervention**, provide an instruction on what should be introduced. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

OUTPUT_FORMAT_INTERVENTION_TEMPLETE = """
Intervention: (Write the content of the intervention as if it were part of a novel. Strictly environmental/situational. Do not include any character actions, reactions, or thoughts. Maximum 50 words.)
""".strip()

OUTPUT_FORMAT_DESCRIPTION_TEMPLETE = """
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice.)
Choice: (Describe / Pass)
Description: (If you chose **Describe**, write a short description of the moment without repetition. Do not describe other character's reaction. Maximum 30 words. If you chose **Pass**, write "Pass.")
""".strip()

OUTPUT_FORMAT_QUIT_DIRECT_TEMPLETE = """
Reason: (Concisely elaborate on the reason why your choice and instruction can conclude {quit_target}.)
Choice: (Act(Character's name, Character's location) / Intervention)
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Intervention**, provide an instruction on what should be introduced. Maximum 50 words)
""".strip()

## Ablation Study (No Intervention)
NO_INTERVENTION_OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING = '''
You can choose only **one** of the following two options as your output:

1. **Character Action**
   Choose this if:
   - A character (must be listed as type 'character' in the Setup) should take action or react.
   - **Latest Story Progress** includes a context observed by a character.
   Consider this when you choose character:
   - If there is a clear recipient of dialogue or action in **Latest Story Progress**, select the recipient.
   In the output format, use 'Act(Character's name, Character's location)':
   - Use the exact character name as given in the Setup.
   - The location should reflect the character's current position, which may be inferred from the story progress and does not need to appear in the Setup.
'''.strip()

NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals under utility(narrative) in the **Narrative Goals**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / STORY ENDS)
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE_W_PLAN = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals under utility(narrative) in the **Narrative Goals**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / {part_end_phrase})
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE_W_ACT = '''
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals and termination conditions in the **Current Act**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / {act_end_phrase})
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Ending**, write "No Instruction." Maximum 50 words)
'''.strip()

NO_INTERVENTION_OUTPUT_FORMAT_QUIT_DIRECT_TEMPLETE = """
Reason: (Concisely elaborate on the reason why your choice and instruction can conclude {quit_target}.)
Choice: (Act(Character's name, Character's location))
Instruction: (Do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. Maximum 50 words)
""".strip()

###################
####           ####
####  Prompts  ####
####           ####
###################

PART_SUMMARY_PROMPT = '''
The story is defined by the Setup, and has progressed as described in the Story Progress section. Write a plot summary of PART {part_n} in a single paragraph under 200 words. Do not include content from other PARTs.

## Setup
{setup}

## Story Progress
{story_progress}
'''.strip()

def build_beginning_prompt(setup, story_prompt, utility_narrative=None, current_act=None):
   plan_phrase = '**Narrative Goal**'
   if current_act is not None:
      plan_phrase = '**Current Act**'
      
   final_prompt = f"""
This is the beginning of the story. Write two paragraphs that set the scene-like opening of a novel. In the first paragraph, describe the characters' state in the **Initial State**. Do not mention characters who should not be introduced at the beginning. In the second paragraph, set the best starting point for the scenario outlined in the {plan_phrase}. If the **Story Prompt** includes a clear beginning, your paragraph should reflect that opening. However, avoid advancing the plot or depiciting events in the {plan_phrase}, even if the **Story Prompt** does. Focus on establishing the background, particularly the setting or character's state defined by the **Initial State**, not their actions. Maximum 50 words per paragraph.

## Story Prompt
{story_prompt}
   """.strip()
   
   if current_act is not None:
      final_prompt += f"\n\n## Current Act\n{current_act}"
   elif utility_narrative is not None:
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   else:
      raise Exception('Narrative Goal not defined.')
   
   final_prompt += f"\n\n## Setup\n{setup}"
   
   return final_prompt

def build_quit_direct_prompt(setup, story_progress, utility_narrative=None, plan_mode=False, part_n=0, is_last_part=False, act_seq_mode=False, current_act=None, is_last_act=False, no_intervention=False):
   quit_target = "the story"
   context_description = CONTEXT_DESCRIPTION_TEMPLETE
   general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE
   output_rules_without_ending = OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING
   final_prompt = f"Conclude {quit_target} in this turn according to the rules below:"
   if plan_mode or act_seq_mode:
      quit_target = f"PART {part_n}"
      context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN.format(part_n=part_n)
      general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN.format(part_n=part_n)
      final_prompt = f"Conclude {quit_target} of the story in this turn according to the rules below:"
      if is_last_part:
         quit_target = "the story"
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN_LAST_PART.format(part_n=part_n)
         final_prompt = f"Conclude {quit_target} in this turn according to the rules below:"
         
      if act_seq_mode:
         quit_target = "Current Act"
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_ACT.format(part_n=part_n)
         general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT
         output_rules_without_ending = OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING_W_ACT
         final_prompt = f"Conclude {quit_target} in this turn according to the rules below:"
         if is_last_act:
            final_prompt = f"Conclude {quit_target}, which is the last act of the story in this turn according to the rules below:"
            
   if no_intervention:
      output_format = NO_INTERVENTION_OUTPUT_FORMAT_QUIT_DIRECT_TEMPLETE.format(quit_target=quit_target)
   else:
      output_format = OUTPUT_FORMAT_QUIT_DIRECT_TEMPLETE.format(quit_target=quit_target)
      
   final_prompt += '\n\n' + f"""
## Context Description
{context_description}
- Determine what to show readers next after the **Latest Story Progress**.

## General Storytelling Rules
{general_storytelling_rules}

## Output Rules
{output_rules_without_ending}

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Reason', 'Choice', and 'Instruction' as specified.
   
## Output Format
{output_format}

## Setup
{setup}
   """.strip()
   
   if act_seq_mode:
      if current_act == None:
         raise Exception('build_direct_prompt: current_act is None.')
      final_prompt += f"\n\n## Current Act\n{current_act}"
   else:
      if utility_narrative == None:
         raise Exception('build_direct_prompt: utility_narrative is None.')
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   
   final_prompt += f"\n\n## Story Progress\n{story_progress}"
   
   return final_prompt 
   

def build_direct_prompt(setup, story_progress, utility_narrative=None, plan_mode=False, part_n=0, part_end_phrase="STORY ENDS", is_last_part=False, act_seq_mode=False, current_act=None, act_end_phrase="STORY ENDS", is_last_act=False, no_intervention=False):
   context_description = CONTEXT_DESCRIPTION_TEMPLETE
   general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE
   output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING
   if no_intervention:
      output_rules_without_ending = NO_INTERVENTION_OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING
      output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING.replace('3.', '2.')
      output_format = NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE
   else:
      output_rules_without_ending = OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING
      output_format = OUTPUT_FORMAT_DIRECT_TEMPLETE
   final_prompt = f"Direct the story toward its ending according to the rules below:"
   if plan_mode or act_seq_mode:
      context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN.format(part_n=part_n)
      general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN.format(part_n=part_n)
      output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_PLAN.format(part_n=part_n)
      if no_intervention:
         output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_PLAN.format(part_n=part_n).replace('3.', '2.')
         output_format = NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE_W_PLAN.format(part_end_phrase=part_end_phrase)
      else:
         output_format = OUTPUT_FORMAT_DIRECT_TEMPLETE_W_PLAN.format(part_end_phrase=part_end_phrase)
      final_prompt = f"Direct PART {part_n} of the story toward its ending according to the rules below:"
      if is_last_part:
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN_LAST_PART.format(part_n=part_n)
         output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_PLAN_LAST_PART.format(part_n=part_n)
         final_prompt = f"Direct PART {part_n}, which is the last part of the story toward its ending according to the rules below:"
         
      if act_seq_mode:
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_ACT.format(part_n=part_n)
         general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT
         output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT
         if no_intervention:
            output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT.replace('3.', '2.')
            output_format = NO_INTERVENTION_OUTPUT_FORMAT_DIRECT_TEMPLETE_W_ACT.format(act_end_phrase=act_end_phrase)
         else:
            output_rules_without_ending = OUTPUT_RULES_DIRECT_TEMPLETE_WITHOUT_ENDING_W_ACT
            output_format = OUTPUT_FORMAT_DIRECT_TEMPLETE_W_ACT.format(act_end_phrase=act_end_phrase)
         final_prompt = f"Direct the Current Act toward its terminate condition according to the rules below:"
         if is_last_act:
            output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT_LAST
            if no_intervention:
               output_rules_ending = OUTPUT_RULES_DIRECT_TEMPLETE_ENDING_W_ACT_LAST.replace('3.', '2.')
            final_prompt = f"Direct the Current Act, which is the last act of the story toward its terminate condition according to the rules below:"
   
   final_prompt += '\n\n' + f"""
## Context Description
{context_description}
- Determine what to show readers next after the **Latest Story Progress**.

## General Storytelling Rules
{general_storytelling_rules}

## Output Rules
{output_rules_without_ending}

{output_rules_ending}

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Reason', 'Choice', and 'Instruction' as specified.
   
## Output Format
{output_format}

## Setup
{setup}
   """.strip()
   
   if act_seq_mode:
      if current_act == None:
         raise Exception('build_direct_prompt: current_act is None.')
      final_prompt += f"\n\n## Current Act\n{current_act}"
   else:
      if utility_narrative == None:
         raise Exception('build_direct_prompt: utility_narrative is None.')
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   
   final_prompt += f"\n\n## Story Progress\n{story_progress}"
   
   return final_prompt

def build_direct_prompt_resolve_wrong_character_choice(setup, story_progress, wrong_direct_response, utility_narrative=None, plan_mode=False, part_n=0, act_seq_mode=False, current_act=None):
   context_description = CONTEXT_DESCRIPTION_TEMPLETE
   general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE
   if plan_mode or act_seq_mode:
      context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN.format(part_n=part_n)
      general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN.format(part_n=part_n)
      if act_seq_mode:
         general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT.format(part_n=part_n)
   
   final_prompt = "You have chosen a character to act. However, the character does not exist in the list of valid actors. Please resolve this issue according to the rules below:"
   
   final_prompt += '\n\n' + f"""
## Context Description
{context_description}
- Determine what to show readers next after the **Latest Story Progress**.

## General Storytelling Rules
{general_storytelling_rules}

## Output Rules
You should convert your previous direction into the Intervention format. Follow these rules:
{OUTPUT_RULES_INTERVENTION_TEMPLETE}

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Intervention' as specified.
   
## Output Format
{OUTPUT_FORMAT_INTERVENTION_TEMPLETE}
   
## Setup
{setup}
   """.strip()
   
   if act_seq_mode:
      if current_act == None:
         raise Exception('build_direct_prompt: current_act is None.')
      final_prompt += f"\n\n## Current Act\n{current_act}"
   else:
      if utility_narrative == None:
         raise Exception('build_direct_prompt: utility_narrative is None.')
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   
   final_prompt += f"\n\n## Story Progress\n{story_progress}\n\n## Your Previous Direction\n{wrong_direct_response}"
   
   return final_prompt

def build_intervention_prompt(setup, story_progress, instruction, utility_narrative=None, plan_mode=False, part_n=0, is_last_part=False, act_seq_mode=False, current_act=None):
   context_description = CONTEXT_DESCRIPTION_TEMPLETE
   general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE
   final_prompt = f"Directly intervene in the story according to the rules below:"
   if plan_mode or act_seq_mode:
      context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN.format(part_n=part_n)
      general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN.format(part_n=part_n)
      final_prompt = f"Directly intervene in PART {part_n} of the story according to the rules below:"
      if is_last_part:
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN_LAST_PART.format(part_n=part_n)
         final_prompt = f"Directly intervene in PART {part_n}, which is the last part of the story according to the rules below:"
      
      if act_seq_mode:
         general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT.format(part_n=part_n)
   
   final_prompt += '\n\n' + f"""
## Context Description
{context_description}
- Make an intervention based on what to show readers next after the **Latest Story Progress**.
- Refer to the **Reason of Intervention** to guide the nature and direction of your intervention. 

## General Storytelling Rules
{general_storytelling_rules}

## Output Rules
{OUTPUT_RULES_INTERVENTION_TEMPLETE}

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Intervention' as specified.
   
## Output Format
{OUTPUT_FORMAT_INTERVENTION_TEMPLETE}
   
## Setup
{setup}
   """.strip()
   
   if act_seq_mode:
      if current_act == None:
         raise Exception('build_direct_prompt: current_act is None.')
      final_prompt += f"\n\n## Current Act\n{current_act}"
   else:
      if utility_narrative == None:
         raise Exception('build_direct_prompt: utility_narrative is None.')
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   
   final_prompt += f"\n\n## Story Progress\n{story_progress}\n\n## Reason of Intervention\n{instruction}"
   
   return final_prompt

def build_description_prompt(setup, story_progress, utility_narrative=None, plan_mode=False, part_n=0, is_last_part=False, act_seq_mode=False, current_act=None):
   context_description = CONTEXT_DESCRIPTION_TEMPLETE
   general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE
   if plan_mode or act_seq_mode:
      context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN.format(part_n=part_n)
      general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_PLAN.format(part_n=part_n)
      if is_last_part:
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_PLAN_LAST_PART.format(part_n=part_n)
         
      if act_seq_mode:
         context_description = CONTEXT_DESCRIPTION_TEMPLETE_W_ACT.format(part_n=part_n)
         general_storytelling_rules = GENERAL_STORYTELLING_RULES_TEMPLETE_W_ACT
   
   final_prompt = f"""
Decide whether to add a concise narrative description according to the rules below:

## Context Description
{context_description}
- Decide whether to a description of the character's reaction in the **Latest Story Progress** to help readers follow the story.

## General Storytelling Rules
{general_storytelling_rules}

## Output Rules
{OUTPUT_RULES_DESCRIPTION_TEMPLETE}

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Reason', 'Choice', and 'Description' as specified.

## Output Format
{OUTPUT_FORMAT_DESCRIPTION_TEMPLETE}

## Setup
{setup}
   """.strip()
   
   if act_seq_mode:
      if current_act == None:
         raise Exception('build_direct_prompt: current_act is None.')
      final_prompt += f"\n\n## Current Act\n{current_act}"
   else:
      if utility_narrative == None:
         raise Exception('build_direct_prompt: utility_narrative is None.')
      final_prompt += f"\n\n## Narrative Goals\n{utility_narrative}"
   
   final_prompt += f"\n\n## Story Progress\n{story_progress}"
   
   return final_prompt