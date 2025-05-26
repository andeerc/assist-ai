from langchain_openai import ChatOpenAI
from openai import OpenAI # Added for get_openai_client
from .settings import OPENAI_API_KEY

def get_llm(model_name: str, temperature: float = 0.7, **kwargs) -> ChatOpenAI:
    """
    Provides a centralized way to get ChatOpenAI LLM instances for crewAI.
    Ensure OPENAI_API_KEY is set in your environment or .env file.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in settings. Please ensure it's set in your .env file or environment variables.")
    
    return ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model=model_name, # Corrected parameter name from model_name to model for ChatOpenAI
        temperature=temperature,
        **kwargs
    )

def get_gpt35(temperature: float = 0.1, **kwargs) -> ChatOpenAI:
    """
    DEPRECATED: Use get_llm(model_name="gpt-3.5-turbo", temperature=...) instead.
    Provides a GPT-3.5-turbo LLM instance.
    The default temperature is set to 0.1 for potentially more deterministic behavior
    in agents that previously used temperature=0.
    """
    return get_llm(model_name="gpt-3.5-turbo", temperature=temperature, **kwargs)

def get_gpt40(temperature: float = 0.1, **kwargs) -> ChatOpenAI:
    """
    DEPRECATED: Use get_llm(model_name="gpt-4o", temperature=...) instead.
    Provides a GPT-4o LLM instance.
    The default temperature is set to 0.1 for potentially more deterministic behavior
    in agents that previously used temperature=0.
    """
    return get_llm(model_name="gpt-4o", temperature=temperature, **kwargs)

def get_openai_client() -> OpenAI:
    """
    Provides an OpenAI client instance, typically for direct API interactions
    like those in ChatManager.
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in settings. Please ensure it's set in your .env file or environment variables.")
    return OpenAI(api_key=OPENAI_API_KEY)