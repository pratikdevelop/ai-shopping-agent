"""Standalone Deep Agent exported from LangSmith Fleet."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from custom_middleware import custom_middleware
from custom_tools import custom_tools
from deepagents import create_deep_agent
from fleet_deepagents_export import StaticSkillsLoader, load_agent_components
from model_provider import create_chat_model

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
FLEET_DIR = PROJECT_DIR / "fleet"
CUSTOM_SKILLS_DIR = PROJECT_DIR / "custom_skills"

_SKILL_LOADER = StaticSkillsLoader(
    [
        (FLEET_DIR / "skills", "/skills/fleet"),
        (CUSTOM_SKILLS_DIR, "/skills/custom"),
    ]
)


async def graph(runtime: Any):
    """Build and return the shopping agent graph."""
    components = await load_agent_components(FLEET_DIR)
    fleet_tools = list(components.get("tools") or [])

    logger.info("Fleet tools loaded: %s", len(fleet_tools))
    for index, tool in enumerate(fleet_tools, start=1):
        if isinstance(tool, dict):
            name = tool.get("name", "unknown")
        else:
            name = getattr(tool, "name", type(tool).__name__)
        logger.info("Fleet tool %s: %s", index, name)

    tool_names = {
        tool.get("name", "") if isinstance(tool, dict)
        else getattr(tool, "name", "")
        for tool in fleet_tools
    }
    if not any("tavily" in str(name).lower() for name in tool_names):
        logger.warning(
            "No Tavily search tool was found in the loaded Fleet tools. "
            "The agent must not claim live web research was performed."
        )

    components.pop("model", None)
    model = create_chat_model()
    components["tools"] = fleet_tools + list(custom_tools)

    if _SKILL_LOADER.files:
        components["skills"] = _SKILL_LOADER.skill_paths

    return create_deep_agent(
        model=model,
        middleware=[_SKILL_LOADER, *custom_middleware],
        **components,
    ).with_config({"recursion_limit": 1000})
