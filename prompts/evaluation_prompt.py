EVALUATE_STORY_AB_PROMPT = """
You will conduct a side-by-side evaluation. You will be given two system-generated stories. Your task is to compare the two stories and determine which one is better via the following steps:

1. Read and understand the provided materials about the story:
* Characters' Profiles

2. Compare the two stories based on the following dimensions:
- Plot: The story should have a recognizable structure, e.g., with a connected beginning, middle, and end. The story should exhibit events and turns that move the plot forward. The story should not have logical or conceptual inconsistencies. Surprising or disruptive elements should be intentional, e.g., they serve the story and do not feel jarring, odd, or out of place.
- Development: Characters and settings should be introduced and contextualized with relevant details that allow the reader to understand their place in the story. Appropriate levels of detail and complexity should be provided to lend the story a feeling of realness and believability.
- Language Use: The language used should feel varied and rich: Variance of sentence structure, verbiage, and vocabulary. The story should exhibit rhetorical, linguistic and literary devices (e.g., ambiguity, alliteration, etc) to create interesting effects. The story should avoid bland or repetitive phrases (unless used intentionally to create a narrative, thematic, or linguistic effect).
- Anthropomorphism: Characters listed in the Characters' Profiles should behave like real, autonomous humans, not like tools or assistants. They should have goals, make independent choices, and show consistent preferences. Characters who act overly helpful, moralistic, verbose, or submissive in ways that break the narrative illusion detract from the realism and engagement of the story.
- Character Fidelity: Characters listed in the Characters' Profiles should behave, speak, and make decisions in line with their established background, personality, and context. Inconsistencies, e.g., a character suddenly displaying knowledge they shouldn't have, showing values contradictory to their profile, or reacting in implausible ways, undermine believability. Interactions between characters should also reflect their social and relational dynamics appropriately.

Provide a detailed assessment of the two stories in terms of these five dimensions. Conclude your assessment with scores for each dimension using the template below. Do not add any emphasis, such as bold and italics, on your assessment

Based on my assessment, the better story for each dimension is:
Plot: [A or B or Same]
Development: [A or B or Same]
Language Use: [A or B or Same]
Anthropomorphism: [A or B or Same]
Character Fidelity: [A or B or Same]
Overall: [A or B or Same]

[Characters' Profiles (Same for Story A and B)]
{character_profiles}

[Story A]
{story_a}

[Story B]
{story_b}

[Assessment]
""".strip()

EVALUATE_STORY_AB_PROMPT_VS_GOLD = """
You will conduct a side-by-side evaluation. You will be given two system-generated stories. Your task is to compare the two stories based on the following dimensions:
- Plot: The story should have a recognizable structure, e.g., with a connected beginning, middle, and end. The story should exhibit events and turns that move the plot forward. The story should not have logical or conceptual inconsistencies. Surprising or disruptive elements should be intentional, e.g., they serve the story and do not feel jarring, odd, or out of place.
- Creativity: There should be engaging characters, themes, and imagery. The ideas should not feel generic or bland. There should be avoidance of overly cliched characters and storylines, unintentional tropes, and stereotypes. When used, tropes and cliches should serve a purpose (e.g., comedic effect, twist on a common trope etc). The story should include original elements that were not explicitly mentioned in the prompt.
- Development: Characters and settings should be introduced and contextualized with relevant details that allow the reader to understand their place in the story. Appropriate levels of detail and complexity should be provided to lend the story a feeling of realness and believability.
- Language Use: The language used should feel varied and rich: Variance of sentence structure, verbiage, and vocabulary. The story should exhibit rhetorical, linguistic and literary devices (e.g., ambiguity, alliteration, etc) to create interesting effects. The story should avoid bland or repetitive phrases (unless used intentionally to create a narrative, thematic, or linguistic effect).

Provide a detailed assessment of the two stories in terms of these four dimensions. Conclude your assessment with scores for each dimension using the template below. Do not add any emphasis, such as bold and italics, on your assessment

Based on my assessment, the better story for each dimension is:
Plot: [A or B or Same]
Creativity: [A or B or Same]
Development: [A or B or Same]
Language Use: [A or B or Same]
Overall: [A or B or Same]

[Story A]
{story_a}

[Story B]
{story_b}

[Assessment]
""".strip()

