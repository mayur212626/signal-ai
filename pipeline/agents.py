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
