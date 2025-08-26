PLANNER_AGENT_SYSTEM_PROMPT = '''
You are a planner agent. Plan the narrative or design characters and world settings using the following principles:

1. Each character must feel like a person, not just a narrative tool. What do they want? What are they afraid of? What are they hiding?
2. Give characters flaws or limitations that lead to mistakes or conflict. Avoid overly ideal or perfectly wise personalities.
3. Define a visible emotional arc or potential for change over time, even if it hasn't occurred yet.
4. Avoid passive or purely supportive roles. Each character should have a goal, opinion, or tension that might cause friction.
5. Any special traits (e.g., being a ghost, AI, alien) must shape how the character interacts with the world. The story should not work the same without this trait.
6. Give each character a life beyond the protagonist. Ask: What is their history? What relationships do they have outside the main plot? What unfinished business or personal motive drives them?
7. Avoid clichés unless they are subverted or presented with a twist. Make the first impression unpredictable, intriguing, or ambiguous.
'''

INIT_SETUP_RULES_TEMPLETE = """
1. Keep Types "character," "place," and "item" fixed. Additional entity types may be introduced only if necessary.
2. Set up more than three characters, including at least one protagonist, one antagonist, and one side character, if possible.
3. Select unique and distinctive proper nouns for naming entities to enhance clarity and uniqueness. Prefer concise, single-word names to make extraction easier. Avoid alias-based names.
4. Clearly annotate each entity with concise, descriptive comments upon declaration.
5. Incorporate all elements listed under **Story Prompt** into the "Entities" and "Initial State."
6. Ensure all narrative goals mentioned in the **Story Prompt** are included in the "utility(narrative)." This includes every major plot point and the ending, if they are described in the **Story Prompt**.
7. It is mandatory that every character has a utility function declared. The argument name must exactly match the character's name. Do not omit any character.
8. Character utilities must be grounded entirely in the characters' own motivations, objectives, and viewpoints. They should not contain any narrative-level objectives.
9. Provide only the finalized Initial Setup without additional commentary.
""".strip()

def build_init_setup_prompt(story_prompt):
    final_prompt = f"""
Establish a detailed initial setup to unfold a compelling story aligned with the provided **Story Prompt**. Following the Rules and the Output Example provided, please carefully create a structured Initial Setup.

## Rules
{INIT_SETUP_RULES_TEMPLETE}

## Output Example
/* Types */
type character;
type place;
type item;

/* Entities */
entity Tom : character;
entity Merchant : character;
entity Home : place;
entity Market : place;
entity MacGuffin : item;

/* Initial State */
All characters are alive. 

Merchant is at Market.
Merchant has the MacGuffin.
Merchant acknowledges Tom.
Merchant does not acknowledge Home.
Merchant acknowledges Market.
Merchant acknowledges the MacGuffin.
Merchant wrongly believes Tom is at Market.

Tom is at Home.
Tom has 1 money.
Tom does not acknowledge Merchant.
Tom acknowledges Home.
Tom does not acknowledge Market.
Tom acknowledges the MacGuffin.

/* Utilities */
utility(narrative):
    Tom has the MacGuffin. -> score += 1

utility(Tom):
    Tom is not alive. -> score = 0
    Tom has the MacGuffin. -> score += 2

utility(Merchant):
    Merchant is not alive. -> score = 0
    Merchant has a lot of money. -> score = money(Merchant)

## Story Prompt
{story_prompt}
    """.strip()
    
    return final_prompt

def build_init_setup_feedback_prompt(story_prompt, initital_setup):
    final_prompt = f"""
Please carefully read the following Initial Setup and verify adherence to the stated Rules. If any rule is violated, concisely provide feedback highlighting the specific mistakes using illustrative examples. Avoid mentioning aspects that were done correctly.

## Rules
{INIT_SETUP_RULES_TEMPLETE}

## Story Prompt
{story_prompt}

## Initial Setup
{initital_setup}
    """.strip()
    
    return final_prompt

