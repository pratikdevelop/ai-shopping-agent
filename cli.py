"""Interactive CLI for the AI Shopping & Deal Finder."""

from __future__ import annotations

import asyncio
from agent import graph


async def main() -> None:
    agent = await graph({})

    # Preserve conversation history across agent invocations.
    conversation_history = []

    print("\nAI Shopping & Deal Finder")
    print("----------------------------------------")
    print("Commands:")
    print("  /multi  - Enter a multiline message")
    print("  /reset  - Clear conversation history")
    print("  /exit   - Quit")
    print("----------------------------------------")

    while True:
        try:
            user_input = input("\nYou: ")

        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            return

        command = user_input.strip().lower()

        if command in {"/exit", "/quit"}:
            print("Bye!")
            return

        if command == "/reset":
            conversation_history.clear()
            print("Conversation history cleared.")
            continue

        # Multiline prompt support.
        if command in {"/multi", "/paste"}:
            print("\nPaste your complete prompt below.")
            print("Type /send on a new line when finished.")
            print("Type /cancel to discard the message.\n")

            lines = []

            try:
                while True:
                    line = input("... ")

                    if line.strip().lower() == "/send":
                        break

                    if line.strip().lower() == "/cancel":
                        lines = []
                        break

                    if line.strip().lower() in {"/exit", "/quit"}:
                        print("\nBye!")
                        return

                    lines.append(line)

            except (KeyboardInterrupt, EOFError):
                print("\nMultiline input cancelled.")
                continue

            user_input = "\n".join(lines).strip()

        if not user_input.strip():
            continue

        # Include previous messages instead of sending only the latest input.
        request_messages = [
            *conversation_history,
            {
                "role": "user",
                "content": user_input,
            },
        ]

        try:
            result = await agent.ainvoke(
                {"messages": request_messages}
            )

            # Save the complete conversation for the next invocation.
            conversation_history = result.get(
                "messages",
                request_messages,
            )

            response_messages = result.get("messages", [])

            if response_messages:
                last_message = response_messages[-1]

                if isinstance(last_message, dict):
                    answer = last_message.get("content", "")
                else:
                    answer = getattr(last_message, "content", "")

                print("\nAgent:", flush=True)

                if isinstance(answer, str):
                    print(answer)
                else:
                    print(answer)

                print()

            else:
                print("\nAgent: No response was returned.\n")

        except Exception as exc:
            print(f"\nAgent error: {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    asyncio.run(main())