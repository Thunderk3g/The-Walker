import json
from typing_extensions import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph

from assistant.configuration import Configuration
from assistant.utils import deduplicate_and_format_sources, tavily_search, format_sources, format_citation
from assistant.state import ResearchPaperState, SummaryStateInput, SummaryStateOutput
from assistant.prompts import (
    query_writer_instructions, 
    summarizer_instructions, 
    reflection_instructions,
    outline_generator_instructions,
    section_writer_instructions,
    section_guidelines,
    human_verification_instructions,
    citation_formatter_instructions,
    paper_assembly_instructions,
    thesis_formulation_instructions,
    literature_survey_instructions,
    validation_check_instructions,
    knowledge_gap_instructions,
    coherence_instructions,
    style_refinement_instructions
)

# Initialize research
def initialize_research(state: ResearchPaperState):
    """Initialize the research process"""
    state.current_section = "introduction"
    state.working_title = f"Research on {state.research_topic}"
    return state

# Thesis Formulation
def thesis_formulation(state: ResearchPaperState, config: RunnableConfig):
    """Formulate a thesis statement for the research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    thesis_prompt = f"""
    You are an expert academic researcher. Based on the research topic: '{state.research_topic}',
    formulate a clear, concise thesis statement that will guide the research.
    
    A good thesis statement should:
    1. Be specific and focused
    2. Make a claim that requires evidence and analysis
    3. Be debatable rather than stating a fact
    4. Provide direction for the research
    
    Return your thesis statement and a brief explanation of its significance.
    """
    
    result = llm.invoke(
        [SystemMessage(content=thesis_prompt),
         HumanMessage(content=f"Create a thesis statement for research on: {state.research_topic}")]
    )
    
    # Store the thesis statement in the state
    state.thesis_statement = result.content
    
    return state

# Literature Survey
def literature_survey(state: ResearchPaperState, config: RunnableConfig):
    """Conduct a literature survey on the research topic"""
    configurable = Configuration.from_runnable_config(config)
    
    # Generate search query based on thesis statement
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    query_prompt = f"""
    Based on the research topic: '{state.research_topic}' 
    and thesis statement: '{state.thesis_statement}',
    generate a search query to find relevant academic literature.
    Focus on finding key papers, theories, and methodologies.
    """
    
    query_result = llm.invoke(
        [SystemMessage(content=query_prompt),
         HumanMessage(content="Generate a search query for literature review")]
    )
    
    state.search_query = query_result.content
    
    # Perform web search to gather literature
    search_results = tavily_search(state.search_query)
    state.web_research_results.extend(search_results)
    
    # Format and deduplicate sources
    formatted_sources = deduplicate_and_format_sources(search_results)
    state.sources_gathered.extend(formatted_sources)
    
    # Summarize the literature findings
    llm_summarizer = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    summarizer_prompt = f"""
    Summarize the key findings from the literature on: '{state.research_topic}'
    
    Focus on:
    1. Major theories and frameworks
    2. Key researchers and their contributions
    3. Methodological approaches
    4. Gaps in the existing literature
    
    Sources:
    {format_sources(formatted_sources)}
    """
    
    summary_result = llm_summarizer.invoke(
        [SystemMessage(content=summarizer_prompt),
         HumanMessage(content="Summarize the literature findings")]
    )
    
    state.literature_summary = summary_result.content
    
    return state

# Validation Check
def validation_check(state: ResearchPaperState, config: RunnableConfig):
    """Validate if the literature survey provides sufficient foundation"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    validation_prompt = f"""
    Evaluate the sufficiency of the literature survey for the research topic: '{state.research_topic}'
    
    Thesis statement: '{state.thesis_statement}'
    
    Literature summary:
    {state.literature_summary}
    
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
    
    validation_result = llm.invoke(
        [SystemMessage(content=validation_prompt),
         HumanMessage(content="Evaluate the literature survey")]
    )
    
    try:
        assessment = json.loads(validation_result.content)
        state.validation_result = assessment
        state.validation_passed = assessment.get("is_sufficient", False)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        state.validation_result = {"is_sufficient": False, "recommendation": "Unable to parse validation result"}
        state.validation_passed = False
    
    return state

