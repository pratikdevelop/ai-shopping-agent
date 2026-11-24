import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


@tool
def search_product(query: str) -> str:
    """Search for a shopping product using a search query."""
    return f"Product search executed: {query}"


def test_nvidia():
    from langchain_nvidia_ai_endpoints import ChatNVIDIA

    model = ChatNVIDIA(
        model=os.getenv(
            "NVIDIA_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b",
        ),
        nvidia_api_key=os.getenv("NVIDIA_API_KEY"),
    )

    return model


def test_groq():
    from langchain_groq import ChatGroq

    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        api_key=os.getenv("GROQ_API_KEY"),
    )

    return model


def verify_tool_calling(name, model):
    print(f"\nTesting {name} tool calling...")

    model_with_tools = model.bind_tools(
        [search_product],
        tool_choice="required",
    )

    response = model_with_tools.invoke(
        "Search for laptops under 60000 Indian rupees. "
        "Call the search_product tool with an appropriate query."
    )

    if response.tool_calls:
        for call in response.tool_calls:
            print("Tool:", call["name"])
            print("Arguments:", call["args"])

        print(f"{name}: TOOL CALLING SUCCESSFUL")
    else:
        raise RuntimeError(
            f"{name} did not return a tool call: {response.content}"
        )


if __name__ == "__main__":
    for name, factory in [
        ("NVIDIA", test_nvidia),
        ("GROQ", test_groq),
    ]:
        try:
            verify_tool_calling(name, factory())
        except Exception as exc:
            print(f"{name}: FAILED - {type(exc).__name__}: {exc}")
