"""
Basic smoke tests for SIGNAL pipeline.
Run: python tests.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from data.transcripts import TRANSCRIPTS

def test_transcripts_loaded():
    assert len(TRANSCRIPTS) == 6, f"Expected 6 transcripts, got {len(TRANSCRIPTS)}"
    for t in TRANSCRIPTS:
        assert "transcript" in t
        assert "stage" in t
        assert len(t["transcript"]) > 200
    print(f"✅ {len(TRANSCRIPTS)} transcripts loaded and valid")

def test_transcript_metadata():
    required = ["id","title","date","stage","outcome","duration_min","participants"]
    for t in TRANSCRIPTS:
        for key in required:
            assert key in t, f"Missing key '{key}' in {t.get('id','?')}"
    print("✅ All transcript metadata fields present")

if __name__ == "__main__":
    test_transcripts_loaded()
    test_transcript_metadata()
    print("\n✅ All tests passed")
