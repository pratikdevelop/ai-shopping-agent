"""Run shopping research through the existing LangGraph Deep Agent."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI

from backend.app.schemas.shopping import ProductSearchRequest

logger = logging.getLogger(__name__)
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")


class ShoppingAgentError(RuntimeError):
    """Raised when the LangGraph shopping agent cannot produce an answer."""


def build_research_prompt(request: ProductSearchRequest) -> str:
    """Build a complete, self-contained research prompt from validated input."""
    research_date = datetime.now(INDIA_TIMEZONE).date().isoformat()

    details = [
        "You are conducting a real shopping research task, not giving a general product overview.",
        f"CURRENT RESEARCH DATE (India, Asia/Kolkata): {research_date}.",
        "Use this exact date as the Research timestamp in your report. Never reuse a date from memory, prior chats, search snippets, or old reports.",
        "Use live Tavily web search for this request. Inspect relevant product and official retailer pages with read_url_content when accessible.",
        "Do not ask follow-up questions. Use all supplied requirements and complete the research.",
        "Never invent prices, offers, ratings, review counts, seller details, delivery estimates, stock, showroom addresses, phone numbers, or URLs.",
        "Do not claim a retailer, offer, price, stock, or showroom detail is verified unless a current source directly supports it.",
        "A search-result snippet is a discovery lead, not proof of stock, a final checkout price, or a confirmed showroom quotation.",
        "Use direct product-page links where available. Cite a source URL alongside every listed price, offer, seller claim, and local-store claim.",
        "If a value cannot be substantiated, write 'Not verified'. Do not estimate a missing value or fill it from memory.",
        "Do not describe research as comprehensive if any requested retailer or important evidence could not be checked.",
        "Do not start with narration such as 'Now I have comprehensive data'. Return the actual report directly.",
        "",
        "REQUIRED REPORT FORMAT",
        "1. Product overview: exact product, variant, condition, location, budget, and the exact research date above.",
        "2. Retailer comparison: provide a Markdown table with one row for every preferred retailer. Include retailer, exact product/variant, listed price, shipping, unconditional discount, standard payable price, conditional offers, seller, rating/reviews, delivery/availability, and direct source link. Use 'Not verified' for missing evidence.",
        "3. Offer breakdown: separate instant bank discounts, coupons, cashback, exchange bonuses, and EMI offers. State eligibility, validity, and source. Do not subtract conditional benefits from the standard payable price.",
        "4. Local stores: only when requested, list stores in the requested city with official store-locator/product evidence. Clearly distinguish an actual retailer branch from an independent multi-brand shop. Do not claim stock without store-specific confirmation.",
        "5. Recommendations: identify the lowest verified standard payable price and the most trustworthy option only when evidence supports those conclusions. Otherwise say that no winner can yet be verified.",
        "6. Sources: provide direct clickable URLs. Do not cite fabricated or generic search URLs.",
        "",
        "COMPLETION RULES",
        "- Include the comparison table even if every retailer row contains 'Not verified'.",
        "- Include at least one direct source URL for every verified retailer price or offer.",
        "- If live search fails or its results do not support a comparison, state that clearly and return a partial report. Never manufacture a completed comparison.",
        "- Do not use a historical research timestamp. The required timestamp is exactly the current date supplied above.",
        "- Keep the report focused on the requested product. Do not pad it with specifications unless they help establish exact model/variant matching.",
        "",
        "USER REQUIREMENTS",
        f"Product/query: {request.query}",
        f"Country: {request.country}",
        f"Currency: {request.currency}",
        f"Budget: {request.budget_amount if request.budget_amount is not None else 'Not specified'} {request.currency}",
        f"Condition: {request.condition}",
        f"Brand: {request.brand or 'Not specified'}",
        f"Category: {request.category or 'Not specified'}",
        f"City: {request.city or 'Not specified'}",
        f"State: {request.state or 'Not specified'}",
        f"Postal code: {request.postal_code or 'Not specified'}",
        f"Required specifications: {request.specifications or 'Not specified'}",
        f"Preferred retailers: {', '.join(request.preferred_retailers) if request.preferred_retailers else 'Search reputable retailers relevant to this product'}",
        f"Include physical/local stores: {'Yes' if request.include_local_stores else 'No'}",
    ]

    return "\n".join(details)


def _message_content(message: Any) -> Any:
    if isinstance(message, dict):
        return message.get("content")
    return getattr(message, "content", None)


def _message_role(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("role") or message.get("type") or "").lower()
    return str(getattr(message, "type", "") or getattr(message, "role", "")).lower()


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text_value = block.get("text")
                if isinstance(text_value, str):
                    parts.append(text_value)
        return "\n".join(part for part in parts if part).strip()

    return ""


def _extract_final_answer(result: Any) -> str:
    if not isinstance(result, dict):
        raise ShoppingAgentError("The LangGraph agent returned an unexpected response format.")

    messages = result.get("messages")
    if not isinstance(messages, list):
        raise ShoppingAgentError("The LangGraph agent response did not contain a messages list.")

    # Prefer the last assistant/AI message with visible text. Tool-call-only
    # assistant messages are skipped because they are not the final answer.
    for message in reversed(messages):
        if _message_role(message) not in {"ai", "assistant"}:
            continue

        tool_calls = (
            message.get("tool_calls")
            if isinstance(message, dict)
            else getattr(message, "tool_calls", None)
        )
        content = _content_to_text(_message_content(message))
        if content and not tool_calls:
            return content

    raise ShoppingAgentError("The LangGraph agent did not return a final text answer.")


def _observed_tool_activity(result: Any) -> tuple[set[str], set[str]]:
    """Return tool names called and tool names with non-empty result messages."""
    called: set[str] = set()
    returned: set[str] = set()

    if not isinstance(result, dict):
        return called, returned

    for message in result.get("messages", []):
        if isinstance(message, dict):
            tool_calls = message.get("tool_calls") or []
            message_name = message.get("name")
            status = message.get("status")
            is_error = bool(message.get("is_error") or message.get("isError"))
        else:
            tool_calls = getattr(message, "tool_calls", None) or []
            message_name = getattr(message, "name", None)
            status = getattr(message, "status", None)
            is_error = bool(getattr(message, "is_error", False))

        for call in tool_calls:
            if isinstance(call, dict):
                name = call.get("name")
                if not name and isinstance(call.get("function"), dict):
                    name = call["function"].get("name")
            else:
                name = getattr(call, "name", None)
            if isinstance(name, str) and name:
                called.add(name.lower())

        role = _message_role(message)
        if (
            role in {"tool", "tool_result"}
            and isinstance(message_name, str)
            and message_name
        ):
            called.add(message_name.lower())
            content = _content_to_text(_message_content(message))
            if content and status != "error" and not is_error:
                returned.add(message_name.lower())

    return called, returned


def _validate_research_answer(answer: str, research_date: str) -> list[str]:
    """Flag obvious gaps that make a purported completed comparison unreliable."""
    warnings: list[str] = []

    has_markdown_table = bool(
        re.search(r"(?m)^\s*\|.*\|\s*$", answer)
        and re.search(r"(?m)^\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*$", answer)
    )
    if not has_markdown_table:
        warnings.append(
            "The final answer does not contain a Markdown retailer-comparison table."
        )

    urls = set(re.findall(r"https?://[^\s)>\]]+", answer, flags=re.IGNORECASE))
    if len(urls) < 2:
        warnings.append(
            "The final answer contains fewer than two direct source URLs. "
            "Retailer prices and offers cannot be independently checked from this response."
        )

    if not re.search(r"(?im)^\s*(?:#{1,6}\s*)?Sources?\s*:?\s*$", answer):
        if not re.search(r"(?im)^\s*(?:#{1,6}\s*)?References?\s*:?\s*$", answer):
            warnings.append("The final answer does not include a dedicated Sources section.")

    timestamp_match = re.search(
        r"(?i)research\s+(?:timestamp|date)[^0-9]{0,30}(\d{4}-\d{2}-\d{2})",
        answer,
    )
    if not timestamp_match:
        warnings.append(
            f"The answer does not state the required research date ({research_date})."
        )
    elif timestamp_match.group(1) != research_date:
        warnings.append(
            f"The answer reports research date {timestamp_match.group(1)}, "
            f"but this search ran on {research_date} (India time)."
        )

    return warnings


async def _get_agent(app: FastAPI) -> Any:
    """Build the graph once per API process, only when a search is requested."""
    agent = getattr(app.state, "shopping_agent", None)
    if agent is not None:
        return agent

    lock = getattr(app.state, "shopping_agent_lock", None)
    if lock is None:
        lock = asyncio.Lock()
        app.state.shopping_agent_lock = lock

    async with lock:
        agent = getattr(app.state, "shopping_agent", None)
        if agent is not None:
            return agent

        try:
            # Import lazily so the FastAPI health endpoint can work even if
            # provider credentials or Fleet MCP tools are not configured yet.
            from agent import graph

            agent = await graph({})
        except Exception as exc:
            logger.exception("Could not initialize the LangGraph shopping agent")
            raise ShoppingAgentError(
                "The shopping agent could not initialize. Check provider credentials, "
                "Fleet MCP configuration, and backend logs."
            ) from exc

        app.state.shopping_agent = agent
        return agent


async def run_shopping_research(
    request: ProductSearchRequest,
    app: FastAPI,
) -> tuple[str, list[str]]:
    """Invoke LangGraph and return the answer plus evidence-quality warnings."""
    research_date = datetime.now(INDIA_TIMEZONE).date().isoformat()
    agent = await _get_agent(app)
    prompt = build_research_prompt(request)

    try:
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
    except Exception as exc:
        logger.exception("LangGraph shopping research invocation failed")
        raise ShoppingAgentError(
            "The shopping agent failed while researching this request. Check backend logs."
        ) from exc

    answer = _extract_final_answer(result)
    called_tools, returned_tools = _observed_tool_activity(result)
    warnings = _validate_research_answer(answer, research_date)

    tavily_called = any("tavily" in name for name in called_tools)
    tavily_returned = any("tavily" in name for name in returned_tools)
    if not tavily_called:
        warnings.append(
            "No Tavily search tool call was observed in the LangGraph execution. "
            "Treat current prices, offers, and availability as unverified."
        )
    elif not tavily_returned:
        warnings.append(
            "A Tavily tool call was observed, but no non-empty successful Tavily tool result "
            "was found in the LangGraph messages."
        )

    url_reader_called = any(
        "read_url" in name or "url_content" in name for name in called_tools
    )
    url_reader_returned = any(
        "read_url" in name or "url_content" in name for name in returned_tools
    )
    if not url_reader_called:
        warnings.append(
            "No URL-reading tool call was observed. Product-page details may not have been independently inspected."
        )
    elif not url_reader_returned:
        warnings.append(
            "A URL-reading tool call was observed, but no non-empty successful URL-reading result was found."
        )

    # Keep warnings unique while preserving their explanatory order.
    warnings = list(dict.fromkeys(warnings))
    if warnings:
        logger.warning(
            "Shopping research returned with evidence-quality warnings: %s",
            warnings,
        )

    return answer, warnings
