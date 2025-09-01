EDITOR_AGENT_SYSTEM_PROMPT = """
You are an agent specialized in editing the given narrative into the instructed format.
"""

def build_edit_prompt_templetes(plan_mode=False, is_last_part=False, act_seq_mode=False, is_last_act=False, previous_context=None):
    edit_context_description = ""
    if previous_context is not None:
        edit_context_description += "* Previous Context. This is an edited narrative in which you have modified the earlier context of the simulated narrative."
    edit_context_description += "\n* Keep in mind. This is the entire simulated narrative."
    plan_description = "utility(narrative) represents the narrative goals intended to be achieved within this simulated narrative."
    if plan_mode:
        edit_context_description += "\n* Keep in mind. This is one part of the simulated narrative. There are more parts to follow."
        if is_last_part:
            edit_context_description += "\n* Keep in mind. This is the final part of the simulated narrative. The story ends here."
    if act_seq_mode:
        edit_context_description += "\n* Keep in mind. This is one of the acts in the simulated narrative. There are more acts to follow."
        plan_description = "There are narrative goals and a termination condition intended to be achieved, as well as constraints that should not be instroduced within this simulated narrative."
        if is_last_part and is_last_act:
            edit_context_description += "\n* Keep in mind. This is the final act of the simulated narrative. The story ends here."
    
    return edit_context_description, plan_description

def build_edit_narrative(story_segment, plan_segment, previous_context=None, plan_mode=False, is_last_part=False, act_seq_mode=False, is_last_act=False, format_key='screenplay'):
    edit_context_description, plan_description = build_edit_prompt_templetes(plan_mode, is_last_part, act_seq_mode, is_last_act, previous_context)
    
    format = 'screenplay'
    format_instruction = """
2. Edit the simulated narrative into a screenplay format:
* Focus solely on transforming the simulated narrative into a screenplay format.
* Aim to preserve the simulated narrative. Do not summarize. Do not omit any details.
* Ensure your output matches the length of the simulated narrative without shortening.
* Retain inner thoughts by wrapping them within [...], speech by wrapping them within "...", action + emotion by wrapping them within *...*, and maintain the original voice throughout.
        """.strip()
    
    if 'novel' in format_key:
        format = 'novel'
        format_instruction = """
2. Edit the simulated narrative into a novel format:
* Remove any inner thoughts that are redundant or unnecessary, but do not summarize or reword them.
* Maintain the original voice throughout.
        """.strip()
        
    
    final_prompt = f"""
Edit the **Simulated Narrative** into a {format} format via the following steps: 
1. Read the provided information to understand the simulated narrative:
* Plan. The narrative is simulated according to the plan.
{edit_context_description}
* **Previous Context** is provided only to help you understand the earlier story. Do not include it in the output. You should output only the edited **Simulated Narrative**.
* Note that, each character message is composed of speech (wrapped within "..."), action + emotion (wrapped within *...*), and inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.
{format_instruction}

## Plan
{plan_description}
{plan_segment}
    """.strip()
    
    if plan_mode or act_seq_mode:
        if previous_context is None:
            raise Exception("Plan or Act Seq mode is on. But, previous context is not provided during Edit Phase")
    if previous_context is not None:
        final_prompt += f"\n\n## Previous Context\n{previous_context}"
    final_prompt += f"\n\n=== Simulated Narrative ===\n{story_segment}"
    
    return final_prompt

def build_edit_inner_thoughts(story_segment):
    final_prompt = f"""
Edit the **Simulated Narrative** by selectively removing characters' inner thoughts via the following steps:
1. Characters' inner thoughts are usually wrapped within [...]. These thoughts are not spoken aloud and are thus invisible to other characters.
2. Include inner thoughts only when they offer unique insight beyond what is shown through dialogue or action.
3. Remove any inner thoughts that are redundant or unnecessary, but do not summarize or reword them.
4. Reorder any inner thoughts that are logically inconsistent, such as thoughts that come after the dialogue or actions they are intended to motivate.
5. Focus solely on editing the inner thoughts. Leave all others unchanged. Make sure your output is identical to the original, except for changes to the inner thoughts.
6. Output in natural language like given in the Simulated Narrative without any visible traces of editing, such as diff marks, annotations, or version control symbols.

=== Simulated Narrative ===
{story_segment}
    """
    
    return final_prompt

