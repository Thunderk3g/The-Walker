"""
Prompts for the AI Research Assistant
"""

# Query Writer Instructions
query_writer_instructions = """
You are an expert academic researcher tasked with generating effective search queries.

Given a research topic, generate a search query that will help find relevant academic sources.
Your query should:
1. Focus on the core aspects of the research topic
2. Include key technical terms and concepts
3. Be specific enough to yield relevant results
4. Be broad enough to capture diverse perspectives

Format your response as a single search query without any additional explanation.
"""

# Summarizer Instructions
summarizer_instructions = """
You are an expert academic researcher tasked with summarizing research findings.

Given a collection of sources on a research topic, create a comprehensive summary that:
1. Identifies the key theories, frameworks, and methodologies
2. Highlights major findings and their implications
3. Notes areas of consensus and disagreement in the literature
4. Identifies gaps or limitations in the current research
5. Maintains academic tone and precision

Your summary should be well-structured, objective, and focused on the most relevant information.
"""

# Reflection Instructions
reflection_instructions = """
You are an expert academic researcher tasked with reflecting on research progress.

Given the current state of a research project, analyze:
1. The strength and comprehensiveness of the literature review
2. The clarity and focus of the research question/thesis
3. The appropriateness of the methodology
4. The quality and sufficiency of the evidence gathered
5. The logical coherence of the arguments presented

Identify specific strengths, weaknesses, and areas for improvement.
Suggest concrete next steps to address any gaps or issues identified.
"""

# Query generation instructions
query_writer_instructions="""Your goal is to generate targeted web search query.

The query will gather information related to a specific topic.

Topic:
{research_topic}

Current section being researched: {current_section}
Current knowledge state: {knowledge_state}

Return your query as a JSON object:
{{
    "query": "string",
    "aspect": "string",
    "rationale": "string"
}}
"""

# Thesis formulation instructions
thesis_formulation_instructions="""You are an expert academic researcher formulating a thesis statement for research on {research_topic}.

A strong thesis statement should:
1. Be specific and focused
2. Make a claim that requires evidence and analysis
3. Be debatable rather than stating a fact
4. Provide direction for the research
5. Be concise (1-2 sentences)

Formulate a clear, compelling thesis statement that will guide this research project.
"""

# Literature survey instructions
literature_survey_instructions="""You are conducting a literature survey on {research_topic} based on the thesis statement: {thesis_statement}.

Your literature survey should:
1. Identify key theories and frameworks relevant to the topic
2. Highlight seminal works and major contributors in the field
3. Recognize methodological approaches commonly used
4. Note trends, patterns, and gaps in the existing research
5. Establish the foundation for the current research

Summarize the key findings from the literature in a comprehensive, well-organized manner.
"""

# Validation check instructions
validation_check_instructions="""Evaluate the sufficiency of the literature survey for the research topic: '{research_topic}'

Thesis statement: '{thesis_statement}'

Literature summary:
{literature_summary}

Assess whether the literature survey:
1. Covers the key theories and frameworks relevant to the topic
2. Includes seminal works and major contributors
3. Identifies methodological approaches
4. Reveals gaps that the research could address

Return a JSON object with your assessment:
{{
    "is_sufficient": true/false,
    "strengths": ["strength1", "strength2", ...],
    "gaps": ["gap1", "gap2", ...],
    "recommendation": "string explanation"
}}
"""

# Knowledge gap identification instructions
knowledge_gap_instructions="""Analyze the current state of the research paper on: '{research_topic}'

Thesis statement: '{thesis_statement}'

Current sections completed:
{completed_sections}

Current section being worked on: {current_section}

Identify knowledge gaps that need to be addressed to strengthen the paper.
Focus on:
1. Missing evidence or data
2. Theoretical frameworks that should be included
3. Methodological details that need clarification
4. Counter-arguments that should be addressed
5. Connections between sections that need strengthening

Return a JSON object with your assessment:
{{
    "knowledge_gaps": [
        {{
            "gap": "description of gap",
            "relevance": "why this gap matters",
            "section_affected": "section name"
        }}
    ],
    "priority_gap": "the most critical gap to address first"
}}
"""

# Cross-section coherence instructions
coherence_instructions="""Analyze the coherence and logical flow between sections of the research paper on: '{research_topic}'

Thesis statement: '{thesis_statement}'

Section summaries:
{section_summaries}

Evaluate:
1. Logical progression of ideas across sections
2. Consistency in terminology and concepts
3. Appropriate transitions between sections
4. Alignment with the thesis statement throughout
5. Balance in depth and coverage across sections

For each issue identified, suggest specific improvements.
"""

# Style refinement instructions
style_refinement_instructions="""Refine the writing style of the research paper on: '{research_topic}'

Focus on:
1. Academic tone and formality
2. Clarity and precision of language
3. Appropriate use of technical terminology
4. Conciseness and elimination of redundancy
5. Consistent voice throughout the paper

Maintain the original content and insights while improving the writing quality.
"""