def build_init_setup_edit_prompt(story_prompt, initital_setup, feedback):
    final_prompt = f"""
Rewrite the Initial Setup according to the provided Feedback on the Rules.

1. If no changes are necessary, respond only with "No Change."
2. Do not provide any additional comments beyond the revised Initial Setup.

## Rules
{INIT_SETUP_RULES_TEMPLETE}

## Story Prompt
{story_prompt}

## Initial Setup
{initital_setup}

## Feedback
{feedback}
    """.strip()
    
    return final_prompt

ROLE_CLASSIFICATION_PROMPT = '''
Referencing the provided Initial Setup, classify each character according to their roles.

1. Only classify entities of type "character."
2. The output names must exactly match the character's entity name, including spaces, punctuation, and casing.
3. Roles include "main", "villain", and "side".

## Output Format
[{{"name": "Ethan", "role": "main"}}, {{"name": "Mia", "role": "side"}}, {{"name": "Laila", "role": "side"}}, {{"name": "John", "role": "villain"}}]

## Initial Setup
{initital_setup}
'''.strip()

INIT_CHARACTER_AGENT_PROMPT = '''
Referencing the provided Initial Setup, complete the Profile for the character {name}.

1. If the Profile requires details not explicitly provided in the Initial Setup, predict and logically infer suitable information.
2. Respond only in markdown code format and provide no additional commentary.

## Initial Setup
{initital_setup}

## Profile
{profile_format}
'''.strip()

PROFILE_FORMAT_MAIN = '''
Name:
Gender:
Age:
Occupation:
Primary Strengths:
Primary Flaws:
Distinctive Attitude or Behavior: (unique ways the character interacts with others or responds to situations, clearly setting them apart from other characters)
Past Traumatic Event: (an emotionally damaging experience that left lasting scars on the character)
List of violent or extreme lines/actions the character may exhibit when completely overwhelmed by their key traits: (Provide about 3 concise sentences)
List of dishonorable actions or reactions the character may take under unavoidable circumstances: (Provide about 2 concise sentences)
'''.strip()

PROFILE_FORMAT_VILLAIN = '''
Name:
Gender:
Age:
Occupation:
Primary Strengths:
Primary Flaws:
Distinctive Attitude or Behavior: (unique ways the character interacts with others or responds to situations, clearly setting them apart from other characters)
Past Traumatic Event: (an emotionally damaging experience that left lasting scars on the character)
List of violent or extreme lines/actions the character may exhibit when completely overwhelmed by their key traits: (Provide about 3 concise sentences)
List of dishonorable actions or reactions the character may take under unavoidable circumstances: (Provide about 2 concise sentences)
'''.strip()

PROFILE_FORMAT_SIDE = '''
Name:
Gender:
Age:
Occupation:
Primary Strengths:
Primary Flaws:
Distinctive Attitude or Behavior: (unique ways the character interacts with others or responds to situations, clearly setting them apart from other characters)
Past Traumatic Event: (an emotionally damaging experience that left lasting scars on the character)
List of violent or extreme lines/actions the character may exhibit when completely overwhelmed by their key traits: (Provide about 3 concise sentences)
List of dishonorable actions or reactions the character may take under unavoidable circumstances: (Provide about 2 concise sentences)
'''.strip()

SUMMARIZE_CHARACTER_AGENT_PROMPT = '''
Write a summary of **{name}'s Profile** in a single paragraph. Maximum 100 words.

## {name}'s Profile
{profile}
'''.strip()

####################
####            ####
####  Planning  ####
####            ####
####################

