"""
SIGNAL — Multi-Agent Pipeline
"""

import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"

def _call(system, user, max_tokens=1500):
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
        system=system
    )
    return resp.content[0].text

def agent_ingestion(transcript):
    """Agent 1: Structure raw transcript."""
    system = "You are a sales intelligence analyst. Extract structured information. Return ONLY valid JSON."
    user = f"Analyze this transcript and return JSON with: key_topics, buyer_role_insights, deal_context, critical_moments\n\n{transcript['transcript']}"
    raw = _call(system, user)
    try:
        return json.loads(raw)
    except:
        return {"key_topics": [], "deal_context": raw[:200], "critical_moments": []}


# Agent 1 v2 — improved JSON schema with buyer_role_insights
def agent_ingestion_v2(transcript):
    """Improved ingestion with richer schema."""
    pass  # will replace agent_ingestion


def agent_theme_extractor(transcript):
    """Agent 2: Thematic analysis — pain points."""
    system = "You are a qualitative research analyst. Perform thematic analysis. Return ONLY valid JSON."
    user = f"Extract pain points from this transcript. Return JSON with primary_pain_points, objections.\n\n{transcript['transcript']}"
    raw = _call(system, user, 2000)
    try:
        return json.loads(raw)
    except:
        return {"primary_pain_points": [], "objections": []}

# agent 2 extended: unspoken_fears, buying_triggers added to schema


def agent_sentiment(transcript):
    """Agent 3: Sentiment and deal momentum tracking."""
    system = "You are a conversation dynamics analyst. Return ONLY valid JSON."
    user = f"Analyze sentiment and momentum.\n\nOutcome: {transcript['outcome']}\n{transcript['transcript']}"
    raw = _call(system, user, 1800)
    try:
        return json.loads(raw)
    except:
        return {"overall_sentiment": "Unknown", "buyer_engagement_score": 5}

# agent 3: added trust_signals, risk_signals, seller_effectiveness to output
