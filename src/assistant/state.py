import operator
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict, Annotated
from datetime import datetime

@dataclass(kw_only=True)
class ResearchPaperState:
    # Core research parameters
    research_topic: str = field(default=None)  # Main research topic
    working_title: str = field(default=None)  # Working title for the paper
    thesis_statement: str = field(default=None)  # Thesis statement for the research
    
    # Research process tracking
    search_query: str = field(default=None)  # Current search query
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)  # Search results
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)  # Formatted sources
    research_loop_count: int = field(default=0)  # Research iteration counter
    literature_summary: str = field(default=None)  # Summary of literature findings
    
    # Validation tracking
    validation_result: Dict[str, Any] = field(default_factory=dict)  # Results of validation check
    validation_passed: bool = field(default=False)  # Whether validation passed
    knowledge_gaps: Dict[str, Any] = field(default_factory=dict)  # Identified knowledge gaps
    
    # Paper sections
    outline: Dict[str, List[str]] = field(default_factory=dict)  # Paper outline
    sections: Dict[str, str] = field(default_factory=lambda: {
        'abstract': None,
        'introduction': None,
        'literature_review': None,
        'methodology': None,
        'results': None,
        'discussion': None,
        'conclusion': None,
        'references': None
    })
    
    # Citation management
    citations: Dict[str, Any] = field(default_factory=lambda: {
        'sources': [],
        'formatted': []
    })
    
    # Progress tracking
    current_section: str = field(default="introduction")  # Current section being worked on
    completed_sections: List[str] = field(default_factory=list)  # Completed sections
    all_sections_complete: bool = field(default=False)  # Whether all sections are complete
    
    # Cross-section coherence
    coherence_analysis: str = field(default=None)  # Analysis of cross-section coherence
    
    # Validation tracking
    validation_status: Dict[str, bool] = field(default_factory=lambda: {
        'sources_verified': False,
        'outline_approved': False,
        'methodology_sound': False,
        'results_consistent': False,
        'citations_complete': False
    })
    
    # Human-in-the-loop verification
    human_verification_required: bool = field(default=False)  # Flag if human verification is needed
    human_feedback: str = field(default=None)  # Feedback from human reviewer
    verification_history: List[Dict] = field(default_factory=list)  # History of verification interactions
    verification_step: str = field(default=None)  # Current step requiring verification
    
    # Final output
    running_summary: str = field(default=None)  # Progressive summary (for compatibility)
    final_paper: str = field(default=None)  # Complete assembled paper
    citation_style: str = field(default="APA")  # Citation style for the paper

    def record_verification(self, step: str, feedback: str, approved: bool):
        """Record human verification interaction"""
        self.verification_history.append({
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "feedback": feedback,
            "approved": approved,
            "section": self.current_section
        })
        self.human_verification_required = False
        self.human_feedback = feedback
        
        # Update validation status based on the step
        if step in self.validation_status:
            self.validation_status[step] = approved
            
        return self

    def request_verification(self, step: str):
        """Request human verification for a specific step"""
        self.human_verification_required = True
        self.verification_step = step
        return self

@dataclass(kw_only=True)
class SummaryStateInput(TypedDict):
    research_topic: str = field(default=None)  # Report topic
    target_audience: str = field(default="academic")  # Target audience
    citation_style: str = field(default="IEEE")  # Citation style

@dataclass(kw_only=True)
class SummaryStateOutput(TypedDict):
    running_summary: str = field(default=None)  # Final report summary
    final_paper: str = field(default=None)  # Complete research paper
    verification_report: Dict = field(default_factory=dict)  # Human verification summary