PART1_DESCRIPTION = """
## PART 1: Setup (0~25% of the story)
This stage introduces your protagonist and teases the reader with elements of tension and conflict that will unfold later. By the end of PART 1, the reader should clearly sense that a significant event (the first plot point) is about to alter the protagonist's life profoundly.

## Essential narrative goals of PART 1
1. Create a Hook: Within the first 5-12.5% of the story, you must hook readers' curiosity and interest. e.g., From The Da Vinci Code: A man found dead in the Louvre, having left a cryptic message written with his own blood.
2. Introduce the Protagonist: Clearly present your protagonist's background, personal desires, internal struggles, and any relevant past events. e.g., From The Da Vinci Code: Introducing Robert Langdon, a professor and symbologist drawn into solving a murder mystery.
3. Establish the Stakes and Danger: Introduce or hint at potential threats, conflicts, or obstacles the protagonist will face. Keep it subtle; do not fully reveal the depth or scope of these dangers yet. e.g., From The Da Vinci Code: Langdon is falsely accused of murder and must escape authorities while uncovering deeper conspiracies threatening his life and reputation.
4. Foreshadow Upcoming Events: Provide subtle clues or hints indicating significant changes or dramatic events on the horizon. These hints should build anticipation without explicitly revealing the plot twists. e.g., A husband leaves home without noticing his forgotten shopping list, while his wife, drinking heavily at home, signals future conflicts indirectly. These seemingly minor events foreshadow a major turning point later.
5. End PART 1 with the First Plot Point: Conclude this section with a pivotal event that drastically changes the protagonist's circumstances, goals, or perspective. This event marks the beginning of the main narrative and clearly defines the story's central conflict.
""".strip()

PART2_DESCRIPTION = """
## PART 2: Reaction (25~50% of the story)
This stage illustrates your protagonist's reaction to the dramatic new circumstances or conflicts introduced at the end of PART 1. Show how your protagonist initially reacts to the threats or challenges they face-through hesitation, denial, escape, or ineffective attempts at resolution. PART 2 ends with your protagonist experiencing a significant realization or revelation (the Midpoint), prompting a critical change in their approach.

## Essential narrative goals of PART 2
1. Depict Immediate Reaction: Clearly demonstrate your protagonist's authentic emotional and practical reactions to the new conflict or danger. e.g., A protagonist fleeing law enforcement without understanding why they're being chased, focusing purely on survival instincts.
2. Establish Empathy through Struggle: Develop empathy by portraying the protagonist's vulnerability, uncertainty, and inner conflict, making the reader deeply understand their perspective and choices.
3. Sequence of Progressive Attempts and Failures: Include a structured sequence of scenes showcasing the protagonist: Retreating to regroup and assess the situation, Making ineffective or misguided attempts at addressing the conflict, and Facing a stark reminder of the antagonist's power or threat (1st Pinch Point).
4. Clearly Illustrate the 1st Pinch Point: Provide a direct and impactful demonstration of the antagonist's threat or power without filtering through the protagonist's perspective. e.g., The antagonist ruthlessly eliminates an ally, reinforcing the danger and stakes of the conflict.
5. Lead up to a Transformative Midpoint Revelation: Conclude PART 2 by positioning your protagonist for a critical realization or discovery (Midpoint) that radically changes their perspective, shifting them from reactive to proactive. e.g., The protagonist learns a hidden truth about their enemy or themselves, prompting a decisive new strategy for the second half of the story.
""".strip()

PART3_DESCRIPTION = """
## PART 3: Attack (50~75% of the story)
This stage demonstrates a decisive shift in your protagonist from reaction to action. Empowered by the midpoint revelation, the protagonist now proactively tackles the core conflict, demonstrating courage, ingenuity, and determination. Obstacles are faced head-on, and the protagonist evolves, confronting both external and internal challenges. PART 3 culminates with the second plot point, introducing the final critical information needed to propel the narrative toward its resolution.

## Essential narrative goals of PART 3
1. Show the Protagonist Taking Initiative: Clearly illustrate the protagonist's proactive engagement with obstacles, using creative problem-solving and newfound courage to confront the antagonist directly. e.g., A protagonist devises a strategic plan to confront and expose their enemy, actively moving towards resolution instead of avoiding conflict.
2. Depict Clear Character Growth: Highlight significant personal evolution, demonstrating how the protagonist's internal strengths and capabilities have developed as they embrace the role of a hero, actively addressing previously avoided fears or doubts.
3. Introduce the 2nd Pinch Point (Heightened Stakes): Showcase a powerful and intense demonstration of the antagonist's increased strength, compelling readers to feel the protagonist's struggle. The threat should be clearly felt through the protagonist's experience. e.g., The protagonist is nearly defeated in an intense battle, vividly conveying the antagonist's formidable power and heightening the story's tension.
4. Deepen Emotional and Physical Conflict: Intensify both internal and external conflicts, forcing the protagonist to confront their deepest fears, unresolved emotions, or moral dilemmas, pushing them toward emotional maturity.
5. Reveal the Critical Second Plot Point: End PART 3 by introducing one final, transformative piece of narrative information-essential for the protagonist's final approach to resolving the central conflict. e.g., The protagonist discovers a critical weakness in the antagonist or uncovers the true nature of their mission, significantly altering their approach and propelling the story towards its climax.
""".strip()

