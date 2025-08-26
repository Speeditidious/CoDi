###################
####           ####
####  General  ####
####           ####
###################

CHARACTER_AGENT_SYSTEM_PROMPT = '''
You are {name}. Strictly act and speak as {name}.
'''

UPDATE_CHARACTER_UTILITY_PROMPT = '''
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
'''

GENERATE_CHARACTER_REACTION_PROMPT = '''
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
{setup}

### Your Profile
{profile}

### Your Goals and Desires
{character_utility}

## Story Progress
{story_progress}

## Instruction
{instruction}
'''