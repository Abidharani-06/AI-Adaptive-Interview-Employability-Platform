import re

FILLER_WORDS = [
    "um", "uh", "like", "you know", "basically", "actually",
    "literally", "sort of", "kind of", "i mean", "to be honest",
    "obviously", "right", "anyway"
]


def count_words(text):
    """Count non-empty words in text."""
    if not text:
        return 0
    return len([w for w in text.strip().split() if w])


def evaluate_completeness(text, min_words=25, optimal_words=(40, 200), max_words=300):
    """
    Evaluate whether the candidate provided enough depth and structure
    without being excessively sparse or uninformative.
    """
    if not text or not str(text).strip():
        return 0.0, "Empty answer provided."

    words = count_words(text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = len(sentences)

    # Word count scoring curve
    if words < 10:
        score = 0.20
        feedback = "Answer is far too brief. Provide a thorough, structured explanation with concrete details."
    elif words < min_words:
        score = 0.40 + (words / min_words) * 0.20
        feedback = "Answer is somewhat brief. Elaborate further on your thought process and actions."
    elif optimal_words[0] <= words <= optimal_words[1]:
        # Ideal depth
        score = 0.85
        if sentence_count >= 2:
            score = 1.0
        feedback = "Good depth and well-developed response structure."
    elif words <= max_words:
        # Slightly long
        score = 0.80
        feedback = "Detailed response, though slightly verbose. Aim for crisp delivery."
    else:
        # Rambling
        score = 0.65
        feedback = "Response is excessively long and rambling. Focus on concise, high-impact points."

    # Multi-sentence bonus
    if sentence_count >= 3 and score < 0.95:
        score = min(1.0, score + 0.05)

    return round(score, 4), feedback


def evaluate_clarity(text):
    """
    Evaluate readability, sentence formation, and filler word density.
    Returns clarity score between 0.0 and 1.0 and detected filler issues.
    """
    if not text or not str(text).strip():
        return 0.0, ["No text to evaluate"]

    words = count_words(text)
    if words == 0:
        return 0.0, ["Empty response"]

    text_lower = text.lower()
    found_fillers = []

    for filler in FILLER_WORDS:
        # Match whole phrase or word
        pattern = r"\b" + re.escape(filler) + r"\b"
        occurrences = len(re.findall(pattern, text_lower))
        if occurrences > 0:
            found_fillers.append((filler, occurrences))

    total_filler_count = sum(cnt for _, cnt in found_fillers)
    filler_ratio = total_filler_count / max(1, words)

    # Base clarity from sentence capitalization and punctuation
    base_clarity = 0.90
    if not re.search(r"[.!?]", text):
        base_clarity -= 0.15

    # Penalize high filler word ratio (> 4% is distracting)
    if filler_ratio > 0.08:
        base_clarity -= 0.35
    elif filler_ratio > 0.04:
        base_clarity -= 0.20
    elif filler_ratio > 0.02:
        base_clarity -= 0.08

    clarity_score = max(0.20, min(1.0, base_clarity))
    return round(clarity_score, 4), found_fillers


def evaluate_conciseness(text, optimal_range=(35, 180)):
    """
    Evaluate whether the response is concise and punchy.
    Returns conciseness score (0.0 to 1.0).
    """
    words = count_words(text)
    if words == 0:
        return 0.0

    low, high = optimal_range
    if low <= words <= high:
        return 1.0
    elif words < low:
        return round(max(0.3, words / low), 4)
    else:
        overshoot = words - high
        penalty = min(0.6, (overshoot / 150) * 0.5)
        return round(max(0.4, 1.0 - penalty), 4)


if __name__ == "__main__":
    t_good = "In my final year project, I served as the team lead. I coordinated the task allocations, set up git workflows, and ensured code reviews were conducted weekly. This allowed us to deploy the prototype two weeks ahead of schedule."
    t_sparse = "I did the project with my friends."
    t_filler = "Um, basically, like, we had a problem, and you know, actually I just like, fixed the database because, like, it was slow."

    print("=== COMPLETENESS & CLARITY DEMO ===")
    for label, text in [("Good", t_good), ("Sparse", t_sparse), ("Filler", t_filler)]:
        comp, comp_fb = evaluate_completeness(text)
        clar, fillers = evaluate_clarity(text)
        conc = evaluate_conciseness(text)
        print(f"\n[{label}] Text: {text}")
        print(f"  Completeness: {comp * 100:.1f}% ({comp_fb})")
        print(f"  Clarity     : {clar * 100:.1f}% (Fillers: {fillers})")
        print(f"  Conciseness : {conc * 100:.1f}%")
