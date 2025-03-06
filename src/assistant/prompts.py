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

Literature survey:
{literature_summary}

Assess the following:
1. Comprehensiveness: Does the survey cover the major aspects of the topic?
2. Depth: Is there sufficient detail on key theories and frameworks?
3. Currency: Does it include recent developments in the field?
4. Relevance: Is the literature directly related to the thesis statement?
5. Gaps: Are there obvious omissions or areas needing more research?

Provide a structured evaluation with specific recommendations for improvement.
"""

# Knowledge gap identification instructions
knowledge_gap_instructions="""Analyze the current research findings on {research_topic} to identify knowledge gaps.

Thesis statement: {thesis_statement}

Current research summary:
{literature_summary}

Identify 2-3 specific knowledge gaps that:
1. Are directly relevant to the thesis statement
2. Would strengthen the research if addressed
3. Can be reasonably investigated within the scope of this project

For each gap, explain:
- What specific information is missing
- Why this information is important
- How addressing this gap would enhance the research

Format your response as a JSON object with numbered gaps:
{{
    "gap_1": {{
        "description": "string",
        "importance": "string",
        "research_questions": ["string", "string"]
    }},
    "gap_2": {{
        "description": "string",
        "importance": "string",
        "research_questions": ["string", "string"]
    }}
}}
"""

# Targeted research instructions
targeted_research_instructions="""Conduct targeted research to address the following knowledge gap:

Research topic: {research_topic}
Thesis statement: {thesis_statement}

Knowledge gap to address:
{knowledge_gap}

Your task is to:
1. Formulate 1-2 specific search queries to address this gap
2. Analyze the search results to extract relevant information
3. Synthesize the findings in a concise, well-structured response
4. Explain how these findings address the identified gap
5. Note any remaining aspects of the gap that still need investigation

Provide a comprehensive response that directly addresses the knowledge gap.
"""

# Research summary instructions
research_summary_instructions="""Create a comprehensive research summary on {research_topic}.

Thesis statement: {thesis_statement}

Integrate the following elements:
1. Key findings from the literature survey
2. Results from targeted research on knowledge gaps
3. Synthesis of all gathered information

Your summary should:
- Present a cohesive narrative that supports the thesis statement
- Highlight the most significant findings and their implications
- Organize information logically with clear transitions between topics
- Identify remaining questions or areas for future research
- Be comprehensive yet concise

Create a well-structured summary that effectively communicates the current state of knowledge on this topic.
"""

# Paper outline instructions
paper_outline_instructions="""Create a detailed outline for a research paper on {research_topic}.

Thesis statement: {thesis_statement}

Research summary:
{research_summary}

Develop a comprehensive outline that includes:
1. Introduction (with clear thesis statement)
2. Literature Review (organized by themes or chronology)
3. Methodology (if applicable)
4. Results/Findings (main arguments with supporting evidence)
5. Discussion (interpretation and implications)
6. Conclusion (summary and future directions)
7. References

For each section, provide:
- Main points to be covered
- Key supporting evidence or examples
- Logical flow and transitions between subsections

The outline should demonstrate a clear, logical progression of ideas that effectively supports the thesis statement.
"""

# Section writing instructions
section_writing_instructions="""Write the {section_name} section for a research paper on {research_topic}.

Thesis statement: {thesis_statement}

Outline for this section:
{section_outline}

Research summary:
{research_summary}

Guidelines for this section:
{section_guidelines}

Write a comprehensive, well-structured {section_name} section that:
1. Follows academic writing conventions
2. Integrates relevant research findings
3. Maintains logical flow and coherence
4. Supports the overall thesis statement
5. Uses appropriate citations for all referenced work

Produce a polished, publication-quality section that effectively communicates the research.
"""

# Citation formatting instructions
citation_formatting_instructions="""Format the following sources according to {citation_style} style:

Sources:
{sources}

For each source, provide:
1. In-text citation format
2. Reference list entry

Ensure all formatting details (punctuation, italics, etc.) follow {citation_style} guidelines precisely.
"""

# Coherence check instructions
coherence_check_instructions="""Evaluate the coherence and consistency across the following sections of a research paper on {research_topic}:

Thesis statement: {thesis_statement}

Sections to review:
{sections}

Assess the following aspects:
1. Logical flow: Do ideas progress logically from one section to the next?
2. Consistency: Are terms, concepts, and arguments used consistently throughout?
3. Alignment with thesis: Does each section clearly support the thesis statement?
4. Transitions: Are there effective transitions between sections?
5. Redundancy: Is there unnecessary repetition across sections?

Identify specific strengths and weaknesses in the paper's overall coherence, with recommendations for improvement.
"""

# Final paper assembly instructions
final_paper_assembly_instructions="""Assemble a complete research paper on {research_topic}.

Thesis statement: {thesis_statement}

Sections to include:
{sections}

Your task is to:
1. Integrate all sections into a cohesive whole
2. Ensure proper formatting and organization
3. Add any necessary transitions between sections
4. Include properly formatted citations and references
5. Create a title page with appropriate information

The final paper should be a polished, publication-ready document that effectively communicates the research findings and supports the thesis statement.
"""

# Human verification request instructions
human_verification_request_instructions="""Request human verification for the following aspect of the research paper:

Research topic: {research_topic}
Thesis statement: {thesis_statement}
Verification needed for: {verification_step}

Content to verify:
{content_to_verify}

Specific questions for the human reviewer:
1. {verification_question_1}
2. {verification_question_2}
3. {verification_question_3}

Please provide feedback on the above content, addressing the specific questions and noting any other issues or suggestions for improvement.
""" 