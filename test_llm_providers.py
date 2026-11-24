import os
from dotenv import load_dotenv

load_dotenv()

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_groq import ChatGroq


def test_nvidia():
    print("\nTesting NVIDIA Nemotron...")

    model = ChatNVIDIA(
        model=os.getenv(
            "NVIDIA_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b",
        ),
        nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    )

    response = model.invoke(
        "Reply with exactly: NVIDIA CONNECTION SUCCESSFUL"
    )

    print("Response:", response.content)


def test_groq():
    print("\nTesting Groq...")

    model = ChatGroq(
        model=os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        ),
        api_key=os.getenv("GROQ_API_KEY"),
    )

    response = model.invoke(
        "Reply with exactly: GROQ CONNECTION SUCCESSFUL"
    )

    print("Response:", response.content)


if __name__ == "__main__":
    for name, test in [
        ("NVIDIA", test_nvidia),
        ("Groq", test_groq),
    ]:
        try:
            test()
            print(f"{name}: SUCCESS")
        except Exception as exc:
            print(f"{name}: FAILED - {type(exc).__name__}: {exc}")