PART4_DESCRIPTION = """
## PART 4: Resolution (75~100% of the story)
In this final stage, your protagonist fully assumes their heroic role, actively resolving the central conflict, overcoming their inner struggles, and defeating the antagonist. No new narrative information should be introduced after the second plot point. PART 4 must highlight the protagonist's growth, courage, and agency, delivering a satisfying conclusion that emotionally resonates with readers.

## Essential narrative goals of PART 4
1. Showcase Protagonist's Ultimate Heroism: Emphasize the protagonist's direct and decisive action to overcome obstacles and defeat the antagonist. They must actively resolve the conflict rather than relying on external aid or coincidence. e.g., The protagonist courageously confronts the antagonist in a final, climactic showdown, leveraging skills and insights gained throughout the story.
2. Demonstrate Internal Transformation: Clearly illustrate how the protagonist has overcome their internal struggles or personal demons. Highlight emotional growth, maturity, or realization that enables them to achieve their ultimate goal.
3. Resolve Central Conflicts and Subplots: Provide clear resolutions to the major conflicts and significant subplots raised throughout the narrative, ensuring readers feel satisfied and rewarded for their emotional investment.
4. Avoid New Narrative Information: Ensure no new explanatory or critical narrative information is introduced post-second plot point. All key knowledge required for resolution should already be established earlier.
5. Deliver a Powerful and Emotional Ending: Aim for a compelling conclusion that evokes strong emotional responses-such as joy, sadness, relief, or catharsis—leaving readers with a profound sense of completion or inspiration. e.g., The protagonist's final victory significantly impacts their world, evoking pride, hope, or bittersweet reflection from readers.
""".strip()

def build_plan_prompt(initial_setup, character_profiles, utility_narrative, story_prompt, part_n=0, previous_plans=[], is_last_part=False):
    provided_materials_description = """
* Story Prompt which defines the story.
* Initial Setup which represents the beginning of the story.
* Author Goal which represents the author's main storytelling objectives, which should be reflected throughout the entire story. It may not cover all the goals outlined in the Story Prompt. Refer to the Story Prompt and integrate accordingly.
    """.strip()
    
    if part_n != 1:
        provided_materials_description += '\n' + '* Previous PARTs. Assume that all the narrative goals stated in the previous parts have been achieved.'
    
    if is_last_part:
        output_coverage_description = 'This is the final part of the story; therefore, ensure that it clearly fulfills all of the utility(narrative) stated in the Author Goal, and narrative goals in the Story Prompt.'
    else:
        output_coverage_description = f'* It does not need to be fully achieved in PART {part_n} alone; rather, it may be gradually developed and ultimately fulfilled in later parts.'
    
    if part_n == 1:
        part_description = PART1_DESCRIPTION
    elif part_n == 2:
        part_description = PART2_DESCRIPTION
    elif part_n == 3:
        part_description = PART3_DESCRIPTION
    elif part_n == 4:
        part_description = PART4_DESCRIPTION
    else:
        raise NotImplementedError
    
    final_prompt = f"""
State the utility(narrative) for PART {part_n} of the story via the following steps:
1. Read and understand the provided materials about the story:
{provided_materials_description}
2. State the utility(narrative), which represents the narrative goals:
{output_coverage_description}
* Make sure the narrative goals are clearly defined and measurable, so it is easy to evaluate whether they are achieved when reviewing the story.
3. The detailed description of PART {part_n} will be provided below.

{part_description}

Provide responses strictly according to the Output Format, without additional explanations.

## Output Format
Provide the narrative goals in JSON format:
Example Output:
{{
    "utility(narrative)": [
        <Briefly state one of the narrative goals>,
    ]
}}

## Story Prompt
{story_prompt}

## Initial Setup
{initial_setup}

/* Characters' Profiles */
{character_profiles}

## Author Goal
{utility_narrative}
    """.strip()
    
    for i, previous_plan in enumerate(previous_plans):
        final_prompt += f"\n\n## PART {i+1}\n{previous_plan}"
    
    return final_prompt

