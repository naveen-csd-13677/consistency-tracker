"""LLM integration service with multi-provider support."""

import json
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.models.llm_config import LLMConfig

logger = logging.getLogger(__name__)


def _get_llm_config(db: Session) -> Optional[LLMConfig]:
    """Get the active LLM configuration from the database."""
    return db.query(LLMConfig).first()


def _call_openai(api_key: str, model: str, prompt: str) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model or "gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return ""


def _call_anthropic(api_key: str, model: str, prompt: str) -> str:
    """Call Anthropic API."""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model or "claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        logger.error("Anthropic API error: %s", e)
        return ""


def _call_google(api_key: str, model: str, prompt: str) -> str:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        gen_model = genai.GenerativeModel(model or "gemini-pro")
        response = gen_model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error("Google API error: %s", e)
        return ""


def _call_ollama(base_url: str, model: str, prompt: str) -> str:
    """Call Ollama local API."""
    try:
        import urllib.request

        url = f"{base_url}/api/generate"
        data = json.dumps({"model": model or "llama2", "prompt": prompt, "stream": False})
        req = urllib.request.Request(
            url,
            data=data.encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "")
    except Exception as e:
        logger.error("Ollama API error: %s", e)
        return ""


def call_llm(db: Session, prompt: str) -> str:
    """Call the configured LLM provider. Falls back to empty string on failure."""
    config = _get_llm_config(db)
    if not config or not config.provider:
        return ""

    provider = config.provider.lower()
    model = config.model

    if provider == "openai" and config.openai_api_key:
        return _call_openai(config.openai_api_key, model, prompt)
    elif provider == "anthropic" and config.anthropic_api_key:
        return _call_anthropic(config.anthropic_api_key, model, prompt)
    elif provider == "google" and config.google_api_key:
        return _call_google(config.google_api_key, model, prompt)
    elif provider == "ollama":
        return _call_ollama(config.ollama_base_url or "http://localhost:11434", model, prompt)

    return ""


def generate_suggestion_for_goal(
    db: Session,
    goal_name: str,
    purpose: str,
    current_duty: str,
    difficulty: str,
    weekly_pct: float,
    status_indicator: str,
) -> str:
    """Generate an AI suggestion for a goal based on its performance."""
    prompt = f"""You are a personal consistency coach. Analyze this goal and provide a brief, actionable suggestion.

Goal: {goal_name}
Purpose: {purpose}
Current Duty: {current_duty}
Difficulty: {difficulty}
Weekly Consistency: {weekly_pct}%
Status: {status_indicator}

{"This goal is struggling. Suggest concrete modifications to make the duty more achievable (reduce scope, change timing, restructure)." if weekly_pct < 70 else ""}
{"This goal needs attention. Suggest small improvements to boost consistency." if 70 <= weekly_pct < 90 else ""}
{"This goal is on track. Provide encouragement and suggest ways to maintain momentum." if weekly_pct >= 90 else ""}

Respond with a concise 2-3 sentence suggestion."""

    result = call_llm(db, prompt)
    if not result:
        # Rule-based fallback
        if weekly_pct < 70:
            return f"Consider reducing the scope of '{current_duty}' to make it more achievable. Try breaking it into smaller steps or reducing the duration/intensity."
        elif weekly_pct < 90:
            return f"You're making progress with '{current_duty}'. Try setting a specific time each day for this duty and removing potential obstacles."
        else:
            return f"Excellent consistency with '{current_duty}'! Keep up the great work. Consider if you're ready for a slightly more challenging version."

    return result


def generate_upgrade_proposal(
    db: Session,
    goal_name: str,
    purpose: str,
    current_duty: str,
    current_difficulty: str,
    next_difficulty: str,
) -> str:
    """Generate an AI-proposed new duty for an upgrade."""
    prompt = f"""You are a personal consistency coach. A user has maintained ≥95% consistency for 4+ weeks and is ready for an upgrade.

Goal: {goal_name}
Purpose: {purpose}
Current Duty: {current_duty}
Current Difficulty: {current_difficulty}
Next Difficulty Level: {next_difficulty}

Propose a specific new duty that represents a reasonable progression. The new duty should be:
- Slightly more challenging than the current duty
- Still achievable with consistent effort
- Aligned with the goal's purpose

Respond with ONLY the new duty description (one sentence)."""

    result = call_llm(db, prompt)
    if not result:
        # Rule-based fallback
        return f"{current_duty} (increased intensity - {next_difficulty} level)"

    return result.strip()


def generate_motivation(db: Session, overall_pct: float, perfect_days: int) -> str:
    """Generate a personalised motivational message."""
    prompt = f"""You are an encouraging personal consistency coach. Generate a brief motivational message.

Overall Consistency: {overall_pct}%
Perfect Days (all goals completed): {perfect_days}

Provide a 1-2 sentence motivational message that acknowledges their current performance. Be specific and encouraging."""

    result = call_llm(db, prompt)
    if not result:
        if overall_pct >= 90:
            return f"Outstanding! You've achieved {overall_pct}% consistency with {perfect_days} perfect days. You're building unstoppable momentum!"
        elif overall_pct >= 70:
            return f"Good progress at {overall_pct}% consistency! With {perfect_days} perfect days, you're on the right track. Keep pushing!"
        else:
            return f"Every day is a new opportunity. You have {perfect_days} perfect days already - let's build on that foundation!"

    return result
