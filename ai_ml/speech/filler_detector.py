"""
Filler Word Detection Module
----------------------------
Analyzes spoken transcripts for common filler words and phrases.
Measures filler word count, density (per 100 words), and frequency breakdown.

IMPORTANT:
Does NOT diagnose nervousness, hesitation as a psychological defect, or lack of confidence.
Measures strictly observable lexical occurrences in the spoken response.
"""

import re
from typing import Dict, List, Optional, Tuple, Any

DEFAULT_FILLER_WORDS = [
    # Single-word vocalized fillers
    "um",
    "uh",
    "er",
    "ah",
    "like",
    "actually",
    "basically",
    "literally",
    "honestly",
    "right",
    # Multi-word filler phrases
    "you know",
    "i mean",
    "sort of",
    "kind of",
    "as in"
]


class FillerDetector:
    """
    Detects and quantifies observable filler words and filler phrases in speech transcripts.
    """

    def __init__(self, custom_fillers: Optional[List[str]] = None):
        """
        Parameters:
        - custom_fillers: Optional list of additional or replacement filler words/phrases.
        """
        fillers = list(DEFAULT_FILLER_WORDS)
        if custom_fillers:
            for f in custom_fillers:
                f_norm = f.strip().lower()
                if f_norm and f_norm not in fillers:
                    fillers.append(f_norm)

        # Sort fillers by length descending so multi-word phrases match before single words
        self.phrase_fillers = [f for f in fillers if " " in f]
        self.phrase_fillers.sort(key=len, reverse=True)
        self.single_fillers = set(f for f in fillers if " " not in f)

    def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyzes transcript for filler words and phrases.

        Returns:
        - Dictionary with filler count, fillers_per_100_words, detected_fillers breakdown, and feedback.
        """
        if not transcript or not transcript.strip():
            return {
                "total_words": 0,
                "filler_count": 0,
                "fillers_per_100_words": 0.0,
                "detected_fillers": {},
                "most_frequent_fillers": [],
                "density_category": "none",
                "feedback": "No spoken words provided for filler analysis."
            }

        text = transcript.lower()
        detected_counts: Dict[str, int] = {}
        filler_instances = 0

        # Step 1: Detect multi-word filler phrases first
        temp_text = text
        for phrase in self.phrase_fillers:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            matches = re.findall(pattern, temp_text)
            if matches:
                count = len(matches)
                detected_counts[phrase] = count
                filler_instances += count
                # Replace with placeholder to prevent sub-word matching
                temp_text = re.sub(pattern, " __FILLER__ ", temp_text)

        # Step 2: Tokenize remaining text into words
        raw_words = re.findall(r'\b[a-zA-Z\']+\b', temp_text)
        total_word_count = len(re.findall(r'\b[a-zA-Z\']+\b', text))

        for word in raw_words:
            if word in self.single_fillers:
                detected_counts[word] = detected_counts.get(word, 0) + 1
                filler_instances += 1

        fillers_per_100 = round((filler_instances / max(1, total_word_count)) * 100, 2)
        sorted_fillers = sorted(detected_counts.items(), key=lambda x: x[1], reverse=True)

        # Objective, non-psychological density categorization
        if fillers_per_100 <= 1.5:
            density_cat = "minimal"
            feedback = f"Minimal filler word usage observed ({fillers_per_100} per 100 words)."
        elif fillers_per_100 <= 4.0:
            density_cat = "moderate"
            top_words = ", ".join([f"'{k}'" for k, _ in sorted_fillers[:2]])
            feedback = f"Moderate filler word frequency observed ({fillers_per_100} per 100 words; primarily {top_words})."
        else:
            density_cat = "frequent"
            top_words = ", ".join([f"'{k}'" for k, _ in sorted_fillers[:3]])
            feedback = f"Noticeable presence of filler words observed ({fillers_per_100} per 100 words; common items: {top_words})."

        return {
            "total_words": total_word_count,
            "filler_count": filler_instances,
            "fillers_per_100_words": fillers_per_100,
            "detected_fillers": dict(detected_counts),
            "most_frequent_fillers": sorted_fillers,
            "density_category": density_cat,
            "feedback": feedback
        }
