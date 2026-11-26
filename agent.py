"""Standalone deepagent exported from LangSmith Fleet."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from custom_middleware import custom_middleware
from custom_tools import custom_tools
from deepagents import create_deep_agent
from fleet_deepagents_export import (
    StaticSkillsLoader,
    load_agent_components,
)
from model_provider import create_chat_model


PROJECT_DIR = Path(__file__).parent
FLEET_DIR = PROJECT_DIR / "fleet"
CUSTOM_SKILLS_DIR = PROJECT_DIR / "custom_skills"


# Load exported Fleet skills and custom skills.
_SKILL_LOADER = StaticSkillsLoader(
    [
        (FLEET_DIR / "skills", "/skills/fleet"),
        (CUSTOM_SKILLS_DIR, "/skills/custom"),
    ]
)


async def graph(runtime: Any):
    """Build and return the shopping agent graph."""

    # Load Fleet configuration, tools and instructions.
    components = await load_agent_components(FLEET_DIR)

    fleet_tools = list(components.get("tools") or [])

    print(f"\n[DEBUG] Fleet tools loaded: {len(fleet_tools)}", flush=True)

    for index, tool in enumerate(fleet_tools, start=1):
        if isinstance(tool, dict):
            name = tool.get("name", "unknown")
        else:
            name = getattr(tool, "name", type(tool).__name__)

        print(f"[DEBUG] {index}. {name}", flush=True)


    # Remove Fleet-specific model configuration.
    components.pop("model", None)

    # Initialize independently configured LLM.
    model = create_chat_model()

    # Combine Fleet MCP tools and custom Python tools.
    # components["tools"] = (
    #     list(components.get("tools", []))
    #     + list(custom_tools)
    # )
    components["tools"] = fleet_tools + list(custom_tools)

    # Register shopping skills.
    if _SKILL_LOADER.files:
        components["skills"] = _SKILL_LOADER.skill_paths

    # Build the production Deep Agent.
    return create_deep_agent(
        model=model,
        middleware=[
            _SKILL_LOADER,
            *custom_middleware,
        ],
        **components,
    ).with_config(
        {"recursion_limit": 1000}
    )