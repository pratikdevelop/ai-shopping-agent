
import os
import asyncio
from dotenv import load_dotenv
from langgraph_sdk import get_client

load_dotenv()

AGENT_ID = "2398b7bb-faf9-4523-8270-08ceba058f08"

API_URL = (
    "https://prod-deepagents-agent-build-"
    "d4c1479ed8ce53fbb8c3eefc91f0aa7d.us.langgraph.app"
)

async def main():
    api_key = os.getenv("LANGGRAPH_API_KEY")

    if not api_key:
        raise RuntimeError(
            "LANGGRAPH_API_KEY missing from .env"
        )

    client = get_client(
        url=API_URL,
        api_key=api_key,
        headers={
            "X-Auth-Scheme": "langsmith-api-key"
        },
    )

    print("Connecting to LangChain Fleet...")

    agent = await client.assistants.get(AGENT_ID)

    print("Connection successful!")
    print("Agent details:")
    print(agent)


if __name__ == "__main__":
    asyncio.run(main())
