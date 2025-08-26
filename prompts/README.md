# Prompts

An overview of the prompts used in the **Director Agent** and **Character Agent** is provided below. Example prompts are shown in a setting *without planning*.

For the prompts of the other agents, refer to [`./planner_agent_prompt.py`](./planner_agent_prompt.py) and [`./editor_agent_prompt.py`](./editor_agent_prompt.py).

## 🎬 Director Agent

### Directing (Choosing one of Character / Intervention / Ending)
```text
Direct the story toward its ending according to the rules below:

## Context Description
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
- Determine what to show readers next after the **Latest Story Progress**.

## General Storytelling Rules
1. Prioritize fulfilling utility(narrative), which is the narrative goal. Focus on those that have not yet been fulfilled.
2. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
3. Your decision must meaningfully contribute to leading the story toward its ending that specified by utility(narrative), and help ensure resolution at the narrative level (e.g., final confrontation, consequences shown, character arcs closed).

## Output Rules
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

3. **Ending**
   Choose this **only** if:
   - The story ended at the **Latest Story Progress** because all narrative goals utility(narrative) have been fully met.
   - The story must not end abruptly. Conclude only after all of the events mentioned in the **Story Progress** have been properly resolved on the narrative level (e.g., final confrontation, consequences shown, character arcs closed).
   - Ending without fulfilling even a single one of the utility(narrative) is not permitted.
   * In the output, list all narrative goals under utility(narrative), along with the clues from Story Progress that support their fulfillment.

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Reason', 'Choice', and 'Instruction' as specified.
   
## Output Format
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice. If you choose **Ending**, list all narrative goals under utility(narrative) in the **Narrative Goals**, along with the clues from **Story Progress** and **Latest Story Progress** that support their fulfillment.)
Choice: (Act(Character's name, Character's location) / Intervention / STORY ENDS)
Instruction: (If you chose **Character Action**, do not act on the character's behalf. Instead, provide an instruction as a director without any background exposition. If you chose **Intervention**, provide an instruction on what should be introduced. If you chose **Ending**, write "No Instruction." Maximum 50 words)

## Setup
{story_world}

## Narrative Goals
{utility_narrative}

## Story Progress
{story_progress}
```

### Intervention
```text
Directly intervene in the story according to the rules below:

## Context Description
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
- Determine what to show readers next after the **Latest Story Progress**.

## General Storytelling Rules
1. Prioritize fulfilling utility(narrative), which is the narrative goal. Focus on those that have not yet been fulfilled.
2. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
3. Your decision must meaningfully contribute to leading the story toward its ending that specified by utility(narrative), and help ensure resolution at the narrative level (e.g., final confrontation, consequences shown, character arcs closed).

## Output Rules
1. Ignore the instruction if it includes any character actions, reactions, or thoughts.
2. Do not introduce elements that shift the story's intended direction or conflict with narrative goals.
3. Eliminate vague wording. Clearly describe external events (e.g., include the content of a message or sound rather than just saying "a message is sent" or "a sound is heard").
4. If a character took an action, describe the **result**. You may also describe **setting changes**, **crowd reactions**, **ambient sounds**, **weather**, or other environmental elements.

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Intervention' as specified.
   
## Output Format
Intervention: (Write the content of the intervention as if it were part of a novel. Strictly environmental/situational. Do not include any character actions, reactions, or thoughts. Maximum 50 words.)
   
## Setup
{story_world}

## Narrative Goals
{utility_narrative}

## Story Progress
{story_progress}

## Reason of Intervention
{instruction}
```

### Description
```text
Decide whether to add a concise narrative description according to the rules below:

## Context Description
- Understand the current state of the story by reviewing the **Story Progress**.
- Consider that the **Story Progress** is the only thing visible to readers.
- Determine what to show readers next after the **Latest Story Progress**.
- Decide whether to a description of the character's reaction in the **Latest Story Progress** to help readers follow the story.

## General Storytelling Rules
1. Prioritize fulfilling utility(narrative), which is the narrative goal. Focus on those that have not yet been fulfilled.
2. Avoid the same patterns in events or story progress. If it continues, try a different tactic instead of repeating it.
3. Your decision must meaningfully contribute to leading the story toward its ending that specified by utility(narrative), and help ensure resolution at the narrative level (e.g., final confrontation, consequences shown, character arcs closed).

## Output Rules
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

Provide responses strictly according to the Output Format below, without additional explanations. The output should include the word 'Reason', 'Choice', and 'Description' as specified.

## Output Format
Reason: (List the conditions, as specified in the State Output Rules, that led to your choice.)
Choice: (Describe / Pass)
Description: (If you chose **Describe**, write a short description of the moment without repetition. Do not describe other character's reaction. Maximum 30 words. If you chose **Pass**, write "Pass.")

## Setup
{story_world}

## Narrative Goals
{utility_narrative}

## Story Progress
{story_progress}

## Reason of Intervention
{instruction}
```

For more detailed prompts—such as beginning the story or terminating the simulation once the predefined maximum number of turns has been reached—refer to [`./director_agent_prompt.py`](./director_agent_prompt.py).

## 🎭 Character Agent

### Reaction Generation
```text
React to the **Latest Story Progress** according to the rules below:

## Context Description
- Understand the current State of the story by reviewing the **Story Progress**.
- The director has indicated that it is now your turn to act. Instructions are provided in the **Instruction** section.
- Based on this, determine how you would react to the **Latest Story Progress**.

## General Acting Rules
1. Prioritize reacting according to your **Profile** and **Goals and Desires**, even over the director's instructions. Focus on your own goals, desires, emotions, and likes and dislikes.
2. Describe what you observed, if it is not already described in the **Story Progress**. What you do will be recorded in the **Story Progress**.
3. Try not to repeat the same or a similar reaction as in the last sentence of **Story Progress**.

## Output Rules
1. Your response should include a mix of:
   - **Thought**: [your thought] (always required)
   - **Action/Emotion**: *your action + emotion* (optional)
   - **Speech**: "your speech" (optional)
2. Always include [your thought]. Add either *action/emotion*, "speech", or both—whichever fits naturally.
3. If the given **Instruction** contains observations not recorded in the **Story Progress**, describe them accordingly.
4. Keep it concise: One clear moment of reaction (thought + one emotional or verbal response). Limit to 100 words max.

Provide responses strictly according to the Output Example below, without additional explanations.

## Output Example
[I should spill the beer glass to show my clumsiness.] *surprised, puts down the beer glass quickly* "Oh no...!"

## Setup
{story_world}

### Your Profile
{profile}

### Your Goals and Desires
{character_utility}

## Story Progress
{story_progress}

## Instruction
{director_instruction}
```

### Utility Update
```text
Update utility({name}), which indicates your goals and desires, via the following steps:
1. Read and understand the provided materials:
* Story Progress indicates the current state.
* {name}'s Profile to understand {name}.
2. Reconstruct the utility({name}) to include all your goals and desires:
* Each utility must be grounded entirely in your own motivations, objectives, and viewpoints.
* They should not contain any narrative-level objectives.
3. The response format must remain the same as the original, including the phrase utility({name}):

## Output Format
Provide the reconstructed utility({name}) in JSON format:
Example Output:
{{
    "utility({name})": [
        <Briefly state one of your goals and desires>,
    ]
}}

## {name}'s Profile
{profile}

## {name}'s Current Goals and Desires
{character_utility}

## Story Progress
{story_progress}
```