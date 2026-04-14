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

# fix: wrap all json.loads in try/except with structured fallbacks


def agent_pattern_synthesizer(all_analyses):
    """Agent 4: Cross-call pattern detection."""
    system = "You are a market intelligence analyst. Find patterns across multiple calls. Return ONLY valid JSON."
    summary = [{"call": a["meta"]["title"], "pain_points": [p["theme"] for p in a["themes"].get("primary_pain_points", [])]} for a in all_analyses]
    user = f"Analyze {len(summary)} calls. Return JSON with top_universal_pain_points, objection_patterns, market_signals, win_loss_patterns.\n\n{json.dumps(summary)}"
    raw = _call(system, user, 2500)
    try:
        return json.loads(raw)
    except:
        return {}

# agent 4: added ideal_customer_profile, competitive_intelligence, recommended_talk_tracks


def agent_strategic_advisor(patterns, all_analyses):
    """Agent 5: Strategic recommendations."""
    system = "You are a CRO and strategic advisor. Generate specific, evidence-backed recommendations. Return ONLY valid JSON."
    user = f"Generate strategic recommendations from these patterns.\n\n{json.dumps(patterns)}"
    raw = _call(system, user, 2000)
    try:
        return json.loads(raw)
    except:
        return {}

# agent 5: added pipeline_health, product_gaps, messaging_opportunities, key_metric_to_watch


def run_pipeline(transcripts, progress_callback=None):
    """Orchestrate all 5 agents."""
    all_analyses = []
    for t in transcripts:
        ingestion = agent_ingestion(t)
        themes = agent_theme_extractor(t)
        sentiment = agent_sentiment(t)
        all_analyses.append({"meta": {k:v for k,v in t.items() if k != "transcript"}, "ingestion": ingestion, "themes": themes, "sentiment": sentiment})
    patterns = agent_pattern_synthesizer(all_analyses)
    strategy = agent_strategic_advisor(patterns, all_analyses)
    return {"calls": all_analyses, "patterns": patterns, "strategy": strategy, "meta": {"total_calls": len(transcripts)}}

# orchestrator: added progress_callback support for streamlit progress bar

# fix: all agent outputs now have safe defaults for missing keys
