"""
SIGNAL — Multi-Agent Pipeline
5 specialized agents analyzing enterprise sales transcripts
"""

import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"

def _call(system: str, user: str, max_tokens: int = 1500) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
        system=system
    )
    text = resp.content[0].text`n    text = text.strip()`n    if text.startswith("```"):`n        text = text.split("`n", 1)[-1]`n        if text.endswith("```"):`n            text = text.rsplit("```", 1)[0]`n    return text.strip()


# ── AGENT 1: INGESTION & STRUCTURING ──────────────────────────────────────────
def agent_ingestion(transcript: dict) -> dict:
    """Structures raw transcript into analysis-ready format."""
    system = """You are a sales intelligence analyst. Extract structured information from B2B sales call transcripts.
Return ONLY valid JSON. No markdown, no explanation."""

    user = f"""Analyze this sales call transcript and return JSON with exactly these keys:
{{
  "key_topics": ["list of 4-6 main topics discussed"],
  "buyer_role_insights": {{"role_name": "their primary concern in one sentence"}},
  "deal_context": "2-3 sentence summary of where this deal stands",
  "critical_moments": ["list of 3-4 pivotal exchanges that shaped the conversation"]
}}

TRANSCRIPT:
Title: {transcript['title']}
Stage: {transcript['stage']}
Outcome: {transcript['outcome']}
{transcript['transcript']}"""

    raw = _call(system, user)
    try:
        return json.loads(raw)
    except:
        return {"key_topics": [], "buyer_role_insights": {}, "deal_context": raw[:200], "critical_moments": []}


# ── AGENT 2: PAIN POINT & THEME EXTRACTOR ─────────────────────────────────────
def agent_theme_extractor(transcript: dict) -> dict:
    """Deep qualitative analysis — thematic coding of buyer pain points."""
    system = """You are a qualitative research analyst specializing in thematic analysis of enterprise sales conversations.
Your job is to surface the real underlying problems buyers have, not just the surface complaints.
Return ONLY valid JSON."""

    user = f"""Perform thematic analysis on this sales transcript. Identify pain points with depth and nuance.
Return JSON:
{{
  "primary_pain_points": [
    {{
      "theme": "short name",
      "description": "what they actually said and what it means underneath",
      "severity": "Critical/High/Medium",
      "buyer_quote": "most revealing direct quote"
    }}
  ],
  "secondary_pain_points": ["brief list of 3-4 additional concerns"],
  "unspoken_fears": ["2-3 things the buyer is worried about but didn't say directly"],
  "buying_triggers": ["what would make them say yes"],
  "objections": [
    {{
      "objection": "what they said",
      "type": "Price/Technical/Trust/Timing/Political",
      "how_handled": "how seller responded",
      "resolved": true
    }}
  ]
}}

TRANSCRIPT:
{transcript['transcript']}"""

    raw = _call(system, user, 2000)
    try:
        return json.loads(raw)
    except:
        return {"primary_pain_points": [], "secondary_pain_points": [], "unspoken_fears": [], "buying_triggers": [], "objections": []}


# ── AGENT 3: SENTIMENT & MOMENTUM TRACKER ─────────────────────────────────────
def agent_sentiment(transcript: dict) -> dict:
    """Tracks emotional arc and deal momentum through the conversation."""
    system = """You are a conversation dynamics analyst. Track sentiment and deal momentum through sales conversations.
Return ONLY valid JSON."""

    user = f"""Analyze the emotional arc and momentum of this sales conversation.
Return JSON:
{{
  "overall_sentiment": "Positive/Neutral/Negative/Mixed",
  "buyer_engagement_score": 0-10,
  "momentum_arc": [
    {{"moment": "description", "sentiment_shift": "direction", "cause": "why it shifted"}}
  ],
  "trust_signals": ["moments where trust was built"],
  "risk_signals": ["moments that could jeopardize the deal"],
  "seller_effectiveness": {{
    "strengths": ["what the seller did well"],
    "missed_opportunities": ["what they could have done better"]
  }},
  "next_step_clarity": "Was there a clear next step? What was it?"
}}

TRANSCRIPT:
Title: {transcript['title']}
Outcome: {transcript['outcome']}
{transcript['transcript']}"""

    raw = _call(system, user, 1800)
    try:
        return json.loads(raw)
    except:
        return {"overall_sentiment": "Unknown", "buyer_engagement_score": 5, "momentum_arc": [], "trust_signals": [], "risk_signals": [], "seller_effectiveness": {"strengths": [], "missed_opportunities": []}, "next_step_clarity": ""}


# ── AGENT 4: CROSS-CALL PATTERN SYNTHESIZER ────────────────────────────────────
def agent_pattern_synthesizer(all_analyses: list) -> dict:
    """Finds patterns ACROSS all calls — the strategic intelligence layer."""
    system = """You are a senior market intelligence analyst. You synthesize patterns across multiple enterprise sales conversations
to surface strategic insights that are invisible when looking at individual calls.
Return ONLY valid JSON."""

    summary = []
    for a in all_analyses:
        summary.append({
            "call": a["meta"]["title"],
            "stage": a["meta"]["stage"],
            "outcome": a["meta"]["outcome"],
            "pain_points": [p["theme"] for p in a["themes"].get("primary_pain_points", [])],
            "objections": [o["objection"] for o in a["themes"].get("objections", [])],
            "sentiment": a["sentiment"].get("overall_sentiment", ""),
            "engagement": a["sentiment"].get("buyer_engagement_score", 5),
        })

    user = f"""Analyze these {len(summary)} enterprise sales calls and find cross-call patterns.
Return JSON:
{{
  "top_universal_pain_points": [
    {{"theme": "name", "frequency": "X of {len(summary)} calls", "strategic_implication": "what this means for product/sales"}}
  ],
  "objection_patterns": [
    {{"objection_type": "category", "frequency": "X of {len(summary)}", "best_response_observed": "what worked"}}
  ],
  "market_signals": [
    {{"signal": "observation", "implication": "what this means for the market"}}
  ],
  "ideal_customer_profile": {{
    "triggers": ["what makes a buyer ready to buy"],
    "disqualifiers": ["what makes a deal likely to stall"],
    "champion_profile": "description of the buyer who drives deals forward"
  }},
  "competitive_intelligence": ["insights about competitors mentioned"],
  "win_loss_patterns": {{
    "win_factors": ["what led to closed/positive outcomes"],
    "loss_factors": ["what led to stalled/lost outcomes"]
  }},
  "recommended_talk_tracks": [
    {{"situation": "when", "recommended_approach": "what to say/do"}}
  ]
}}

CALL DATA:
{json.dumps(summary, indent=2)}"""

    raw = _call(system, user, 2500)
    try:
        return json.loads(raw)
    except:
        return {}


# ── AGENT 5: STRATEGIC ADVISOR ─────────────────────────────────────────────────
def agent_strategic_advisor(patterns: dict, all_analyses: list) -> dict:
    """Translates patterns into executive-ready strategic recommendations."""
    system = """You are a chief revenue officer and strategic advisor. Based on sales intelligence patterns,
generate specific, evidence-backed strategic recommendations. Be direct. Be specific. Avoid generic advice.
Return ONLY valid JSON."""

    user = f"""Based on these cross-call patterns from {len(all_analyses)} enterprise sales conversations,
generate executive-level strategic recommendations.
Return JSON:
{{
  "executive_summary": "3-4 sentence synthesis a CEO would find valuable",
  "strategic_recommendations": [
    {{
      "priority": "P1/P2/P3",
      "recommendation": "specific action",
      "evidence": "which calls/patterns support this",
      "expected_impact": "what changes if this is done",
      "owner": "Sales/Product/Marketing/CS"
    }}
  ],
  "product_gaps": ["things buyers want that the product doesn't clearly solve today"],
  "messaging_opportunities": ["ways to sharpen how the product is positioned based on what resonates"],
  "pipeline_health": {{
    "assessment": "overall health of the pipeline represented in these calls",
    "risk_concentration": "where risk is concentrated",
    "recommended_actions": ["immediate actions to protect/accelerate pipeline"]
  }},
  "key_metric_to_watch": "the single metric most predictive of success based on these conversations"
}}

PATTERNS:
{json.dumps(patterns, indent=2)}"""

    raw = _call(system, user, 2000)
    try:
        return json.loads(raw)
    except:
        return {}


# ── ORCHESTRATOR ───────────────────────────────────────────────────────────────
def run_pipeline(transcripts: list, progress_callback=None) -> dict:
    """Run all 5 agents across all transcripts."""
    all_analyses = []
    steps = len(transcripts) * 3 + 2
    step = 0

    def tick(msg):
        nonlocal step
        step += 1
        if progress_callback:
            progress_callback(step / steps, msg)

    # Per-call agents (1-3)
    for t in transcripts:
        tick(f"📋 Structuring: {t['title'][:40]}...")
        ingestion = agent_ingestion(t)

        tick(f"🔍 Extracting themes: {t['title'][:35]}...")
        themes = agent_theme_extractor(t)

        tick(f"📊 Tracking sentiment: {t['title'][:35]}...")
        sentiment = agent_sentiment(t)

        all_analyses.append({
            "meta": {k: v for k, v in t.items() if k != "transcript"},
            "ingestion": ingestion,
            "themes": themes,
            "sentiment": sentiment,
        })

    # Cross-call agents (4-5)
    tick("🧠 Synthesizing patterns across all calls...")
    patterns = agent_pattern_synthesizer(all_analyses)

    tick("💡 Generating strategic recommendations...")
    strategy = agent_strategic_advisor(patterns, all_analyses)

    return {
        "calls": all_analyses,
        "patterns": patterns,
        "strategy": strategy,
        "meta": {
            "total_calls": len(transcripts),
            "stages": list(set(t["stage"] for t in transcripts)),
            "outcomes": {t["outcome"] for t in transcripts},
        }
    }
