from enum import Enum

class LLMEnum(Enum):
    """
    Enum for LLM types.
    """
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"  