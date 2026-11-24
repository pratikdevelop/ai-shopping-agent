
import os
import asyncio
from dotenv import load_dotenv
from langgraph_sdk import get_client

load_dotenv()

API_URL = "https://prod-deepagents-agent-build-d4c1479ed8ce53fbb8c3eefc91f0aa7d.us.langgraph.app"
AGENT_ID = "2398b7bb-faf9-4523-8270-08ceba058f08"

async def main():
    client = get_client(
        url=API_URL,
        api_key=os.environ["LANGGRAPH_API_KEY"],
        headers={"X-Auth-Scheme": "langsmith-api-key"},
    )

    print("Starting Shopping Agent...\n")

    async with client:
        async with client.threads.stream(
            assistant_id=AGENT_ID
        ) as thread:

            await thread.run.start(
                input={
                    "messages": [
                        {
                            "role": "user",
                            "content": "Find the best laptop under ₹60,000 in India."
                        }
                    ]
                }
            )

            messages = [
                message async for message in thread.messages
            ]

            for message in messages:
                async for token in message.text:
                    print(token, end="", flush=True)

            final_state = await thread.output

            print("\n\nShopping Agent execution completed.")
            print("Final state:", final_state)


if __name__ == "__main__":
    asyncio.run(main())

