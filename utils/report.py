"""
PDF Executive Report Generator for SIGNAL
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io, datetime

NAVY  = colors.HexColor("#0D2B55")
TEAL  = colors.HexColor("#2E75B6")
GREEN = colors.HexColor("#1A7A4A")
RED   = colors.HexColor("#C0392B")
GRAY  = colors.HexColor("#F4F6F9")
MID   = colors.HexColor("#555555")

def S(name, **kw):
    d = dict(fontName="Helvetica", fontSize=9, leading=12, spaceAfter=4,
             spaceBefore=0, textColor=colors.black, alignment=TA_LEFT)
    d.update(kw)
    return ParagraphStyle(name, **d)

def hr(color=NAVY):
    return HRFlowable(width="100%", thickness=1, color=color, spaceAfter=6, spaceBefore=2)

def section(title):
    return [
        Paragraph(title, S("sh", fontName="Helvetica-Bold", fontSize=11,
                            textColor=NAVY, spaceBefore=14, spaceAfter=2)),
        hr()
    ]

def badge(text, color):
    """Inline colored label."""
    return f'<font color="#{color}">[{text}]</font>'

def generate_report(results: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    now = datetime.datetime.now().strftime("%B %d, %Y")
    n_calls = results["meta"]["total_calls"]
    strategy = results.get("strategy", {})
    patterns = results.get("patterns", {})

    # ── COVER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("SIGNAL", S("logo", fontName="Helvetica-Bold", fontSize=28,
                                        textColor=NAVY, alignment=TA_CENTER)))
    story.append(Paragraph("Sales Intelligence & Gap Analysis Report",
                            S("sub", fontSize=12, textColor=MID, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph(f"Generated {now} · {n_calls} Enterprise Sales Calls Analyzed",
                            S("meta", fontSize=9, textColor=MID, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.15*inch))
    story.append(hr(TEAL))
    story.append(Spacer(1, 0.1*inch))

    # ── EXECUTIVE SUMMARY ────────────────────────────────────────────────────
    story += section("EXECUTIVE SUMMARY")
    exec_summary = strategy.get("executive_summary", "Analysis in progress.")
    story.append(Paragraph(exec_summary, S("body", fontSize=10, leading=14, alignment=TA_JUSTIFY)))
    story.append(Spacer(1, 0.1*inch))

    # Key metric
    km = strategy.get("key_metric_to_watch", "")
    if km:
        story.append(Paragraph(f"<b>Key Metric to Watch:</b> {km}",
                               S("km", fontSize=9, textColor=TEAL, spaceAfter=8)))

    # ── PIPELINE HEALTH ──────────────────────────────────────────────────────
    ph = strategy.get("pipeline_health", {})
    if ph:
        story += section("PIPELINE HEALTH")
        story.append(Paragraph(f"<b>Assessment:</b> {ph.get('assessment', '')}",
                               S("body", fontSize=9, leading=13)))
        story.append(Paragraph(f"<b>Risk Concentration:</b> {ph.get('risk_concentration', '')}",
                               S("body", fontSize=9, leading=13)))
        actions = ph.get("recommended_actions", [])
        for a in actions:
            story.append(Paragraph(f"• {a}", S("bul", fontSize=9, leftIndent=12, leading=12)))

    # ── CALL SUMMARIES ───────────────────────────────────────────────────────
    story += section(f"CALL-BY-CALL ANALYSIS ({n_calls} CALLS)")

    outcome_colors = {
        "Closed Won": "1A7A4A",
        "Moved to Demo": "2E75B6",
        "Requested Pilot": "2E75B6",
        "Still Active": "E67E22",
        "Lost — Budget Freeze": "C0392B",
    }

    for call in results["calls"]:
        meta = call["meta"]
        themes = call.get("themes", {})
        sentiment = call.get("sentiment", {})
        oc = meta.get("outcome", "")
        oc_color = outcome_colors.get(oc, "555555")
        eng = sentiment.get("buyer_engagement_score", "-")

        # Call header row
        data = [[
            Paragraph(f"<b>{meta['title']}</b>", S("ch", fontSize=9)),
            Paragraph(f"Stage: <b>{meta['stage']}</b>", S("cs", fontSize=8, alignment=TA_LEFT)),
            Paragraph(f'<font color="#{oc_color}"><b>{oc}</b></font>', S("co", fontSize=8)),
            Paragraph(f"Engagement: <b>{eng}/10</b>", S("ce", fontSize=8)),
        ]]
        t = Table(data, colWidths=[2.4*inch, 1.4*inch, 1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), GRAY),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (0,-1), 8),
            ("LEFTPADDING", (1,0), (-1,-1), 4),
            ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(t)

        # Pain points
        pps = themes.get("primary_pain_points", [])
        if pps:
            pp_text = " · ".join([f"<b>{p['theme']}</b> ({p.get('severity','')[:1]})" for p in pps[:3]])
            story.append(Paragraph(f"Pain Points: {pp_text}",
                                   S("pp", fontSize=8, textColor=MID, leftIndent=8, spaceAfter=2)))

        # Top quote
        for p in pps[:1]:
            q = p.get("buyer_quote", "")
            if q:
                story.append(Paragraph(f'<i>"{q[:120]}..."</i>',
                                       S("q", fontSize=8, textColor=MID, leftIndent=8, spaceAfter=2, fontName="Helvetica-Oblique")))

        # Objections
        objs = themes.get("objections", [])
        if objs:
            resolved = sum(1 for o in objs if o.get("resolved"))
            story.append(Paragraph(
                f"Objections: {len(objs)} raised · {resolved} resolved · Types: {', '.join(set(o.get('type','') for o in objs))}",
                S("oj", fontSize=8, textColor=MID, leftIndent=8, spaceAfter=6)))

        story.append(Spacer(1, 4))

    # ── CROSS-CALL PATTERNS ──────────────────────────────────────────────────
    story += section("CROSS-CALL PATTERNS & MARKET SIGNALS")

    # Universal pain points table
    upps = patterns.get("top_universal_pain_points", [])
    if upps:
        story.append(Paragraph("<b>Universal Pain Points</b>", S("sh2", fontSize=9, spaceAfter=3)))
        rows = [["Theme", "Frequency", "Strategic Implication"]]
        for p in upps:
            rows.append([
                Paragraph(f"<b>{p.get('theme','')}</b>", S("tc", fontSize=8)),
                Paragraph(p.get("frequency",""), S("tc", fontSize=8, textColor=TEAL)),
                Paragraph(p.get("strategic_implication",""), S("tc", fontSize=8, leading=11)),
            ])
        t = Table(rows, colWidths=[1.5*inch, 1.1*inch, 4.2*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), NAVY),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRAY]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#DDDDDD")),
        ]))
        story.append(t)
        story.append(Spacer(1, 8))

    # Market signals
    signals = patterns.get("market_signals", [])
    if signals:
        story.append(Paragraph("<b>Market Signals</b>", S("sh2", fontSize=9, spaceAfter=3)))
        for s in signals:
            story.append(Paragraph(
                f"• <b>{s.get('signal','')}</b> — {s.get('implication','')}",
                S("ms", fontSize=8, leftIndent=8, leading=12)))

    story.append(Spacer(1, 6))

    # Win/Loss patterns
    wl = patterns.get("win_loss_patterns", {})
    if wl:
        story.append(Paragraph("<b>Win/Loss Patterns</b>", S("sh2", fontSize=9, spaceAfter=3)))
        wins = wl.get("win_factors", [])
        losses = wl.get("loss_factors", [])
        rows = [[
            Paragraph("<b>Win Factors</b>", S("wh", fontSize=8, textColor=GREEN)),
            Paragraph("<b>Loss Factors</b>", S("lh", fontSize=8, textColor=RED))
        ]]
        max_rows = max(len(wins), len(losses))
        for i in range(max_rows):
            w = Paragraph(f"✓ {wins[i]}", S("wc", fontSize=8, textColor=GREEN)) if i < len(wins) else Paragraph("", S("e", fontSize=8))
            l = Paragraph(f"✗ {losses[i]}", S("lc", fontSize=8, textColor=RED)) if i < len(losses) else Paragraph("", S("e", fontSize=8))
            rows.append([w, l])
        t = Table(rows, colWidths=[3.4*inch, 3.4*inch])
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("LINEAFTER", (0,0), (0,-1), 0.5, colors.HexColor("#DDDDDD")),
        ]))
        story.append(t)

    # ── STRATEGIC RECOMMENDATIONS ────────────────────────────────────────────
    story += section("STRATEGIC RECOMMENDATIONS")
    recs = strategy.get("strategic_recommendations", [])
    p_colors = {"P1": "C0392B", "P2": "E67E22", "P3": "2E75B6"}
    for r in recs:
        p = r.get("priority", "P2")
        pc = p_colors.get(p, "555555")
        story.append(Paragraph(
            f'<font color="#{pc}"><b>[{p}]</b></font>  <b>{r.get("recommendation","")}</b>  '
            f'<font color="#555555">· Owner: {r.get("owner","")}</font>',
            S("rec", fontSize=9, spaceAfter=2)))
        story.append(Paragraph(
            f'Evidence: {r.get("evidence","")} · Impact: {r.get("expected_impact","")}',
            S("rece", fontSize=8, textColor=MID, leftIndent=16, spaceAfter=6)))

    # Product gaps
    gaps = strategy.get("product_gaps", [])
    if gaps:
        story.append(Paragraph("<b>Product Gaps Identified</b>", S("sh2", fontSize=9, spaceBefore=8, spaceAfter=3)))
        for g in gaps:
            story.append(Paragraph(f"• {g}", S("gap", fontSize=8, leftIndent=8, leading=12)))

    # Messaging
    msgs = strategy.get("messaging_opportunities", [])
    if msgs:
        story.append(Paragraph("<b>Messaging Opportunities</b>", S("sh2", fontSize=9, spaceBefore=8, spaceAfter=3)))
        for m in msgs:
            story.append(Paragraph(f"• {m}", S("msg", fontSize=8, leftIndent=8, leading=12)))

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.2*inch))
    story.append(hr(MID))
    story.append(Paragraph(
        f"SIGNAL · Confidential · {now} · {n_calls} calls · Multi-agent LLM analysis",
        S("foot", fontSize=7, textColor=MID, alignment=TA_CENTER)))

    doc.build(story)
    return buf.getvalue()
