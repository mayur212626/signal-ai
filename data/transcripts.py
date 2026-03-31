"""
Enterprise B2B sales call transcripts — Discovery calls
"""

TRANSCRIPTS = [
    {
        "id": "call_001",
        "title": "Discovery Call — Global Logistics Co.",
        "date": "2026-01-14",
        "stage": "Discovery",
        "outcome": "Moved to Demo",
        "duration_min": 38,
        "participants": {
            "seller": ["Marcus Webb (AE)", "Priya Nair (SE)"],
            "buyer": ["Tom Hartley (VP Operations)", "Dana Cruz (EHS Manager)"]
        },
        "transcript": """
Marcus: Tom, Dana, appreciate you both making time today. Before I dive in, I want to make sure we spend this call understanding your world before talking about ours. Can you give me a sense of what's top of mind in ops right now?

Tom: Yeah, so we're running four DCs, two in the southeast, one in Ohio, one in Nevada. Combined we're processing about 180,000 units a day. The honest answer is that our incident rate has been climbing. Q3 we had 14 recordable incidents, which is up from 9 the year before. Our insurance carrier is already asking questions and frankly so is our board.

Marcus: That 14 — are those concentrated in specific areas or spread across facilities?

Tom: Good question. Nevada and Ohio are the problem children. Both are high-velocity facilities — forklifts running constantly, mixed pedestrian zones, lots of shift overlap chaos. Dana, you want to add?

Dana: Yeah, the thing that keeps me up at night honestly isn't the incidents we're tracking — it's the near misses we're not. Our safety walks happen once a week. We have no visibility between those walks. By the time we know something is a pattern, someone's already gotten hurt.

Marcus: So visibility lag is the core problem. You know something's wrong after the fact.

Dana: Exactly. And our cameras — we have 200+ cameras across those two sites — they're basically just recording. Nobody's watching them. They're evidence after the incident, not prevention before it.
"""
    }
]