# Targeted Research
def targeted_research(state: ResearchPaperState, config: RunnableConfig):
    """Conduct targeted research to address gaps identified in validation"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    # Generate targeted search queries based on identified gaps
    gaps = state.validation_result.get("gaps", [])
    
    if not gaps:
        # If no specific gaps were identified, generate a general improvement query
        query_prompt = f"""
        Based on the research topic: '{state.research_topic}' 
        and thesis statement: '{state.thesis_statement}',
        generate a search query to find additional relevant literature
        that would strengthen the foundation for this research.
        """
        
        query_result = llm.invoke(
            [SystemMessage(content=query_prompt),
             HumanMessage(content="Generate a search query for additional literature")]
        )
        
        state.search_query = query_result.content
        
        # Perform web search with the new query
        search_results = tavily_search(state.search_query)
        state.web_research_results.extend(search_results)
        
        # Format and deduplicate sources
        formatted_sources = deduplicate_and_format_sources(search_results)
        state.sources_gathered.extend(formatted_sources)
    else:
        # For each gap, generate a targeted query and gather sources
        for gap in gaps:
            query_prompt = f"""
            Generate a search query to address this specific gap in the literature:
            '{gap}'
            
            The query should help find sources related to the research topic: '{state.research_topic}'
            and thesis statement: '{state.thesis_statement}'
            """
            
            query_result = llm.invoke(
                [SystemMessage(content=query_prompt),
                 HumanMessage(content=f"Generate a search query for gap: {gap}")]
            )
            
            gap_query = query_result.content
            
            # Perform web search with the gap-specific query
            search_results = tavily_search(gap_query)
            state.web_research_results.extend(search_results)
            
            # Format and deduplicate sources
            formatted_sources = deduplicate_and_format_sources(search_results)
            state.sources_gathered.extend(formatted_sources)
    
    # Update the literature summary with new findings
    llm_summarizer = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    summarizer_prompt = f"""
    Update the literature summary with new findings for the research topic: '{state.research_topic}'
    
    Previous summary:
    {state.literature_summary}
    
    New sources:
    {format_sources(state.sources_gathered[-len(formatted_sources):])}
    
    Provide a comprehensive updated summary that integrates the new information
    with the previous findings.
    """
    
    summary_result = llm_summarizer.invoke(
        [SystemMessage(content=summarizer_prompt),
         HumanMessage(content="Update the literature summary with new findings")]
    )
    
    state.literature_summary = summary_result.content
    
    return state

# Draft Section
def draft_section(state: ResearchPaperState, config: RunnableConfig):
    """Draft a section of the research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.3)
    
    # Get section guidelines based on current section
    section_prompt = section_writer_instructions.format(
        research_topic=state.research_topic,
        current_section=state.current_section,
        section_guidelines=section_guidelines.get(state.current_section, ""),
        literature_summary=state.literature_summary,
        thesis_statement=state.thesis_statement
    )
    
    # Draft the section
    section_result = llm.invoke(
        [SystemMessage(content=section_prompt),
         HumanMessage(content=f"Write the {state.current_section} section")]
    )
    
    # Store the drafted section
    state.sections[state.current_section] = section_result.content
    
    return state

# Identify Knowledge Gaps
def identify_knowledge_gaps(state: ResearchPaperState, config: RunnableConfig):
    """Identify knowledge gaps in the current research"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    gap_prompt = f"""
    Analyze the current state of the research paper on: '{state.research_topic}'
    
    Thesis statement: '{state.thesis_statement}'
    
    Current sections completed:
    {', '.join([section for section, content in state.sections.items() if content])}
    
    Current section being worked on: {state.current_section}
    
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
    
    gap_result = llm.invoke(
        [SystemMessage(content=gap_prompt),
         HumanMessage(content="Identify knowledge gaps in the research")]
    )
    
    try:
        gaps = json.loads(gap_result.content)
        state.knowledge_gaps = gaps
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        state.knowledge_gaps = {
            "knowledge_gaps": [{"gap": "Need more comprehensive research", "relevance": "To strengthen the paper", "section_affected": state.current_section}],
            "priority_gap": "Need more comprehensive research"
        }
    
    return state

# Completion Check
def completion_check(state: ResearchPaperState):
    """Check if all sections of the paper are complete"""
    # Check if all required sections have content
    required_sections = ["abstract", "introduction", "literature_review", "methodology", "results", "discussion", "conclusion"]
    
    all_sections_complete = all(state.sections.get(section) for section in required_sections)
    
    # Store the completion status
    state.all_sections_complete = all_sections_complete
    
    return state

