"""
Observable Fluency and Speaking Rate Analysis Module
----------------------------------------------------
Calculates observable speech rate (Words Per Minute), vocal pacing,
and speech continuity metrics from transcripts and audio duration.

IMPORTANT:
Does NOT assess confidence, intelligence, personality, or psychological traits.
Measures strictly observable word counts, durations, and temporal delivery continuity.
"""

import re
from typing import Dict, Optional, Tuple, Any, List


class FluencyAnalyzer:
    """
    Analyzes observable speaking rate (WPM) and speech continuity metrics.
    """

    def __init__(
        self,
        ideal_wpm_min: float = 120.0,
        ideal_wpm_max: float = 160.0
    ):
        self.ideal_wpm_min = ideal_wpm_min
        self.ideal_wpm_max = ideal_wpm_max

    def analyze_fluency(
        self,
        transcript: str,
        duration_seconds: float,
        pause_metrics: Optional[Dict[str, Any]] = None,
        filler_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Computes speaking rate, pacing classification, and continuity metrics.

        Parameters:
        - transcript: Spoken text transcript.
        - duration_seconds: Total duration of spoken response in seconds.
        - pause_metrics: Optional dict from PauseAnalyzer.
        - filler_metrics: Optional dict from FillerDetector.
        """
        words = re.findall(r'\b[a-zA-Z\']+\b', transcript or "")
        word_count = len(words)
        dur = max(0.0, float(duration_seconds))

        if dur <= 0.5 or word_count == 0:
            return {
                "word_count": word_count,
                "duration_seconds": round(dur, 2),
                "words_per_minute": 0.0,
                "pacing_category": "insufficient_data",
                "speech_continuity_score": 0.0,
                "speech_continuity_percentage": 0.0,
                "feedback": "Insufficient spoken audio or text to evaluate speech rate."
            }

        wpm = (word_count / dur) * 60.0

        # Pacing classification (objective conversational bands)
        if wpm < 95.0:
            pacing_category = "deliberate_measured"
            pacing_desc = "measured and deliberate speaking pace"
        elif wpm <= 125.0:
            pacing_category = "calm_moderate"
            pacing_desc = "calm and controlled conversational pace"
        elif wpm <= 165.0:
            pacing_category = "conversational_standard"
            pacing_desc = "natural and standard conversational pacing"
        elif wpm <= 195.0:
            pacing_category = "energetic_brisk"
            pacing_desc = "brisk and rapid delivery pace"
        else:
            pacing_category = "rapid"
            pacing_desc = "fast delivery pace"

        # Rate stability / optimality factor: 1.0 within [110, 170], gradual falloff outside
        if 110.0 <= wpm <= 170.0:
            rate_factor = 1.0
        elif wpm < 110.0:
            rate_factor = max(0.4, wpm / 110.0)
        else:
            rate_factor = max(0.4, 1.0 - ((wpm - 170.0) / 100.0))

        # Active speech ratio contribution
        active_ratio = 0.75
        if pause_metrics and "speech_active_ratio" in pause_metrics:
            active_ratio = float(pause_metrics["speech_active_ratio"])

        # Filler penalty factor
        filler_penalty = 0.0
        if filler_metrics and "fillers_per_100_words" in filler_metrics:
            density = float(filler_metrics["fillers_per_100_words"])
            filler_penalty = min(0.35, density * 0.04)

        # Speech continuity score in [0.0, 1.0]
        continuity = max(0.0, min(1.0, (active_ratio * 0.5) + (rate_factor * 0.35) - filler_penalty + 0.15))

        feedback = f"Observable speaking rate was {wpm:.1f} WPM ({pacing_desc})."

        return {
            "word_count": word_count,
            "duration_seconds": round(dur, 2),
            "words_per_minute": round(wpm, 1),
            "pacing_category": pacing_category,
            "speech_continuity_score": round(continuity, 4),
            "speech_continuity_percentage": round(continuity * 100, 1),
            "feedback": feedback
        }