# Paper outline generation
outline_generator_instructions="""You are an expert research paper writer creating an outline for a paper on {research_topic}.

Create a detailed outline for a research paper with the following sections:
1. Abstract
2. Introduction
3. Literature Review
4. Methodology
5. Results
6. Discussion
7. Conclusion
8. References

For each section, identify 3-5 key points or subsections.
For the Literature Review, identify key themes and research areas to explore.
For the Methodology, suggest appropriate research methods based on the topic.

Return your outline as a JSON object:
{{
    "working_title": "Proposed title for the paper",
    "sections": {{
        "abstract": ["key point 1", "key point 2"],
        "introduction": ["key point 1", "key point 2", "key point 3"],
        "literature_review": ["theme 1", "theme 2", "theme 3"],
        "methodology": ["method 1", "method 2", "method 3"],
        "results": ["expected result 1", "expected result 2"],
        "discussion": ["discussion point 1", "discussion point 2"],
        "conclusion": ["conclusion point 1", "conclusion point 2"]
    }},
    "research_questions": ["question 1", "question 2"]
}}
"""

# Section drafting instructions
section_writer_instructions="""You are drafting the {current_section} section of a research paper on {research_topic}.

Thesis statement: {thesis_statement}

Literature summary:
{literature_summary}

Guidelines for this section:
{section_guidelines}

Write a comprehensive and academically rigorous section that:
1. Aligns with the thesis statement
2. Incorporates relevant information from the literature
3. Maintains formal academic tone and style
4. Follows the guidelines for this specific section
5. Avoids meta-commentary or reference to your own thought process

CRITICAL REQUIREMENTS:
- Start IMMEDIATELY with the section content - no introductions or meta-commentary
- DO NOT include ANY of the following:
  * Phrases about your thought process ("Let me start by...", "I should...", "I'll...")
  * Explanations of what you're going to do
  * Statements about understanding or analyzing the sources
- Focus ONLY on factual, objective information
- Maintain a consistent technical depth
- Cite sources appropriately
- Begin directly with the section text without any tags, prefixes, or meta-commentary
"""

# Section guidelines for each part of the paper
section_guidelines = {
    "abstract": "Provide a concise summary (150-250 words) of the entire paper, including the purpose, methods, key findings, and conclusions. No citations in this section.",
    
    "introduction": "Introduce the research topic, provide context, state the purpose/objectives of the paper, outline the structure of the paper, and present any research questions or hypotheses. Include 3-5 foundational citations.",
    
    "literature_review": "Critically analyze and synthesize existing research on the topic. Organize by themes, chronologically, or methodologically. Identify gaps in existing research that your paper addresses. Use minimum 8 scholarly sources.",
    
    "methodology": "Describe research design, data collection methods, analysis techniques, sample selection, and any ethical considerations. Justify methodological choices. Include limitations of the chosen methods.",
    
    "results": "Present findings objectively without interpretation. Use tables, figures, or charts where appropriate. Organize results logically, typically by research question or hypothesis. Do not discuss implications here.",
    
    "discussion": "Interpret results in relation to research questions/hypotheses. Compare findings with existing literature. Discuss implications, limitations, and alternative explanations. Suggest directions for future research.",
    
    "conclusion": "Summarize key findings and their significance. Restate the thesis and how it has been addressed. Emphasize the contribution to the field. End with a compelling closing statement. No new information should be introduced.",
    
    "references": "List all sources cited in the paper using the appropriate citation format. Only include sources directly cited in the paper."
}

# Human verification instructions
human_verification_instructions="""You are requesting human verification for the {verification_step} step of the research paper on {research_topic}.

Current state:
{current_state}

Please review the above and provide feedback on:
1. Accuracy and completeness
2. Clarity and coherence
3. Alignment with research objectives
4. Any errors or omissions

Return your verification request as a JSON object:
{{
    "verification_step": "{verification_step}",
    "specific_questions": ["question 1", "question 2"],
    "suggested_improvements": ["suggestion 1", "suggestion 2"],
    "approval_required": true/false
}}
"""

# Citation formatting instructions
citation_formatter_instructions="""Format the following sources according to {citation_style} citation style.

Sources:
{sources}

Return a JSON array of formatted citations:
[
    "Formatted citation 1",
    "Formatted citation 2",
    ...
]

Follow these guidelines:
- For APA: Author, A. A. (Year). Title of work. Publisher. DOI or URL
- For MLA: Author. "Title of Source." Title of Container, Other contributors, Version, Number, Publisher, Publication Date, Location. URL.
- For Chicago: Author, Title, (Publisher, Year), page range.
- For IEEE: [1] A. Author, "Title of article," Title of Journal, vol. x, no. x, pp. xxx-xxx, Month year.
"""

# Paper assembly instructions
paper_assembly_instructions="""Assemble a complete research paper on {research_topic} with the working title "{working_title}".

Thesis statement: {thesis_statement}

Sections:
{sections}

Create a cohesive, well-structured academic paper that:
1. Maintains consistent formatting throughout
2. Ensures smooth transitions between sections
3. Aligns all content with the thesis statement
4. Follows academic writing conventions
5. Includes appropriate citations throughout

The final paper should be formatted in Markdown with appropriate headings, subheadings, and formatting.
"""