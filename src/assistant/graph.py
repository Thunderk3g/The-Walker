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
    thesis_formulation_instructions,
    literature_survey_instructions,
    validation_check_instructions,
    knowledge_gap_instructions,
    targeted_research_instructions,
    research_summary_instructions,
    paper_outline_instructions,
    section_writing_instructions,
    citation_formatting_instructions,
    coherence_check_instructions,
    final_paper_assembly_instructions,
    human_verification_request_instructions
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
    
    # Format the prompt using the template
    prompt = thesis_formulation_instructions.format(
        research_topic=state.research_topic
    )
    
    # Generate thesis statement
    messages = [
        SystemMessage(content="You are an expert academic researcher."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    thesis_statement = response.content.strip()
    
    # Update state
    state.thesis_statement = thesis_statement
    
    return state

# Literature Survey
def literature_survey(state: ResearchPaperState, config: RunnableConfig):
    """Conduct a literature survey on the research topic"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=configurable.temperature)
    
    # Generate search query
    query_prompt = query_writer_instructions.format(
        research_topic=state.research_topic,
        current_section="literature_review",
        knowledge_state="Initial research phase"
    )
    
    messages = [
        SystemMessage(content="You are a research assistant."),
        HumanMessage(content=query_prompt)
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Parse the JSON response
        query_data = json.loads(response.content)
        search_query = query_data.get("query", f"literature review {state.research_topic}")
    except:
        # Fallback if JSON parsing fails
        search_query = f"literature review {state.research_topic}"
    
    # Update state
    state.search_query = search_query
    
    # Perform web search
    search_results = tavily_search(search_query, include_raw_content=True, max_results=5)
    
    # Format and deduplicate sources
    formatted_sources = deduplicate_and_format_sources(search_results)
    
    # Update state with search results
    state.web_research_results.append(search_results)
    state.sources_gathered.append(formatted_sources)
    
    # Generate literature survey
    survey_prompt = literature_survey_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement
    )
    
    messages = [
        SystemMessage(content="You are an expert academic researcher."),
        HumanMessage(content=f"{survey_prompt}\n\nSources:\n{formatted_sources}")
    ]
    
    response = llm.invoke(messages)
    literature_summary = response.content.strip()
    
    # Update state
    state.literature_summary = literature_summary
    state.research_loop_count += 1
    
    return state

# Validation Check
def validation_check(state: ResearchPaperState, config: RunnableConfig):
    """Validate the literature survey"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Format the prompt
    prompt = validation_check_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        literature_summary=state.literature_summary
    )
    
    messages = [
        SystemMessage(content="You are a research validation expert."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    validation_result = response.content.strip()
    
    # Simple heuristic to determine if validation passed
    validation_passed = "sufficient" in validation_result.lower() and "comprehensive" in validation_result.lower()
    
    # Update state
    state.validation_result = {
        "result": validation_result,
        "passed": validation_passed
    }
    state.validation_passed = validation_passed
    
    return state

# Identify Knowledge Gaps
def identify_knowledge_gaps(state: ResearchPaperState, config: RunnableConfig):
    """Identify knowledge gaps in the research"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.2)
    
    # Format the prompt
    prompt = knowledge_gap_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        literature_summary=state.literature_summary
    )
    
    messages = [
        SystemMessage(content="You are a research gap analysis expert."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Parse the JSON response
        gaps = json.loads(response.content)
    except:
        # Fallback if JSON parsing fails
        gaps = {
            "gap_1": {
                "description": "Unable to parse knowledge gaps",
                "importance": "N/A",
                "research_questions": ["What additional information is needed?"]
            }
        }
    
    # Update state
    state.knowledge_gaps = gaps
    
    return state

# Targeted Research
def targeted_research(state: ResearchPaperState, config: RunnableConfig):
    """Conduct targeted research to address knowledge gaps"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=configurable.temperature)
    
    # Get the first knowledge gap
    if not state.knowledge_gaps:
        return state
    
    first_gap_key = list(state.knowledge_gaps.keys())[0]
    knowledge_gap = state.knowledge_gaps[first_gap_key]
    
    # Format the gap as text
    gap_text = f"Gap: {knowledge_gap.get('description', 'Unknown gap')}\n"
    gap_text += f"Importance: {knowledge_gap.get('importance', 'Unknown importance')}\n"
    gap_text += "Research questions:\n"
    for question in knowledge_gap.get('research_questions', []):
        gap_text += f"- {question}\n"
    
    # Generate search query for the gap
    query_prompt = query_writer_instructions.format(
        research_topic=state.research_topic,
        current_section="targeted_research",
        knowledge_state=f"Addressing knowledge gap: {knowledge_gap.get('description', 'Unknown gap')}"
    )
    
    messages = [
        SystemMessage(content="You are a research assistant."),
        HumanMessage(content=query_prompt)
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Parse the JSON response
        query_data = json.loads(response.content)
        search_query = query_data.get("query", f"research {knowledge_gap.get('description', state.research_topic)}")
    except:
        # Fallback if JSON parsing fails
        search_query = f"research {knowledge_gap.get('description', state.research_topic)}"
    
    # Perform web search
    search_results = tavily_search(search_query, include_raw_content=True, max_results=3)
    
    # Format and deduplicate sources
    formatted_sources = deduplicate_and_format_sources(search_results)
    
    # Update state with search results
    state.web_research_results.append(search_results)
    state.sources_gathered.append(formatted_sources)
    
    # Generate targeted research summary
    research_prompt = targeted_research_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        knowledge_gap=gap_text
    )
    
    messages = [
        SystemMessage(content="You are an expert academic researcher."),
        HumanMessage(content=f"{research_prompt}\n\nSources:\n{formatted_sources}")
    ]
    
    response = llm.invoke(messages)
    targeted_research_summary = response.content.strip()
    
    # Update literature summary with new findings
    updated_summary = f"{state.literature_summary}\n\nAdditional Research on {knowledge_gap.get('description', 'Knowledge Gap')}:\n{targeted_research_summary}"
    state.literature_summary = updated_summary
    
    # Remove the addressed gap
    if first_gap_key in state.knowledge_gaps:
        del state.knowledge_gaps[first_gap_key]
    
    return state

# Generate Research Summary
def generate_research_summary(state: ResearchPaperState, config: RunnableConfig):
    """Generate a comprehensive research summary"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=configurable.temperature)
    
    # Format the prompt
    prompt = research_summary_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement
    )
    
    messages = [
        SystemMessage(content="You are an expert academic researcher."),
        HumanMessage(content=f"{prompt}\n\nLiterature Summary:\n{state.literature_summary}")
    ]
    
    response = llm.invoke(messages)
    research_summary = response.content.strip()
    
    # Update state
    state.running_summary = research_summary
    
    return state

# Generate Paper Outline
def generate_paper_outline(state: ResearchPaperState, config: RunnableConfig):
    """Generate an outline for the research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=configurable.temperature)
    
    # Format the prompt
    prompt = paper_outline_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        research_summary=state.running_summary
    )
    
    messages = [
        SystemMessage(content="You are an expert academic writer."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    outline_text = response.content.strip()
    
    # Parse the outline into sections
    sections = {}
    current_section = None
    section_content = []
    
    for line in outline_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check if this is a main section header
        if line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or \
           line.startswith('4.') or line.startswith('5.') or line.startswith('6.') or \
           line.startswith('7.'):
            # Save the previous section if it exists
            if current_section and section_content:
                sections[current_section] = section_content
            
            # Extract the section name
            parts = line.split('.', 1)
            if len(parts) > 1:
                section_name = parts[1].strip().lower().replace(' ', '_')
                current_section = section_name
                section_content = [line]
        elif current_section:
            section_content.append(line)
    
    # Save the last section
    if current_section and section_content:
        sections[current_section] = section_content
    
    # Update state
    state.outline = sections
    
    return state

# Draft Section
def draft_section(state: ResearchPaperState, config: RunnableConfig):
    """Draft a section of the research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=configurable.temperature)
    
    # Get the current section to work on
    current_section = state.current_section
    
    # Get the outline for this section
    section_outline = "\n".join(state.outline.get(current_section, []))
    
    # Format the prompt
    prompt = section_writing_instructions.format(
        section_name=current_section,
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        section_outline=section_outline,
        research_summary=state.running_summary,
        section_guidelines=f"Write a comprehensive {current_section} section."
    )
    
    messages = [
        SystemMessage(content="You are an expert academic writer."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    section_content = response.content.strip()
    
    # Update state
    state.sections[current_section] = section_content
    
    # Mark section as completed
    if current_section not in state.completed_sections:
        state.completed_sections.append(current_section)
    
    # Move to the next section
    section_order = ['abstract', 'introduction', 'literature_review', 'methodology', 
                     'results', 'discussion', 'conclusion', 'references']
    
    try:
        current_index = section_order.index(current_section)
        next_index = current_index + 1
        if next_index < len(section_order):
            state.current_section = section_order[next_index]
    except ValueError:
        # If current section is not in the standard order, default to the next one
        state.current_section = 'conclusion'
    
    return state

# Completion Check
def completion_check(state: ResearchPaperState):
    """Check if all sections are complete"""
    required_sections = ['abstract', 'introduction', 'literature_review', 'conclusion', 'references']
    completed_required = all(section in state.completed_sections for section in required_sections)
    
    # Update state
    state.all_sections_complete = completed_required
    
    return state

# Cross-Section Coherence
def cross_section_coherence(state: ResearchPaperState, config: RunnableConfig):
    """Check coherence across sections"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Prepare sections for review
    sections_text = ""
    for section_name, content in state.sections.items():
        if content:
            sections_text += f"## {section_name.upper()}\n{content}\n\n"
    
    # Format the prompt
    prompt = coherence_check_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        sections=sections_text
    )
    
    messages = [
        SystemMessage(content="You are an expert academic editor."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    coherence_analysis = response.content.strip()
    
    # Update state
    state.coherence_analysis = coherence_analysis
    
    return state

# Citation Formatting
def citation_formatting(state: ResearchPaperState, config: RunnableConfig):
    """Format citations according to the specified style"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Extract sources from web research results
    sources = []
    for result in state.web_research_results:
        if isinstance(result, dict) and 'results' in result:
            sources.extend(result['results'])
    
    # Format sources as text
    sources_text = format_sources(sources)
    
    # Format the prompt
    prompt = citation_formatting_instructions.format(
        citation_style=state.citation_style,
        sources=sources_text
    )
    
    messages = [
        SystemMessage(content="You are an expert in academic citations."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    formatted_citations = response.content.strip()
    
    # Update state
    state.citations['formatted'] = formatted_citations
    state.citations['sources'] = sources
    
    # Update references section
    state.sections['references'] = formatted_citations
    
    return state

# Assemble Final Output
def assemble_final_output(state: ResearchPaperState, config: RunnableConfig):
    """Assemble the final research paper"""
    configurable = Configuration.from_runnable_config(config)
    llm = ChatOllama(model=configurable.local_llm, temperature=0.1)
    
    # Prepare sections for assembly
    sections_text = ""
    for section_name, content in state.sections.items():
        if content:
            sections_text += f"## {section_name.upper()}\n{content}\n\n"
    
    # Format the prompt
    prompt = final_paper_assembly_instructions.format(
        research_topic=state.research_topic,
        thesis_statement=state.thesis_statement,
        sections=sections_text
    )
    
    messages = [
        SystemMessage(content="You are an expert academic editor."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    final_paper = response.content.strip()
    
    # Update state
    state.final_paper = final_paper
    
    return state

# Routing Functions
def route_after_validation(state: ResearchPaperState) -> Literal["draft_section", "targeted_research"]:
    """Route after validation check"""
    if state.validation_passed:
        return "draft_section"
    else:
        return "targeted_research"

def route_after_completion(state: ResearchPaperState) -> Literal["identify_knowledge_gaps", "cross_section_coherence"]:
    """Route after completion check"""
    if state.all_sections_complete:
        return "cross_section_coherence"
    else:
        return "identify_knowledge_gaps"

def route_after_knowledge_gaps(state: ResearchPaperState) -> Literal["targeted_research", "generate_research_summary"]:
    """Route after identifying knowledge gaps"""
    if state.knowledge_gaps and len(state.knowledge_gaps) > 0:
        return "targeted_research"
    else:
        return "generate_research_summary"

# Build the graph
def build_graph():
    """Build the research assistant graph"""
    # Create a new graph
    builder = StateGraph(ResearchPaperState)
    
    # Add nodes
    builder.add_node("initialize_research", initialize_research)
    builder.add_node("thesis_formulation", thesis_formulation)
    builder.add_node("literature_survey", literature_survey)
    builder.add_node("validation_check", validation_check)
    builder.add_node("identify_knowledge_gaps", identify_knowledge_gaps)
    builder.add_node("targeted_research", targeted_research)
    builder.add_node("generate_research_summary", generate_research_summary)
    builder.add_node("generate_paper_outline", generate_paper_outline)
    builder.add_node("draft_section", draft_section)
    builder.add_node("completion_check", completion_check)
    builder.add_node("cross_section_coherence", cross_section_coherence)
    builder.add_node("citation_formatting", citation_formatting)
    builder.add_node("assemble_final_output", assemble_final_output)
    
    # Add edges
    builder.add_edge(START, "initialize_research")
    builder.add_edge("initialize_research", "thesis_formulation")
    builder.add_edge("thesis_formulation", "literature_survey")
    builder.add_edge("literature_survey", "validation_check")
    
    # Conditional routing after validation
    builder.add_conditional_edges(
        "validation_check",
        route_after_validation,
        {
            "draft_section": "draft_section",
            "targeted_research": "identify_knowledge_gaps"
        }
    )
    
    # Conditional routing after knowledge gaps
    builder.add_conditional_edges(
        "identify_knowledge_gaps",
        route_after_knowledge_gaps,
        {
            "targeted_research": "targeted_research",
            "generate_research_summary": "generate_research_summary"
        }
    )
    
    builder.add_edge("targeted_research", "validation_check")
    builder.add_edge("generate_research_summary", "generate_paper_outline")
    builder.add_edge("generate_paper_outline", "draft_section")
    builder.add_edge("draft_section", "completion_check")
    
    # Conditional routing after completion check
    builder.add_conditional_edges(
        "completion_check",
        route_after_completion,
        {
            "identify_knowledge_gaps": "identify_knowledge_gaps",
            "cross_section_coherence": "cross_section_coherence"
        }
    )
    
    builder.add_edge("cross_section_coherence", "citation_formatting")
    builder.add_edge("citation_formatting", "assemble_final_output")
    builder.add_edge("assemble_final_output", END)
    
    # Compile the graph
    return builder.compile()

# Create the graph
graph = build_graph() 