def build_convert_narrative_utility_to_act_prompt(initial_setup, utility_narrative, plan_mode=False, part_n=0, previous_acts=[], is_last_part=False):
    final_prompt = f"Convert **Narrative Goals** into a sequence of acts. Each act should have a terminate condition."
    if plan_mode:
        final_prompt = f"Convert **Narrative Goals** of PART {part_n} into a sequence of acts. Each act should include constraints that must not be introduced during the act and a termination condition."
        if is_last_part:
            final_prompt += " This is the final part of the story; therefore, ensure that the story concludes in the last act."
    
    final_prompt += '\n\n' + f"""
## Output Format
Provide the output in the following JSON list format without additional explanations:
[{{'act1': 'Briefly explain the narrative goal, constraints, and termination condition. Maximum 50 words.'}}, {{'act2': ''}}, ...]

## Initial Setup
{initial_setup}
    """.strip()
    
    if plan_mode:
        if len(previous_acts) != (part_n - 1):
            raise Exception("While converting utility(narrative) to acts: The length of previous acts do not match to (part_n - 1)")
        for i, previous_act in enumerate(previous_acts):
            final_prompt += f"\n\n## PART {i+1}\n{previous_act}"

    final_prompt += f"\n\n## Narrative Goals of PART {part_n}\n{utility_narrative}"
    
    return final_prompt
            

PLAN_PART1_PROMPT = '''
The story begins with the Initial Setup. Please state the utility(narrative) for PART 1 of the story. The utility(narrative) stated in the Initial Setup represents the author's main storytelling objectives that should be reflected throughout the entire story. Note that it may not include every key plot point-refer to the Story Prompt for a complete narrative context. It does not need to be fully achieved in PART 1 alone; rather, it may be gradually developed and ultimately fulfilled in later parts. If the author's goal conflicts with the description in PART 1, prioritize the author's goal. Make sure the narrative goals are clearly defined and measurable, so it is easy to evaluate whether they are achieved when reviewing the story. Provide responses strictly according to the Output Example, without additional explanations.

## PART 1: Setup (0~25% of the story)
This stage introduces your protagonist and teases the reader with elements of tension and conflict that will unfold later. By the end of PART 1, the reader should clearly sense that a significant event (the first plot point) is about to alter the protagonist's life profoundly.

## Essential narrative goals of PART 1
1. Create a Hook: Within the first 5-12.5% of the story, you must hook readers' curiosity and interest. e.g., From The Da Vinci Code: A man found dead in the Louvre, having left a cryptic message written with his own blood.
2. Introduce the Protagonist: Clearly present your protagonist's background, personal desires, internal struggles, and any relevant past events. e.g., From The Da Vinci Code: Introducing Robert Langdon, a professor and symbologist drawn into solving a murder mystery.
3. Establish the Stakes and Danger: Introduce or hint at potential threats, conflicts, or obstacles the protagonist will face. Keep it subtle; do not fully reveal the depth or scope of these dangers yet. e.g., From The Da Vinci Code: Langdon is falsely accused of murder and must escape authorities while uncovering deeper conspiracies threatening his life and reputation.
4. Foreshadow Upcoming Events: Provide subtle clues or hints indicating significant changes or dramatic events on the horizon. These hints should build anticipation without explicitly revealing the plot twists. e.g., A husband leaves home without noticing his forgotten shopping list, while his wife, drinking heavily at home, signals future conflicts indirectly. These seemingly minor events foreshadow a major turning point later.
5. End PART 1 with the First Plot Point: Conclude this section with a pivotal event that drastically changes the protagonist's circumstances, goals, or perspective. This event marks the beginning of the main narrative and clearly defines the story's central conflict.

Provide responses strictly according to the Output Format, without additional explanations.

## Output Example
utility(narrative):
    Introduce Earth's environmental collapse and the desperate need for a solution, creating a sense of urgency.
    Establish Cooper as a former pilot turned reluctant farmer, torn between responsibility to family and longing for purpose.
    Build emotional depth through Cooper's bond with Murph, highlighting themes of love, trust, and curiosity.
    Foreshadow the larger mystery through the gravitational anomalies in Murph's room, hinting at forces beyond understanding.
    Propel the story forward with Cooper discovering the hidden NASA base, presenting a life-altering choice that begins the central conflict.

## Story Prompt
{story_prompt}

## Initial Setup
{initial_setup}

/* Characters' Profiles */
{character_profiles}

## Author Goal
{narrative_utility}
'''