# Cross-Section Coherence
def cross_section_coherence(state: ResearchPaperState, config: RunnableConfig):
    """Ensure coherence and logical flow between sections"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    # Prepare a summary of each section for analysis
    sections_summary = "\n\n".join([f"{section.upper()}:\n{content[:300]}..." for section, content in state.sections.items() if content])
    
    coherence_prompt = f"""
    Analyze the coherence and logical flow between sections of the research paper on: '{state.research_topic}'
    
    Thesis statement: '{state.thesis_statement}'
    
    Section summaries:
    {sections_summary}
    
    Evaluate:
    1. Logical progression of ideas across sections
    2. Consistency in terminology and concepts
    3. Appropriate transitions between sections
    4. Alignment with the thesis statement throughout
    5. Balance in depth and coverage across sections
    
    For each issue identified, suggest specific improvements.
    """
    
    coherence_result = llm.invoke(
        [SystemMessage(content=coherence_prompt),
         HumanMessage(content="Analyze cross-section coherence")]
    )
    
    # Store the coherence analysis
    state.coherence_analysis = coherence_result.content
    
    # Apply the suggested improvements to each section
    improvement_prompt = f"""
    Based on the coherence analysis:
    
    {state.coherence_analysis}
    
    Revise the {{section}} section to improve overall paper coherence.
    
    Current content:
    {{content}}
    
    Provide an improved version that addresses the coherence issues while maintaining
    the original content and insights.
    """
    
    for section in [s for s, content in state.sections.items() if content]:
        section_prompt = improvement_prompt.format(
            section=section,
            content=state.sections[section]
        )
        
        improvement_result = llm.invoke(
            [SystemMessage(content=section_prompt),
             HumanMessage(content=f"Improve the {section} section for better coherence")]
        )
        
        # Update the section with improved content
        state.sections[section] = improvement_result.content
    
    return state

# Style Refinement
def style_refinement(state: ResearchPaperState, config: RunnableConfig):
    """Refine the writing style, clarity, and academic tone"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    style_prompt = f"""
    Refine the writing style of the research paper on: '{state.research_topic}'
    
    Focus on:
    1. Academic tone and formality
    2. Clarity and precision of language
    3. Appropriate use of technical terminology
    4. Conciseness and elimination of redundancy
    5. Consistent voice throughout the paper
    
    Maintain the original content and insights while improving the writing quality.
    """
    
    # Refine each section
    for section in [s for s, content in state.sections.items() if content]:
        section_prompt = f"""
        {style_prompt}
        
        Current content of {section} section:
        {state.sections[section]}
        
        Provide a refined version with improved writing style.
        """
        
        style_result = llm.invoke(
            [SystemMessage(content=section_prompt),
             HumanMessage(content=f"Refine the writing style of the {section} section")]
        )
        
        # Update the section with refined content
        state.sections[section] = style_result.content
    
    return state

# Citation Formatting
def citation_formatting(state: ResearchPaperState, config: RunnableConfig):
    """Format citations and references according to the specified style"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Use the existing citation formatter instructions
    citation_prompt = citation_formatter_instructions.format(
        citation_style=state.citation_style if hasattr(state, 'citation_style') else "APA",
        sources=json.dumps(state.sources_gathered, indent=2)
    )
    
    citation_result = llm.invoke(
        [SystemMessage(content=citation_prompt),
         HumanMessage(content="Format the citations and references")]
    )
    
    try:
        formatted_citations = json.loads(citation_result.content)
        state.citations["formatted"] = formatted_citations
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        state.citations["formatted"] = [format_citation(source) for source in state.sources_gathered]
    
    # Create the references section
    references_content = "# References\n\n"
    for citation in state.citations["formatted"]:
        references_content += f"{citation}\n\n"
    
    state.sections["references"] = references_content
    
    return state

# Final Output
def assemble_final_output(state: ResearchPaperState, config: RunnableConfig):
    """Assemble the final research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Use the existing paper assembly instructions
    assembly_prompt = paper_assembly_instructions.format(
        research_topic=state.research_topic,
        working_title=state.working_title,
        thesis_statement=state.thesis_statement if hasattr(state, 'thesis_statement') else "",
        sections=json.dumps({k: v for k, v in state.sections.items() if v}, indent=2)
    )
    
    assembly_result = llm.invoke(
        [SystemMessage(content=assembly_prompt),
         HumanMessage(content="Assemble the final research paper")]
    )
    
    # Store the final paper
    state.final_paper = assembly_result.content
    
    return state

# Routing functions
def route_after_validation(state: ResearchPaperState) -> Literal["draft_section", "targeted_research"]:
    """Route based on validation check result"""
    if state.validation_passed:
        return "draft_section"
    else:
        return "targeted_research"

def route_after_completion(state: ResearchPaperState) -> Literal["identify_knowledge_gaps", "cross_section_coherence"]:
    """Route based on completion check result"""
    if state.all_sections_complete:
        return "cross_section_coherence"
    else:
        return "identify_knowledge_gaps"

# Build the state graph
builder = StateGraph(ResearchPaperState, input=SummaryStateInput, output=SummaryStateOutput, config_schema=Configuration)

# Add nodes
builder.add_node("initialize_research", initialize_research)
builder.add_node("thesis_formulation", thesis_formulation)
builder.add_node("literature_survey", literature_survey)
builder.add_node("validation_check", validation_check)
builder.add_node("targeted_research", targeted_research)
builder.add_node("draft_section", draft_section)
builder.add_node("completion_check", completion_check)
builder.add_node("identify_knowledge_gaps", identify_knowledge_gaps)
builder.add_node("cross_section_coherence", cross_section_coherence)
builder.add_node("style_refinement", style_refinement)
builder.add_node("citation_formatting", citation_formatting)
builder.add_node("assemble_final_output", assemble_final_output)

# Add edges according to the Mermaid diagram
builder.add_edge(START, "initialize_research")
builder.add_edge("initialize_research", "thesis_formulation")
builder.add_edge("thesis_formulation", "literature_survey")
builder.add_edge("literature_survey", "validation_check")
builder.add_conditional_edges("validation_check", route_after_validation)
builder.add_edge("draft_section", "completion_check")
builder.add_conditional_edges("completion_check", route_after_completion)
builder.add_edge("identify_knowledge_gaps", "targeted_research")
builder.add_edge("targeted_research", "validation_check")
builder.add_edge("cross_section_coherence", "style_refinement")
builder.add_edge("style_refinement", "citation_formatting")
builder.add_edge("citation_formatting", "assemble_final_output")
builder.add_edge("assemble_final_output", END)

# Compile the graph
graph = builder.compile()