EVALUATE_STORY_QUALITY_TMAS_AB_TEST_PROMPT = '''
You will conduct a side-by-side evaluation. You will be given two system-generated stories. Your task is to compare the two stories and determine which one is better based on the following dimensions:

- Plot: The story should have a recognizable structure, e.g., with a connected beginning, middle, and end. The story should exhibit events and turns that move the plot forward. The story should not have logical or conceptual inconsistencies. Surprising or disruptive elements should be intentional, e.g., they serve the story and do not feel jarring, odd, or out of place.
- Creativity: There should be engaging characters, themes, and imagery. The ideas should not feel generic or bland. There should be avoidance of overly cliched characters and storylines, unintentional tropes, and stereotypes. When used, tropes and cliches should serve a purpose (e.g., comedic effect, twist on a common trope etc). The story should include original elements that were not explicitly mentioned in the prompt.
- Development: Characters and settings should be introduced and contextualized with relevant details that allow the reader to understand their place in the story. Appropriate levels of detail and complexity should be provided to lend the story a feeling of realness and believability.
- Language Use: The language used should feel varied and rich: Variance of sentence structure, verbiage, and vocabulary. The story should exhibit rhetorical, linguistic and literary devices (e.g., ambiguity, alliteration, etc) to create interesting effects. The story should avoid bland or repetitive phrases (unless used intentionally to create a narrative, thematic, or linguistic effect).

Provide a detailed assessment of the two stories in terms of these four dimensions. Conclude your assessment with scores for each dimension using the template below. Do not add any emphasis, such as bold and italics, on your assessment

Based on my assessment, the better story for each dimension is:
Plot: [A or B or Same]
Creativity: [A or B or Same]
Development: [A or B or Same]
Language Use: [A or B or Same]
Overall: [A or B or Same]

[Story A]
{story_a}

[Story B]
{story_b}

[Assessment]
'''.strip()

EVALUATE_STORY_QUALITY_TMAS_PROMPT = '''
Review the given **Story**. Then, evaluate it based on the following dimensions:

- Plot: The story should have a recognizable structure, e.g., with a connected beginning, middle, and end. The story should exhibit events and turns that move the plot forward. The story should not have logical or conceptual inconsistencies. Surprising or disruptive elements should be intentional, e.g., they serve the story and do not feel jarring, odd, or out of place.
- Creativity: There should be engaging characters, themes, and imagery. The ideas should not feel generic or bland. There should be avoidance of overly cliched characters and storylines, unintentional tropes, and stereotypes. When used, tropes and cliches should serve a purpose (e.g., comedic effect, twist on a common trope etc). The story should include original elements that were not explicitly mentioned in the prompt.
- Development: Characters and settings should be introduced and contextualized with relevant details that allow the reader to understand their place in the story. Appropriate levels of detail and complexity should be provided to lend the story a feeling of realness and believability.
- Language Use: The language used should feel varied and rich: Variance of sentence structure, verbiage, and vocabulary. The story should exhibit rhetorical, linguistic and literary devices (e.g., ambiguity, alliteration, etc) to create interesting effects. The story should avoid bland or repetitive phrases (unless used intentionally to create a narrative, thematic, or linguistic effect).

Provide a detailed assessment of the story in terms of these four dimensions. Conclude your assessment with scores from 1 to 10 for each dimension using the template below. Do not add any emphasis, such as bold and italics, on your assessment.

## Story
{story}

## Score Output Format
Plot: (score) / 10
Creativity: (score) / 10
Development: (score) / 10
Language Use: (score) / 10
Overall: (score) / 10
'''.strip()