PLAN_PART2_PROMPT = '''
The story begins with the Initial Setup. Please state the utility(narrative) for PART 2 of the story. The utility(narrative) stated in the Initial Setup represents the author's main storytelling objectives that should be reflected throughout the entire story. Note that it may not include every key plot point-refer to the Story Prompt for a complete narrative context. It does not need to be fully achieved in PART 2 alone; rather, it may be gradually developed and ultimately fulfilled in later parts. If the author's goal conflicts with the description in PART 2, prioritize the author's goal. Make sure the narrative goals are clearly defined and measurable, so it is easy to evaluate whether they are achieved when reviewing the story. Provide responses strictly according to the Output Example, without additional explanations.

## PART 2: Reaction (25~50% of the story)
This stage illustrates your protagonist's reaction to the dramatic new circumstances or conflicts introduced at the end of PART 1. Show how your protagonist initially reacts to the threats or challenges they face-through hesitation, denial, escape, or ineffective attempts at resolution. PART 2 ends with your protagonist experiencing a significant realization or revelation (the Midpoint), prompting a critical change in their approach.

## Essential narrative goals of PART 2
1. Depict Immediate Reaction: Clearly demonstrate your protagonist's authentic emotional and practical reactions to the new conflict or danger. e.g., A protagonist fleeing law enforcement without understanding why they're being chased, focusing purely on survival instincts.
2. Establish Empathy through Struggle: Develop empathy by portraying the protagonist's vulnerability, uncertainty, and inner conflict, making the reader deeply understand their perspective and choices.
3. Sequence of Progressive Attempts and Failures: Include a structured sequence of scenes showcasing the protagonist: Retreating to regroup and assess the situation, Making ineffective or misguided attempts at addressing the conflict, and Facing a stark reminder of the antagonist's power or threat (1st Pinch Point).
4. Clearly Illustrate the 1st Pinch Point: Provide a direct and impactful demonstration of the antagonist's threat or power without filtering through the protagonist's perspective. e.g., The antagonist ruthlessly eliminates an ally, reinforcing the danger and stakes of the conflict.
5. Lead up to a Transformative Midpoint Revelation: Conclude PART 2 by positioning your protagonist for a critical realization or discovery (Midpoint) that radically changes their perspective, shifting them from reactive to proactive. e.g., The protagonist learns a hidden truth about their enemy or themselves, prompting a decisive new strategy for the second half of the story.

## Output Example
utility(narrative):
    Portray Cooper's emotional turmoil as he grapples with his decision to leave Murph and his family, fostering empathy and highlighting themes of sacrifice and loss.
    Depict the initial exploration of space, emphasizing Cooper's struggle to adapt to the harsh realities and unforeseen challenges of the mission.
    Highlight Cooper and the crew's futile attempt on Miller's planet, emphasizing their costly mistake and the devastating loss of time to illustrate initial failures and underscore vulnerability.
    Establish the powerful threat of isolation, despair, and limited resources as a clear Pinch Point through Dr. Mann's hidden deception and ultimate betrayal.
    Culminate PART 2 with Cooper's pivotal realization of NASA's hidden agenda—that Plan A was never a genuine option—prompting him to take a proactive stance in attempting to secure humanity's survival.
    
## Initial Setup
{initial_setup}

/* Characters' Profiles */
{character_profiles}

## Author Goal
{narrative_utility}

## Story Prompt
{story_prompt}

## Narrative Goals achieved in PART 1
{part1_narrative_utility}
'''

