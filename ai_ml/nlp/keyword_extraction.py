import re
from collections import Counter


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "also", "really", "just", "well"
}


def tokenize(text):
    """Clean and extract alphanumeric word tokens."""
    if not text:
        return []
    cleaned = re.sub(r"[^a-zA-Z0-9\s\-]", " ", str(text).lower())
    words = [w.strip() for w in cleaned.split() if w.strip()]
    return words


def extract_keywords(text, top_n=6):
    """
    Extract meaningful topical keywords from text using frequency
    and stopword exclusion.
    """
    tokens = tokenize(text)
    filtered = [t for t in tokens if len(t) > 2 and t not in STOPWORDS]
    if not filtered:
        return []

    counts = Counter(filtered)
    most_common = [word for word, _ in counts.most_common(top_n)]
    return most_common


CONCEPT_SYNONYMS = {
    "situation": ["when", "during", "project", "context", "background", "while", "team", "college", "scenario"],
    "task": ["task", "responsibility", "goal", "objective", "assigned", "required", "aim", "deliverable"],
    "action": ["implemented", "developed", "designed", "created", "built", "coded", "analyzed", "researched", "refactored", "debugged", "optimized", "stepped in", "approach"],
    "result": ["result", "outcome", "impact", "reduced", "improved", "increased", "achieved", "delivered", "deployed", "completed", "saved", "launched", "feedback", "learned"],
    "outcome": ["result", "outcome", "impact", "reduced", "improved", "increased", "achieved", "delivered", "deployed", "completed", "saved", "launched", "feedback", "learned"],
    "challenge": ["challenge", "roadblock", "issue", "problem", "bottleneck", "bug", "latency", "obstacle", "difficult", "struggle", "failure"],
    "solution": ["solution", "solved", "resolved", "fixed", "optimized", "debugged", "implemented", "refactored"],
    "learning": ["learned", "takeaway", "lesson", "growth", "understanding", "retrospective"],
    "disagreement": ["disagreement", "conflict", "differing", "disagreed", "opposing", "debate", "argument"],
    "teamwork": ["team", "teammate", "collaboration", "collaborative", "peer", "pair", "group"],
    "resolution": ["resolution", "resolved", "agreed", "consensus", "compromise", "settled", "alignment"],
    "pressure": ["pressure", "tight", "deadline", "urgent", "priority", "competing", "stress", "fast-paced"],
    "leadership": ["leadership", "led", "initiative", "lead", "ownership", "guided", "coordinated", "organized"],
    "motivation": ["motivated", "motivation", "inspired", "pursue", "interest", "passion", "drive"],
    "contribution": ["contribution", "contributed", "role", "designed", "built", "coded", "responsible", "part"]
}


def check_concept_coverage(candidate_answer, expected_themes, star_components=None):
    """
    Check the proportion of expected concepts/themes covered in the candidate's answer.
    Accepts string (semicolon or comma delimited) or list of theme strings.
    Supports semantic synonym clusters and optional star_components.
    """
    if not candidate_answer:
        return 0.0, [], []

    if isinstance(expected_themes, str):
        themes = [
            t.strip().lower()
            for t in expected_themes.replace(";", ",").split(",")
            if t.strip()
        ]
    elif isinstance(expected_themes, (list, tuple)):
        themes = [str(t).strip().lower() for t in expected_themes if str(t).strip()]
    else:
        return 1.0, [], []

    if not themes:
        return 1.0, [], []

    answer_lower = str(candidate_answer).lower()
    matched = []
    missing = []

    def get_variants(t):
        t_clean = t.strip().lower()
        vars_set = {t_clean}
        # Common morphological suffixes in HR / behavioral keywords
        for sfx in ["work", "ing", "ment", "tion", "sion", "ed", "es", "s", "er", "able"]:
            if t_clean.endswith(sfx) and len(t_clean) - len(sfx) >= 3:
                root = t_clean[:-len(sfx)]
                vars_set.add(root)
                if sfx in ["tion", "sion"]:
                    vars_set.add(root + "e")
                    vars_set.add(root + "ed")
                    vars_set.add(root + "ing")
        return vars_set

    for theme in themes:
        # 1. Check star components if available
        if star_components:
            star_key = "result" if theme == "outcome" else theme
            if star_key in star_components and star_components[star_key]:
                matched.append(theme)
                continue

        # 2. Check concept synonym cluster if theme in dictionary
        synonyms = CONCEPT_SYNONYMS.get(theme, [])
        found = False
        for syn in synonyms:
            pattern = r"\b" + re.escape(syn)
            if re.search(pattern, answer_lower) or syn in answer_lower:
                found = True
                break

        # 3. Check exact word and morphological stem variants
        if not found:
            theme_vars = get_variants(theme)
            for v in theme_vars:
                pattern = r"\b" + re.escape(v)
                if re.search(pattern, answer_lower) or v in answer_lower:
                    found = True
                    break

        if found:
            matched.append(theme)
        else:
            missing.append(theme)

    coverage_ratio = len(matched) / len(themes)
    return round(coverage_ratio, 4), matched, missing



if __name__ == "__main__":
    sample_text = """
    In my previous project, I faced a major communication roadblock within the team.
    I took the initiative to set up daily standup meetings and encouraged active listening.
    As a result, we reached a compromise and delivered the software on schedule.
    """

    expected = "communication; active listening; compromise; result; team"

    print("=== KEYWORD EXTRACTION DEMO ===")
    kws = extract_keywords(sample_text)
    print("Extracted Keywords:", kws)

    ratio, matched, missing = check_concept_coverage(sample_text, expected)
    print(f"Coverage Ratio: {ratio * 100:.1f}%")
    print("Matched Concepts:", matched)
    print("Missing Concepts:", missing)
