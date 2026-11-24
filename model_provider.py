import os

from langchain_core.language_models.chat_models import BaseChatModel


def create_chat_model() -> BaseChatModel:
    """
    Create the configured LLM provider.

    Supported providers:
    - NVIDIA Nemotron
    - Groq GPT-OSS
    """

    provider = os.getenv("LLM_PROVIDER", "nvidia").strip().lower()

    if provider == "nvidia":
        from langchain_nvidia_ai_endpoints import ChatNVIDIA

        api_key = os.getenv("NVIDIA_API_KEY")

        if not api_key:
            raise ValueError("NVIDIA_API_KEY is missing.")

        model_name = os.getenv(
            "NVIDIA_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b",
        )

        print(f"Initializing NVIDIA model: {model_name}")

        return ChatNVIDIA(
            model=model_name,
            nvidia_api_key=api_key,
        )

    elif provider == "groq":
        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is missing.")

        model_name = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        print(f"Initializing Groq model: {model_name}")

        return ChatGroq(
            model=model_name,
            api_key=api_key,
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. "
            "Choose 'nvidia' or 'groq'."
        )
