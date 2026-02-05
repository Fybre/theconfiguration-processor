"""AI-powered summary generation module.

This module provides optional AI summary generation using local LLMs
with OpenAI-compatible APIs (Ollama, LM Studio, LocalAI, etc.).

Installation:
    pip install -e ".[ai]"      # AI module only
    pip install -e ".[webai]"   # Web interface + AI

Usage:
    from src.ai import LLMConfig, AISummaryGenerator

    config = LLMConfig(
        base_url="http://localhost:11434/v1",
        model_name="llama3.2"
    )
    generator = AISummaryGenerator(config)

    # Test connection
    success, message = generator.test_connection()

    # Generate summaries
    summaries = generator.generate_all_summaries(configuration)
"""

# Graceful import handling - module works without openai installed
AI_AVAILABLE = False
AI_ERROR = None

try:
    from .llm_client import LLMClient, LLMConfig
    from .summary_generator import AISummaryGenerator
    AI_AVAILABLE = True
except ImportError as e:
    AI_ERROR = str(e)
    # Define stub classes so code doesn't break
    class LLMConfig:
        """Stub class when AI dependencies not installed."""
        pass

    class LLMClient:
        """Stub class when AI dependencies not installed."""
        pass

    class AISummaryGenerator:
        """Stub class when AI dependencies not installed."""
        def __init__(self, *args, **kwargs):
            raise ImportError(
                f"AI module not available: {AI_ERROR}\n"
                "Install with: pip install -e \".[ai]\""
            )


__all__ = [
    'LLMConfig',
    'LLMClient',
    'AISummaryGenerator',
    'AI_AVAILABLE',
    'AI_ERROR'
]
