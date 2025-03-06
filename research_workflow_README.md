# The-Walker: Research Workflow Documentation

This document provides detailed information about the research workflow implemented in The-Walker AI Research Assistant.

## Architecture Overview

The-Walker uses a LangGraph-based architecture to implement a multi-step research workflow. The workflow is designed as a directed graph where each node represents a specific research step, and edges define the flow between steps.

### Key Components

1. **State Management**: The `ResearchPaperState` class maintains the state of the research process, including:
   - Research topic and thesis statement
   - Search queries and results
   - Literature summaries and knowledge gaps
   - Paper sections and citations

2. **Configuration**: The `Configuration` class provides configurable parameters for:
   - Research limits (loop counts, revision attempts)
   - LLM settings (model, temperature, tokens)
   - Citation styles and validation thresholds

3. **Graph Structure**: The workflow is implemented as a directed graph with:
   - Nodes for each research step (literature survey, validation, drafting, etc.)
   - Conditional edges for decision points (e.g., whether more research is needed)
   - Start and end nodes for workflow entry and exit

## Detailed Workflow Steps

### 1. Initialize Research
- **Input**: Research topic from the user
- **Process**: Sets up initial state and working title
- **Output**: Initialized state with research topic

### 2. Thesis Formulation
- **Input**: Research topic
- **Process**: Uses LLM to generate a focused thesis statement
- **Output**: Thesis statement added to state

### 3. Literature Survey
- **Input**: Research topic and thesis statement
- **Process**:
  - Generates search query using LLM
  - Performs web search via Tavily API
  - Formats and deduplicates sources
  - Generates literature summary using LLM
- **Output**: Literature summary and gathered sources

### 4. Validation Check
- **Input**: Literature summary, thesis statement
- **Process**: Evaluates the sufficiency of the literature survey
- **Output**: Validation result (pass/fail) and recommendations

### 5. Knowledge Gap Identification
- **Input**: Literature summary, thesis statement
- **Process**: Uses LLM to identify specific knowledge gaps
- **Output**: Structured knowledge gaps with descriptions and research questions

### 6. Targeted Research
- **Input**: Knowledge gap, research topic
- **Process**:
  - Generates specific search query for the gap
  - Performs focused web search
  - Synthesizes findings to address the gap
  - Updates literature summary with new information
- **Output**: Updated literature summary and additional sources

### 7. Research Summary Generation
- **Input**: Complete literature summary
- **Process**: Creates comprehensive summary of all research findings
- **Output**: Cohesive research summary

### 8. Paper Outline Generation
- **Input**: Research summary, thesis statement
- **Process**: Creates structured outline for the research paper
- **Output**: Outline with sections and subsections

### 9. Section Drafting
- **Input**: Outline, research summary, current section
- **Process**: Drafts each section based on the outline and research
- **Output**: Completed section content

### 10. Completion Check
- **Input**: Completed sections
- **Process**: Verifies that all required sections are complete
- **Output**: Completion status (complete/incomplete)

### 11. Cross-Section Coherence Check
- **Input**: All completed sections
- **Process**: Evaluates consistency and flow across sections
- **Output**: Coherence analysis and recommendations

### 12. Citation Formatting
- **Input**: Gathered sources, citation style
- **Process**: Formats citations according to specified style
- **Output**: Formatted citations and references section

### 13. Final Paper Assembly
- **Input**: All completed sections, citations
- **Process**: Assembles sections into a cohesive paper
- **Output**: Complete research paper

## Resource Optimization Techniques

The workflow incorporates several optimizations for resource-constrained environments:

1. **Controlled Iteration**: Limits on research loops and revision attempts prevent excessive computation.

2. **Efficient Search**: Targeted search queries reduce the number of API calls and focus on relevant information.

3. **Token Management**: Controlled token generation limits memory usage during LLM inference.

4. **Thread Limitation**: Reduced thread count prevents overwhelming CPU resources.

5. **Model Selection**: Optimized for GGUF quantized models, which use less memory and compute.

6. **Incremental Processing**: The workflow processes information incrementally rather than all at once.

7. **Selective Depth**: Adjusts research depth based on the complexity of the topic and available resources.

## Extending the Workflow

The modular design allows for easy extension:

1. **Adding Nodes**: New research steps can be added as nodes in the graph.

2. **Custom Routing**: Conditional edges can be modified to implement custom routing logic.

3. **Configuration Tuning**: Parameters in the Configuration class can be adjusted for different use cases.

4. **Model Swapping**: Different LLMs can be used by changing the model parameter.

5. **API Integration**: Additional APIs can be integrated for specialized research needs. 