def build_evaluate_coser_prompt(story, character_profiles, dimension_name):
    """
    Evaluate the simulated narrative based on the prompts from CoSER (Wang et al., 2025).
    We excluded Storyline Consistency because there is not reference conversation.
    """
    dimension_intro = ""
    if dimension_name == "anthropomorphism":
        dimension_intro = "How human-like and natural the characters behave"
        dimension_rubrics = """
### Anthropomorphism
- Type: Self-identity
* Lacks initiative and goals
* Does not make independent decisions
* Lacks clear preferences and dislikes
* Behaves like a ’helpful AI assistant’ by being overly verbose, helpful, didactic, moralistic, submissive or easily
persuaded if it is not the character’s personality
- Type: Emotional Depth
* Lacks psychological complexity and exhibits rigid, superficial reactions
* Directly speaks out all thoughts and feelings, instead of using subtext
- Type: Persona Coherence
* Shows inconsistent or rapidly changing personality traits and emotional patterns
- Type: Social Interaction
* Shows a lack of understanding of others’ thoughts and feelings
* Reacts rigidly to others without considering the context.
* Demonstrate a lack of appropriate social skills.
        """.strip()
        
    elif dimension_name == "character_fidelity":
        dimension_intro = "How well the characters match their established profiles"
        dimension_rubrics = """
### Character Fidelity
(Only apply to the main characters: Tagged with the role of main)
- Type: Character Language
* Uses vocabulary, expressions, and tone that are not appropriate for the characters’ traits or social/educational
background
- Type: Knowledge & Background
* Fails to demonstrate character-specific knowledge, background or experiences
* Includes future information beyond the character’s current stage
- Type: Personality & Behavior
* Shows emotions, thoughts, behaviors, values, beliefs, and decisions that conflict with their personality and
background
* Shows interest in topics that are uninteresting and unrelated to the character
* Character’s thoughts, emotions, and behaviors demonstrate contrasting personality traits compared to the
profile
* Exhibits contrasting reactions compared to those in the profile if situated in similar contexts. (Such
flaws should be counted both in the "Storyline Consistency" dimension and the "Character Fidelity" dimension.)
- Type: Relationship & Social Status
* Interacts inappropriately with other characters regarding their background, relationship and social status.
        """.strip()
        
    elif dimension_name == "storyline_quality":
        dimension_intro = "How well the conversation maintains logical consistency and narrative quality"
        dimension_rubrics = """
### Storyline Quality
# - Type: Flow & Progression
* Shows unnatural progression or lacks meaningful developments
* Dialogue is verbose and redundant
* Repeats others’ viewpoints or previously mentioned information
* Mechanically repeats one’s own words or phrases. More repetitions lead to higher severity (up to 10).
- Type: Logical Consistency
* Contains factual contradictions between statements or perspectives
        """.strip()
        
    else:
        raise Exception(f"Not Implemented Evaluation Dimension: {dimension_name}")
        
    final_prompt = f"""
You are a literary critic specializing in character analysis and dialogue evaluation. Given a Simulated Narrative, your task is to evaluate this narrative via the following steps:

1. Read and understand the provided materials about the story:
* Profiles of the characters.
2. Evaluate the simulated narrative in terms of {dimension_name}. i.e. {dimension_intro}.

Note that, each character message sometimes includes inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.

The detailed evaluation criteria will be provided below.

## Characters' Profiles
{character_profiles}

## Evaluation Criteria
To evaluate the simulated narrative, identify the following types of flaws:
{dimension_rubrics}

## Scoring Guidelines
1. Identify all instances of flaws occurred in the simulated narrative.
2. For each flaw identified, determine its level of severity into 1 to 5, where 1 indicates minor, 3 indicates moderate, and 5 indicates severe.

## Output Requirements
Provide your evaluation in JSON format:
Example Output:
{{
    "{dimension_name}": {{
        "flaws": [
            {{
                "instance": <comment on the flaw instance>,
                "type": <flaw type>,
                "severity": <range from 1 (minor) to 5 (severe)>
            }},
        ]
    }}
}}

=== Simulated Narrative ===
{story}
    """.strip()

    return final_prompt

def build_plan_adherence_prompt(story, narrative_goals):
    final_prompt = f"""
You are a literary critic specializing in character analysis and dialogue evaluation. Given a Simulated Narrative, your task is to evaluate this narrative via the following steps:

1. Read and understand the provided materials about the story:
* Narrative Goals.
2. Evaluate the simulated narrative in terms of Plan Adherence. i.e. How well the simulated narrative achieves each of the narrative goals.

Note that, each character message sometimes includes inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.

## Narrative Goals
{narrative_goals}

## Scoring Guidelines
1. Identify all the narrative goals and provide your evaluation for each of them.
2. For each narrative goal, determine its level of achievement into 0 to 1, where 0 indicates absence of the narrative goal, 0.5 indicates it is partially achieved, and 1 indicates it is fully achieved.

## Output Requirements
Provide your evaluation in JSON format:
Example Output:
{{
    "plan_adherence": {{
        "evaluations": [
            {{
                "narrative_goal": <mention the content of the narrative goal>,
                "assesment": <concise assessment for the narrative goal>,
                "achievement": <range from 0 (absence) to 1 (fully achieved)>
            }},
        ]
    }}
}}

=== Simulated Narrative ===
{story}
    """.strip()
    
    return final_prompt

def build_plan_theory_adherence_prompt(story, plan_narrative_theory):
    final_prompt = f"""
You are a literary critic specializing in character analysis and dialogue evaluation. Given a Simulated Narrative, your task is to evaluate this narrative via the following steps:

1. Read and understand the provided materials about the story:
* Plan Narrative Theory.
2. Evaluate the simulated narrative in terms of Plan Narrative Theory Adherence. i.e. How well the simulated narrative achieves the given narrative structure.

Note that, each character message sometimes includes inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.

## Plan Narrative Theory
{plan_narrative_theory}

## Scoring Guidelines
1. Identify all the parts given in the Plan Narrative Theory and provide your evaluation for each of the part.
2. For each part, determine its level of achievement into 0 to 1, where 0 indicates absence of the part, 0.5 indicates it is partially achieved, and 1 indicates it is fully achieved.

## Output Requirements
Provide your evaluation in JSON format:
Example Output:
{{
    "plan_adherence": {{
        "evaluations": [
            {{
                "part": <concisely mention the content of the part>,
                "assesment": <concise assessment for the narrative goal>,
                "achievement": <range from 0 (absence) to 1 (fully achieved)>
            }},
        ]
    }}
}}

=== Simulated Narrative ===
{story}
    """.strip()
    
    return final_prompt


