"""
SIGNAL — Sales Intelligence & Gap Analysis Layer
Enterprise-grade multi-agent transcript analysis platform
"""

import streamlit as st
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

from data.transcripts import TRANSCRIPTS
from pipeline.agents import run_pipeline
from utils.report import generate_report
import plotly.graph_objects as go
import plotly.express as px

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIGNAL — Sales Intelligence",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #F7F9FC; }

  .signal-header {
    background: linear-gradient(135deg, #0D2B55 0%, #1a4a8a 100%);
    color: white; padding: 2rem 2.5rem; border-radius: 12px;
    margin-bottom: 1.5rem;
  }
  .signal-header h1 { font-size: 2.2rem; font-weight: 700; margin: 0; letter-spacing: -0.5px; }
  .signal-header p { font-size: 0.95rem; opacity: 0.8; margin: 0.3rem 0 0 0; }

  .metric-card {
    background: white; border-radius: 10px; padding: 1.2rem 1.5rem;
    border-left: 4px solid #2E75B6; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    margin-bottom: 0.5rem;
  }
  .metric-card .val { font-size: 2rem; font-weight: 700; color: #0D2B55; line-height: 1; }
  .metric-card .label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.2rem; }

  .call-card {
    background: white; border-radius: 10px; padding: 1.2rem 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 1rem;
    border-top: 3px solid #2E75B6;
  }
  .call-card.won { border-top-color: #1A7A4A; }
  .call-card.lost { border-top-color: #C0392B; }
  .call-card.active { border-top-color: #E67E22; }

  .pain-badge {
    display: inline-block; background: #EEF4FF; color: #2E75B6;
    border-radius: 20px; padding: 2px 10px; font-size: 0.75rem;
    font-weight: 500; margin: 2px 3px 2px 0;
  }
  .pain-badge.critical { background: #FEF0EF; color: #C0392B; }
  .pain-badge.high { background: #FFF5EB; color: #E67E22; }

  .quote-block {
    background: #F7F9FC; border-left: 3px solid #2E75B6;
    padding: 0.6rem 1rem; border-radius: 0 6px 6px 0;
    font-style: italic; color: #444; font-size: 0.85rem;
    margin: 0.5rem 0;
  }

  .insight-card {
    background: white; border-radius: 10px; padding: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 0.8rem;
  }
  .insight-card .priority-p1 { color: #C0392B; font-weight: 700; }
  .insight-card .priority-p2 { color: #E67E22; font-weight: 700; }
  .insight-card .priority-p3 { color: #2E75B6; font-weight: 700; }

  .tag {
    display: inline-block; background: #EEF4FF; color: #2E75B6;
    border-radius: 4px; padding: 1px 8px; font-size: 0.72rem; font-weight: 500;
    margin: 1px 2px;
  }
  .tag.green { background: #EEFAF4; color: #1A7A4A; }
  .tag.red { background: #FEF0EF; color: #C0392B; }
  .tag.gray { background: #F4F4F4; color: #666; }

  .section-title {
    font-size: 0.7rem; font-weight: 600; color: #888;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem;
  }

  div[data-testid="stSidebar"] { background: #0D2B55 !important; }
  div[data-testid="stSidebar"] * { color: white !important; }
  div[data-testid="stSidebar"] .stSelectbox label { color: rgba(255,255,255,0.7) !important; }
  div[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

  .stButton button {
    background: #2E75B6; color: white; border: none;
    border-radius: 8px; font-weight: 600; padding: 0.5rem 1.5rem;
  }
  .stButton button:hover { background: #1a5a9a; }

  .stProgress > div > div { background: #2E75B6; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📡 SIGNAL")
    st.markdown("*Sales Intelligence Layer*")
    st.markdown("---")

    st.markdown("**Select Calls to Analyze**")
    call_options = {t["title"]: t for t in TRANSCRIPTS}
    selected_titles = st.multiselect(
        "Transcripts",
        options=list(call_options.keys()),
        default=list(call_options.keys()),
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Upload Your Own**")
    uploaded = st.file_uploader("Paste or upload .txt transcript", type=["txt"], label_visibility="collapsed")

    st.markdown("---")
    run_btn = st.button("⚡  Run Analysis", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; opacity:0.6; line-height:1.6;">
    <b>Pipeline</b><br>
    Agent 1: Ingestion & Structure<br>
    Agent 2: Thematic Analysis<br>
    Agent 3: Sentiment Tracking<br>
    Agent 4: Pattern Synthesis<br>
    Agent 5: Strategic Advisory
    </div>
    """, unsafe_allow_html=True)


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="signal-header">
  <h1>📡 SIGNAL</h1>
  <p>Sales Intelligence & Gap Analysis Layer · Multi-Agent LLM Pipeline · Enterprise B2B Transcripts</p>
</div>
""", unsafe_allow_html=True)


# ── INIT STATE ────────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None
if "running" not in st.session_state:
    st.session_state.running = False


# ── RUN PIPELINE ──────────────────────────────────────────────────────────────
if run_btn and selected_titles:
    selected_transcripts = [call_options[t] for t in selected_titles]

    # Handle uploaded transcript
    if uploaded:
        content = uploaded.read().decode("utf-8")
        selected_transcripts.append({
            "id": "uploaded",
            "title": uploaded.name.replace(".txt",""),
            "date": "2026-01-01",
            "stage": "Unknown",
            "outcome": "Pending Analysis",
            "duration_min": 0,
            "participants": {"seller": [], "buyer": []},
            "transcript": content
        })

    st.markdown("### ⚙️ Running Multi-Agent Pipeline...")
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(pct, msg):
        progress_bar.progress(min(pct, 1.0))
        status_text.markdown(f"<span style='color:#2E75B6; font-size:0.85rem;'>{msg}</span>", unsafe_allow_html=True)

    with st.spinner(""):
        results = run_pipeline(selected_transcripts, progress_callback=update_progress)

    progress_bar.progress(1.0)
    status_text.markdown("<span style='color:#1A7A4A; font-size:0.85rem;'>✅ Analysis complete</span>", unsafe_allow_html=True)
    st.session_state.results = results
    time.sleep(0.5)
    st.rerun()


# ── RESULTS DASHBOARD ─────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    calls = results["calls"]
    patterns = results.get("patterns", {})
    strategy = results.get("strategy", {})
    n = len(calls)

    # ── TOP METRICS ──────────────────────────────────────────────────────────
    outcomes = [c["meta"]["outcome"] for c in calls]
    won = sum(1 for o in outcomes if "Won" in o or "Demo" in o or "Pilot" in o)
    avg_eng = round(sum(c["sentiment"].get("buyer_engagement_score", 5) for c in calls) / n, 1)
    total_obj = sum(len(c["themes"].get("objections", [])) for c in calls)
    res_obj = sum(sum(1 for o in c["themes"].get("objections", []) if o.get("resolved")) for c in calls)
    res_rate = round((res_obj / total_obj * 100) if total_obj else 0)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="val">{n}</div><div class="label">Calls Analyzed</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="val">{won}/{n}</div><div class="label">Positive Outcomes</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="val">{avg_eng}/10</div><div class="label">Avg Buyer Engagement</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="val">{res_rate}%</div><div class="label">Objection Resolution Rate</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Call Analysis", "🔍 Pain Points & Themes",
        "📊 Sentiment & Momentum", "🧠 Cross-Call Patterns", "💡 Strategy"
    ])


    # ── TAB 1: CALL ANALYSIS ─────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Individual Call Breakdown</div>', unsafe_allow_html=True)

        outcome_color_map = {
            "Closed Won": "won", "Moved to Demo": "", "Requested Pilot": "",
            "Still Active": "active", "Lost — Budget Freeze": "lost"
        }

        for call in calls:
            meta = call["meta"]
            themes = call.get("themes", {})
            sentiment = call.get("sentiment", {})
            ingestion = call.get("ingestion", {})
            oc = meta.get("outcome", "")
            card_class = outcome_color_map.get(oc, "")
            eng = sentiment.get("buyer_engagement_score", "-")

            with st.expander(f"**{meta['title']}** · {meta['stage']} · {oc}", expanded=False):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"**Deal Context:** {ingestion.get('deal_context','')}")
                    st.markdown(f"**Next Step:** {sentiment.get('next_step_clarity','')}")

                    pps = themes.get("primary_pain_points", [])
                    if pps:
                        badges = ""
                        for p in pps:
                            sev = p.get("severity","Medium")
                            cls = "critical" if sev == "Critical" else "high" if sev == "High" else ""
                            badges += f'<span class="pain-badge {cls}">{p["theme"]}</span>'
                        st.markdown(f"**Pain Points:** {badges}", unsafe_allow_html=True)

                    quotes = [p.get("buyer_quote","") for p in pps if p.get("buyer_quote")]
                    if quotes:
                        st.markdown(f'<div class="quote-block">"{quotes[0]}"</div>', unsafe_allow_html=True)

                with c2:
                    st.metric("Engagement", f"{eng}/10")
                    st.metric("Objections", f"{len(themes.get('objections', []))} raised")
                    trust = sentiment.get("trust_signals", [])
                    if trust:
                        st.markdown(f"**Trust built:** {trust[0]}")

                # Critical moments
                moments = ingestion.get("critical_moments", [])
                if moments:
                    st.markdown("**Key Moments:**")
                    for m in moments[:3]:
                        st.markdown(f"→ {m}")

                # Seller effectiveness
                eff = sentiment.get("seller_effectiveness", {})
                if eff:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("✅ **Seller strengths:**")
                        for s in eff.get("strengths", [])[:2]:
                            st.markdown(f"- {s}")
                    with col_b:
                        st.markdown("⚠️ **Missed opportunities:**")
                        for m in eff.get("missed_opportunities", [])[:2]:
                            st.markdown(f"- {m}")


    # ── TAB 2: PAIN POINTS ───────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">Thematic Analysis — Buyer Pain Points Across All Calls</div>', unsafe_allow_html=True)

        # Aggregate all pain points
        all_pain = {}
        for call in calls:
            for p in call["themes"].get("primary_pain_points", []):
                theme = p.get("theme","")
                sev = p.get("severity", "Medium")
                if theme not in all_pain:
                    all_pain[theme] = {"count": 0, "severity": sev, "quotes": [], "descriptions": []}
                all_pain[theme]["count"] += 1
                if p.get("buyer_quote"):
                    all_pain[theme]["quotes"].append(p["buyer_quote"])
                if p.get("description"):
                    all_pain[theme]["descriptions"].append(p["description"])

        sorted_pain = sorted(all_pain.items(), key=lambda x: x[1]["count"], reverse=True)

        if sorted_pain:
            # Frequency chart
            themes_list = [x[0] for x in sorted_pain]
            counts = [x[1]["count"] for x in sorted_pain]
            sev_colors = [
                "#C0392B" if all_pain[t]["severity"] == "Critical"
                else "#E67E22" if all_pain[t]["severity"] == "High"
                else "#2E75B6"
                for t in themes_list
            ]

            fig = go.Figure(go.Bar(
                x=counts, y=themes_list, orientation='h',
                marker_color=sev_colors,
                text=counts, textposition='outside',
            ))
            fig.update_layout(
                title="Pain Point Frequency (colored by severity)",
                xaxis_title="Number of Calls", yaxis_title="",
                height=max(300, len(themes_list)*45),
                plot_bgcolor='white', paper_bgcolor='white',
                margin=dict(l=10, r=40, t=40, b=20),
                font=dict(family="Inter", size=11)
            )
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

            # Deep dive per theme
            st.markdown("---")
            st.markdown('<div class="section-title">Deep Dive by Theme</div>', unsafe_allow_html=True)
            for theme, data in sorted_pain[:6]:
                with st.expander(f"**{theme}** — {data['count']} of {n} calls · Severity: {data['severity']}"):
                    if data["descriptions"]:
                        for d in data["descriptions"][:2]:
                            st.markdown(f"_{d}_")
                    if data["quotes"]:
                        for q in data["quotes"][:2]:
                            st.markdown(f'<div class="quote-block">"{q}"</div>', unsafe_allow_html=True)

        # Unspoken fears
        all_fears = []
        for call in calls:
            all_fears.extend(call["themes"].get("unspoken_fears", []))
        if all_fears:
            st.markdown("---")
            st.markdown('<div class="section-title">Unspoken Fears (what buyers worry about but don\'t say)</div>', unsafe_allow_html=True)
            for f in all_fears[:6]:
                st.markdown(f"• {f}")

        # Buying triggers
        all_triggers = []
        for call in calls:
            all_triggers.extend(call["themes"].get("buying_triggers", []))
        if all_triggers:
            st.markdown("---")
            st.markdown('<div class="section-title">Buying Triggers — What Makes Them Say Yes</div>', unsafe_allow_html=True)
            for t in all_triggers[:6]:
                st.markdown(f"• {t}")


    # ── TAB 3: SENTIMENT ─────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-title">Sentiment & Deal Momentum</div>', unsafe_allow_html=True)

        # Engagement bar chart
        call_titles = [c["meta"]["title"][:30] + "..." for c in calls]
        eng_scores = [c["sentiment"].get("buyer_engagement_score", 5) for c in calls]
        sentiments = [c["sentiment"].get("overall_sentiment", "Neutral") for c in calls]
        sent_colors = {
            "Positive": "#1A7A4A", "Neutral": "#2E75B6",
            "Negative": "#C0392B", "Mixed": "#E67E22"
        }
        bar_colors = [sent_colors.get(s, "#2E75B6") for s in sentiments]

        fig = go.Figure(go.Bar(
            x=call_titles, y=eng_scores,
            marker_color=bar_colors,
            text=eng_scores, textposition='outside',
            customdata=sentiments,
            hovertemplate="<b>%{x}</b><br>Engagement: %{y}/10<br>Sentiment: %{customdata}<extra></extra>"
        ))
        fig.update_layout(
            title="Buyer Engagement Score by Call (colored by overall sentiment)",
            yaxis=dict(range=[0,11], title="Engagement Score"),
            xaxis_title="",
            plot_bgcolor='white', paper_bgcolor='white',
            height=350,
            font=dict(family="Inter", size=11),
            margin=dict(l=10, r=10, t=40, b=80)
        )
        fig.update_xaxes(tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

        # Momentum arcs
        st.markdown("---")
        st.markdown('<div class="section-title">Deal Momentum Arcs</div>', unsafe_allow_html=True)
        for call in calls:
            arcs = call["sentiment"].get("momentum_arc", [])
            if arcs:
                with st.expander(f"**{call['meta']['title']}** — {call['sentiment'].get('overall_sentiment','')}"):
                    for arc in arcs:
                        shift = arc.get("sentiment_shift","")
                        icon = "📈" if "up" in shift.lower() or "positive" in shift.lower() or "improv" in shift.lower() else "📉" if "down" in shift.lower() or "negative" in shift.lower() or "risk" in shift.lower() else "➡️"
                        st.markdown(f"{icon} **{arc.get('moment','')}** — {arc.get('cause','')}")

        # Risk signals across all calls
        all_risks = []
        for call in calls:
            risks = call["sentiment"].get("risk_signals", [])
            for r in risks:
                all_risks.append({"call": call["meta"]["title"][:25], "risk": r})

        if all_risks:
            st.markdown("---")
            st.markdown('<div class="section-title">Risk Signals Across Pipeline</div>', unsafe_allow_html=True)
            for r in all_risks[:8]:
                st.markdown(f"⚠️ **{r['call']}:** {r['risk']}")


    # ── TAB 4: PATTERNS ──────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-title">Cross-Call Intelligence — Patterns Invisible in Individual Calls</div>', unsafe_allow_html=True)

        # Universal pain points
        upps = patterns.get("top_universal_pain_points", [])
        if upps:
            st.markdown("#### Universal Pain Points")
            for p in upps:
                c1, c2 = st.columns([1,3])
                with c1:
                    st.markdown(f'<span class="tag">{p.get("frequency","")}</span>', unsafe_allow_html=True)
                    st.markdown(f"**{p.get('theme','')}**")
                with c2:
                    st.markdown(p.get("strategic_implication",""))
                st.markdown("---")

        # ICP
        icp = patterns.get("ideal_customer_profile", {})
        if icp:
            st.markdown("#### Ideal Customer Profile")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**🟢 Buy Triggers**")
                for t in icp.get("triggers", []):
                    st.markdown(f"• {t}")
            with c2:
                st.markdown("**🔴 Disqualifiers**")
                for d in icp.get("disqualifiers", []):
                    st.markdown(f"• {d}")
            with c3:
                st.markdown("**👤 Champion Profile**")
                st.markdown(icp.get("champion_profile",""))

        # Competitive intel
        comp = patterns.get("competitive_intelligence", [])
        if comp:
            st.markdown("---")
            st.markdown("#### Competitive Intelligence")
            for c in comp:
                st.markdown(f"• {c}")

        # Objection patterns
        obj_patterns = patterns.get("objection_patterns", [])
        if obj_patterns:
            st.markdown("---")
            st.markdown("#### Objection Patterns & Winning Responses")
            for o in obj_patterns:
                with st.expander(f"**{o.get('objection_type','')}** — {o.get('frequency','')}"):
                    st.markdown(f"**Best response observed:** {o.get('best_response_observed','')}")

        # Talk tracks
        talk_tracks = patterns.get("recommended_talk_tracks", [])
        if talk_tracks:
            st.markdown("---")
            st.markdown("#### Recommended Talk Tracks")
            for tt in talk_tracks:
                st.markdown(f"**When:** {tt.get('situation','')}")
                st.markdown(f"**Approach:** {tt.get('recommended_approach','')}")
                st.markdown("")


    # ── TAB 5: STRATEGY ──────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">Executive Strategic Recommendations</div>', unsafe_allow_html=True)

        exec_sum = strategy.get("executive_summary","")
        if exec_sum:
            st.markdown(f"""
            <div style="background:#EEF4FF; border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:1.5rem; border-left:4px solid #2E75B6;">
            <div style="font-size:0.7rem; color:#2E75B6; font-weight:600; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.4rem;">Executive Summary</div>
            <div style="font-size:0.95rem; color:#1a1a1a; line-height:1.6;">{exec_sum}</div>
            </div>
            """, unsafe_allow_html=True)

        recs = strategy.get("strategic_recommendations", [])
        p_colors = {"P1": "#C0392B", "P2": "#E67E22", "P3": "#2E75B6"}
        if recs:
            for r in recs:
                p = r.get("priority","P2")
                pc = p_colors.get(p, "#2E75B6")
                st.markdown(f"""
                <div class="insight-card">
                  <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                    <span style="color:{pc}; font-weight:700; font-size:0.8rem;">{p}</span>
                    <span style="font-weight:600; font-size:0.95rem;">{r.get('recommendation','')}</span>
                    <span class="tag gray">{r.get('owner','')}</span>
                  </div>
                  <div style="font-size:0.82rem; color:#555;">
                    <b>Evidence:</b> {r.get('evidence','')}<br>
                    <b>Expected impact:</b> {r.get('expected_impact','')}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # Pipeline health
        ph = strategy.get("pipeline_health", {})
        if ph:
            st.markdown("---")
            st.markdown("#### Pipeline Health Assessment")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Assessment:** {ph.get('assessment','')}")
                st.markdown(f"**Risk Concentration:** {ph.get('risk_concentration','')}")
            with c2:
                st.markdown("**Immediate Actions:**")
                for a in ph.get("recommended_actions",[]):
                    st.markdown(f"→ {a}")

        # Product gaps + Messaging
        col1, col2 = st.columns(2)
        with col1:
            gaps = strategy.get("product_gaps",[])
            if gaps:
                st.markdown("---")
                st.markdown("#### Product Gaps")
                for g in gaps:
                    st.markdown(f"• {g}")
        with col2:
            msgs = strategy.get("messaging_opportunities",[])
            if msgs:
                st.markdown("---")
                st.markdown("#### Messaging Opportunities")
                for m in msgs:
                    st.markdown(f"• {m}")

        # PDF Download
        st.markdown("---")
        st.markdown("#### Export Report")
        if st.button("📄 Generate Executive PDF Report"):
            with st.spinner("Building report..."):
                pdf_bytes = generate_report(results)
            st.download_button(
                label="⬇️ Download SIGNAL Report (PDF)",
                data=pdf_bytes,
                file_name="SIGNAL_Executive_Report.pdf",
                mime="application/pdf"
            )

else:
    # Landing state
    st.markdown("""
    <div style="text-align:center; padding:4rem 2rem; color:#888;">
      <div style="font-size:3rem; margin-bottom:1rem;">📡</div>
      <h3 style="color:#0D2B55; margin-bottom:0.5rem;">Ready to Analyze</h3>
      <p>Select calls in the sidebar and hit <b>Run Analysis</b> to start the multi-agent pipeline.</p>
      <br>
      <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; margin-top:1rem;">
        <div style="background:white; border-radius:8px; padding:1rem 1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); min-width:180px;">
          <div style="font-size:1.5rem;">🔍</div>
          <div style="font-weight:600; font-size:0.85rem; margin-top:0.3rem;">Thematic Analysis</div>
          <div style="font-size:0.75rem; color:#aaa;">Qualitative coding at scale</div>
        </div>
        <div style="background:white; border-radius:8px; padding:1rem 1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); min-width:180px;">
          <div style="font-size:1.5rem;">📊</div>
          <div style="font-weight:600; font-size:0.85rem; margin-top:0.3rem;">Sentiment Tracking</div>
          <div style="font-size:0.75rem; color:#aaa;">Deal momentum analysis</div>
        </div>
        <div style="background:white; border-radius:8px; padding:1rem 1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); min-width:180px;">
          <div style="font-size:1.5rem;">🧠</div>
          <div style="font-weight:600; font-size:0.85rem; margin-top:0.3rem;">Pattern Synthesis</div>
          <div style="font-size:0.75rem; color:#aaa;">Cross-call intelligence</div>
        </div>
        <div style="background:white; border-radius:8px; padding:1rem 1.5rem; box-shadow:0 1px 4px rgba(0,0,0,0.08); min-width:180px;">
          <div style="font-size:1.5rem;">💡</div>
          <div style="font-weight:600; font-size:0.85rem; margin-top:0.3rem;">Strategic Advisory</div>
          <div style="font-size:0.75rem; color:#aaa;">Executive recommendations</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