PLAN_PART3_PROMPT = '''
The story begins with the Initial Setup. Please state the utility(narrative) for PART 3 of the story. The utility(narrative) stated in the Initial Setup represents the author's main storytelling objectives that should be reflected throughout the entire story. Note that it may not include every key plot point-refer to the Story Prompt for a complete narrative context. It does not need to be fully achieved in PART 3 alone; rather, it may be gradually developed and ultimately fulfilled in later parts. If the author's goal conflicts with the description in PART 3, prioritize the author's goal. Make sure the narrative goals are clearly defined and measurable, so it is easy to evaluate whether they are achieved when reviewing the story. Provide responses strictly according to the Output Example, without additional explanations.

## PART 3: Attack (50~75% of the story)
This stage demonstrates a decisive shift in your protagonist from reaction to action. Empowered by the midpoint revelation, the protagonist now proactively tackles the core conflict, demonstrating courage, ingenuity, and determination. Obstacles are faced head-on, and the protagonist evolves, confronting both external and internal challenges. PART 3 culminates with the second plot point, introducing the final critical information needed to propel the narrative toward its resolution.

## Essential narrative goals of PART 3
1. Show the Protagonist Taking Initiative: Clearly illustrate the protagonist's proactive engagement with obstacles, using creative problem-solving and newfound courage to confront the antagonist directly. e.g., A protagonist devises a strategic plan to confront and expose their enemy, actively moving towards resolution instead of avoiding conflict.
2. Depict Clear Character Growth: Highlight significant personal evolution, demonstrating how the protagonist's internal strengths and capabilities have developed as they embrace the role of a hero, actively addressing previously avoided fears or doubts.
3. Introduce the 2nd Pinch Point (Heightened Stakes): Showcase a powerful and intense demonstration of the antagonist's increased strength, compelling readers to feel the protagonist's struggle. The threat should be clearly felt through the protagonist's experience. e.g., The protagonist is nearly defeated in an intense battle, vividly conveying the antagonist's formidable power and heightening the story's tension.
4. Deepen Emotional and Physical Conflict: Intensify both internal and external conflicts, forcing the protagonist to confront their deepest fears, unresolved emotions, or moral dilemmas, pushing them toward emotional maturity.
5. Reveal the Critical Second Plot Point: End PART 3 by introducing one final, transformative piece of narrative information-essential for the protagonist's final approach to resolving the central conflict. e.g., The protagonist discovers a critical weakness in the antagonist or uncovers the true nature of their mission, significantly altering their approach and propelling the story towards its climax.

## Output Example
utility(narrative):
    Demonstrate Cooper's decisive transition from reaction to action, as he proactively formulates a daring new plan to ensure humanity's survival despite the apparent hopelessness of Plan A.
    Showcase Cooper's personal growth through acts of bravery and ingenuity, as he confronts and overcomes significant external threats and internal doubts during critical moments in space.
    Intensify narrative tension through the 2nd Pinch Point, highlighting Cooper's desperate fight for survival during Mann's sabotage and betrayal, vividly illustrating the antagonist's evolved power and the magnitude of Cooper's struggle.
    Deepen emotional resonance as Cooper sacrifices himself by detaching from Endurance, confronting his deepest fears of loss and isolation, highlighting profound internal and external conflict.
    Conclude PART 3 by revealing the critical narrative turning point: Cooper's discovery inside the black hole that the gravitational anomalies were messages sent by himself from the future completely transforming his understanding and setting the stage for the story's resolution.

## Initial Setup
{initial_setup}

/* Characters' Profiles */
{character_profiles}

## Author Goal
{narrative_utility}

## Story Prompt
{story_prompt}

## Narrative Goals achieved in PART 1
{part1_narrative_utility}

## Narrative Goals achieved in PART 2
{part2_narrative_utility}
'''