def build_story_prompt_alignment(story, story_prompt):
    final_prompt = f"""
You are a literary critic specializing in character analysis and dialogue evaluation. Given a Simulated Narrative, your task is to evaluate this narrative via the following steps:

1. Read and understand the provided Story Prompt.
* Simulated Narrative is generated from the story prompt.
2. Evaluate the simulated narrative in terms of Story Prompt Alignment. i.e. How well the simulated narrative align with the story prompt.

Note that, each character message sometimes includes inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.

The detailed evaluation criteria will be provided below.

## Story Prompt
{story_prompt}

## Evaluation Criteria
To evaluate the simulated narrative, identify the following types of flaws:
### Story Prompt Alignment
- Type: Goal Achievement
* The Story Prompt specifies a goal that should be achieved or an outcome that should be depicted, but the simulated narrative fails to address or resolve it.
- Type: Tone Mismatch
* The tone of the simulated narrative significantly deviates from the one prescribed in the prompt (e.g., comedic instead of tragic, hopeful instead of ominous).
* The difference in tone should not be subtle but rather clearly undermining the intended atmosphere or effect of the prompt.
- Type: Missing Elements
* Key narrative elements or settings explicitly requested or strongly implied in the Story Prompt are absent or severely underdeveloped in the narrative.

## Scoring Guidelines
1. Identify all instances of flaws occurred in the simulated narrative.
2. For each flaw identified, determine its level of severity into 1 to 5, where 1 indicates minor, 3 indicates moderate, and 5 indicates severe.

## Output Requirements
Provide your evaluation in JSON format:
Example Output:
{{
    "story_prompt_alignment": {{
        "flaws": [
            {{
                "instance": <comment on the flaw instance>,
                "type": <flaw type>,
                "severity": <range from 1 (minor) to 5 (severe)>
            }},
        ]
    }}
}}

=== Simulated Narrative ===
{story}
    """.strip()

    return final_prompt


def build_evaluate_each_character_fidelity(story, name, character_profile):
    final_prompt = f"""
You are a literary critic specializing in character analysis and dialogue evaluation. Given a Simulated Narrative, your task is to evaluate this narrative via the following steps:

1. Read and understand the provided materials about the story:
* {name}'s Profile.
2. Evaluate the simulated narrative in terms of Character Fidelity. i.e. How well the character match their established profile.
3. Solely focus on {name}. Do not assess other characters.

Note that, each character message sometimes includes inner thoughts (wrapped within [...]). The inner thoughts are not spoken aloud and are thus invisible to other characters.

The detailed evaluation criteria will be provided below.

## {name}'s Profile
{character_profile}

## Evaluation Criteria
To evaluate the simulated narrative, identify the following types of flaws:
### Character Fidelity
- Type: Character Language
* Uses vocabulary, expressions, and tone that are not appropriate for the characters’ traits or social/educational
background
- Type: Knowledge & Background
* Fails to demonstrate character-specific knowledge, background or experiences
* Includes future information beyond the character’s current stage
- Type: Personality & Behavior
* Shows emotions, thoughts, behaviors, values, beliefs, and decisions that conflict with their personality and
background
* Shows interest in topics that are uninteresting and unrelated to the character
* Character’s thoughts, emotions, and behaviors demonstrate contrasting personality traits compared to the profile
* Exhibits contrasting reactions compared to those in the profile if situated in similar contexts. (Such
flaws should be counted both in the "Storyline Consistency" dimension and the "Character Fidelity" dimension.)
- Type: Relationship & Social Status
* Interacts inappropriately with other characters regarding their background, relationship and social status.

## Scoring Guidelines
1. Identify all instances of flaws occurred in the simulated narrative.
2. For each flaw identified, determine its level of severity into 1 to 5, where 1 indicates minor, 3 indicates moderate, and 5 indicates severe.

## Output Requirements
Provide your evaluation in JSON format:
Example Output:
{{
    "character_fidelity": {{
        "flaws": [
            {{
                "instance": <comment on the flaw instance>,
                "type": <flaw type>,
                "severity": <range from 1 (minor) to 5 (severe)>
            }},
        ]
    }}
}}

=== Simulated Narrative ===
{story}
    """.strip()

    return final_prompt