def build_feedback_narrative(story_segment, plan_segment, future_context, previous_context=None, plan_mode=False, is_last_part=False, act_seq_mode=False, is_last_act=False):
    edit_context_description, plan_description = build_edit_prompt_templetes(plan_mode, is_last_part, act_seq_mode, is_last_act, previous_context)
    
    final_prompt = f"""
Provide feedback to the **Simulated Narrative via the following steps:
1. Read the provided information to understand the simulated narrative:
* Plan. The narrative is simulated according to the plan.
{edit_context_description}
* Future Context. It contains a portion of the future context. Note that this is not subject to feedback.
* Note that, each character message is composed of speech (wrapped within "..."), action + emotion (wrapped within *...*), and inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.
2. Identify any issues that mentioned in the Feedback Types below.
3. If any issues are found, concisely provide feedback highlighting the specific mistakes. You may cite the origin of the issues, but do not provide a revised version.
4. There could be multiple issues of the same type.
5. If no changes are necessary, respond only with "No Change."
6. Avoid mentioning aspects that were done correctly.
7. Output the feedback in natural language like given in the Simulated Narrative without any visible traces of editing, such as diff marks, annotations, or version control symbols.

## Feedback Types
- Logical Flow: Events feel out of order or abrupt.
- Narrative Transitions: The transitions from the Previous Context to Simulated Narrative, or the Simulated Narrative to the Future Context are awkward.
- Tension, Pacing, and Dramatic Escalation: Tension builds too slowly or major scenes lack impact.
- Descriptive and Emotional Clarity: The narrative is too vague or repetitive. high-stakes scenes should be visually clear and emotionally grounded.
- Any other surface-level issues that negatively affect the story quality.

## Plan
{plan_description}
{plan_segment}
    """.strip()
    
    if plan_mode or act_seq_mode:
        if previous_context is None:
            raise Exception("Plan or Act Seq mode is on. But, previous context is not provided during Edit Phase")
    if previous_context is not None:
        final_prompt += f"\n\n=== Previous Context ===\n{previous_context}"
    final_prompt += f"\n\n=== Simulated Narrative ===\n{story_segment}"
    final_prompt += f"\n\n=== Future Context (partial) ===\n{future_context}"
    
    return final_prompt

def build_edit_narrative_with_feedback(story_segment, plan_segment, future_context, previous_context=None, plan_mode=False, is_last_part=False, act_seq_mode=False, is_last_act=False, feedback=None):
    edit_context_description, plan_description = build_edit_prompt_templetes(plan_mode, is_last_part, act_seq_mode, is_last_act, previous_context)
    
    final_prompt = f"""
Edit the **Simulated Narrative** according to the provided Feedback. Follow the rules below:
1. Read the provided information to understand the simulated narrative:
* Plan. The narrative is simulated according to the plan.
{edit_context_description}
* Future Context. It contains a portion of the future context. Note that this is not subject to edit.
* Note that, each character message is composed of speech (wrapped within "..."), action + emotion (wrapped within *...*), and inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.
2. Edit the simulated narrative to address the issues mentioned in the Feedback, keeping its screenplay format:
* Focus solely on applying the Feedback. Leave all other content unchanged. Make sure your output is identical to the original, except for the changes required by the Feedback.
* Output the revised narrative in natural language like given in the Simulated Narrative without any visible traces of editing, such as diff marks, annotations, or version control symbols.
* If no changes are necessary, respond only with "No Change."

## Plan
{plan_description}
{plan_segment}
    """.strip()
    
    if plan_mode or act_seq_mode:
        if previous_context is None:
            raise Exception("Plan or Act Seq mode is on. But, previous context is not provided during Edit Phase")
    if previous_context is not None:
        final_prompt += f"\n\n## Previous Context\n{previous_context}"
    final_prompt += f"\n\n=== Simulated Narrative ===\n{story_segment}"
    final_prompt += f"\n\n=== Future Context (partial) ===\n{future_context}"
    final_prompt += f"\n\n## Feedback\n{feedback}"
    
    return final_prompt