import os
from dataclasses import dataclass, field, fields
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated

# Remove the hardcoded environment variable setting
# os.environ["TAVILY_API_KEY"] = "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"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the research assistant optimized for resource-constrained environments."""
    # Research limits - reduced for better performance on limited hardware
    max_web_research_loops: int = 3
    max_section_revisions: int = 1
    max_targeted_research_attempts: int = 2
    
    # API keys
    tavily_api_key: str = ""  # Will be loaded from environment
    
    # Paper parameters
    citation_style: str = "APA"  # APA, MLA, Chicago, IEEE
    section_params: Dict[str, Any] = field(default_factory=lambda: {
        'abstract_word_limit': 200,
        'introduction_min_sources': 2,
        'literature_review_min_sources': 5,
        'methodology_detail_level': "technical"
    })
    
    # Validation thresholds - optimized for efficiency
    validation_thresholds: Dict[str, Any] = field(default_factory=lambda: {
        'min_citations': 3,
        'max_self_citations': 1,
        'min_sections': 4,  # Minimum number of completed sections
        'literature_survey_min_sources': 6,  # Minimum sources for literature survey
        'coherence_threshold': 0.7  # Threshold for cross-section coherence (0-1)
    })
    
    # Research workflow parameters
    knowledge_gap_threshold: int = 2  # Maximum number of knowledge gaps before targeted research
    style_refinement_level: str = "academic"  # academic, technical, general
    
    # LLM configuration - optimized for resource-constrained environments
    local_llm: str = "deepseek-r1:14b"  # Default to DeepSeek R1 14B for balanced performance
    temperature: float = 0.1  # Lower temperature for more deterministic outputs
    max_tokens: int = 1024  # Limit token generation for better performance
    num_threads: int = 4  # Limit thread usage for better performance on limited CPUs

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})