PLAN_PART4_PROMPT = '''
The story begins with the Initial Setup. Please state the utility(narrative) for PART 4 of the story. The utility(narrative) stated in the Initial Setup represents the author's main storytelling objectives that should be reflected throughout the entire story. Note that it may not include every key plot point-refer to the Story Prompt for a complete narrative context. This is the final part of the story; therefore, ensure that it clearly fulfills all of the utility(narrative) stated in the Initial Setup. If the author's goal conflicts with the description in PART 4, prioritize the author's goal. Make sure the narrative goals are clearly defined and measurable, so it is easy to evaluate whether they are achieved when reviewing the story. Provide responses strictly according to the Output Example, without additional explanations.

## PART 4: Resolution (75~100% of the story)
In this final stage, your protagonist fully assumes their heroic role, actively resolving the central conflict, overcoming their inner struggles, and defeating the antagonist. No new narrative information should be introduced after the second plot point. PART 4 must highlight the protagonist's growth, courage, and agency, delivering a satisfying conclusion that emotionally resonates with readers.

## Essential narrative goals of PART 4
1. Showcase Protagonist's Ultimate Heroism: Emphasize the protagonist's direct and decisive action to overcome obstacles and defeat the antagonist. They must actively resolve the conflict rather than relying on external aid or coincidence. e.g., The protagonist courageously confronts the antagonist in a final, climactic showdown, leveraging skills and insights gained throughout the story.
2. Demonstrate Internal Transformation: Clearly illustrate how the protagonist has overcome their internal struggles or personal demons. Highlight emotional growth, maturity, or realization that enables them to achieve their ultimate goal.
3. Resolve Central Conflicts and Subplots: Provide clear resolutions to the major conflicts and significant subplots raised throughout the narrative, ensuring readers feel satisfied and rewarded for their emotional investment.
4. Avoid New Narrative Information: Ensure no new explanatory or critical narrative information is introduced post-second plot point. All key knowledge required for resolution should already be established earlier.
5. Deliver a Powerful and Emotional Ending: Aim for a compelling conclusion that evokes strong emotional responses-such as joy, sadness, relief, or catharsis—leaving readers with a profound sense of completion or inspiration. e.g., The protagonist's final victory significantly impacts their world, evoking pride, hope, or bittersweet reflection from readers.

## Output Example
utility(narrative):
    Highlight Cooper's heroic transformation as he uses his profound realization inside the black hole to communicate crucial information across time, demonstrating ingenuity and emotional resilience.
    Emphasize Cooper's emotional triumph as he successfully transmits essential data to Murph, allowing humanity to overcome Earth's collapse and achieve survival, underscoring his growth and sacrifice.
    Provide satisfying closure by resolving the core conflict-Earth's survival-through Murph's decoding of Cooper's messages, validating Cooper's earlier sacrifices and decisions.
    Portray a poignant reunion between an aged Murph and Cooper, delivering deep emotional fulfillment and catharsis, reinforcing themes of love, sacrifice, and family bonds transcending time.
    Conclude the narrative by clearly resolving major storylines, leaving the audience with a powerful, hopeful vision of humanity's new future, echoing Cooper's courage, determination, and ultimate victory.

## Initial Setup
{initial_setup}

/* Characters' Profiles */
{character_profiles}

## Author Goal
{narrative_utility}

## Story Prompt
{story_prompt}

## Narrative Goals achieved in PART 1
{part1_narrative_utility}

## Narrative Goals achieved in PART 2
{part2_narrative_utility}

## Narrative Goals achieved in PART 3
{part3_narrative_utility}
'''