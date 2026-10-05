import sys
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

_SHARED_MODEL = None


def get_embedding_model():
    """Lazy load SentenceTransformer singleton."""
    global _SHARED_MODEL
    if _SHARED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _SHARED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _SHARED_MODEL


def calculate_semantic_similarity(reference_text, candidate_answer):
    """
    Direct semantic similarity between reference context and candidate answer
    using SBERT embeddings and cosine similarity.
    Returns normalized score between 0.0 and 1.0.
    """
    if not candidate_answer or len(candidate_answer.strip()) < 5:
        return 0.0

    model = get_embedding_model()
    embeddings = model.encode([str(reference_text).strip(), str(candidate_answer).strip()])
    raw_sim = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])

    # Calibrate raw STS similarity for open-ended QA / interview dialogue:
    # Bi-encoder STS for narrative typically spans ~ 0.015 (unrelated) to ~ 0.15+ (highly focused)
    if raw_sim <= 0.02:
        calibrated = max(0.0, raw_sim / 0.02) * 0.20
    elif raw_sim <= 0.04:
        calibrated = 0.20 + ((raw_sim - 0.02) / 0.02) * 0.40
    elif raw_sim <= 0.08:
        calibrated = 0.60 + ((raw_sim - 0.04) / 0.04) * 0.25
    else:
        calibrated = min(1.0, 0.85 + ((raw_sim - 0.08) / 0.08) * 0.15)

    return round(max(0.0, min(1.0, calibrated)), 4)


def calculate_relevance(question_text, candidate_answer, expected_themes=None, star_components=None):
    """
    Calculate semantic relevance of candidate answer with respect to
    the question and any expected themes.
    Combines SBERT neural semantic similarity with concept coverage.
    Returns a normalized relevance score between 0.0 and 1.0.
    """
    if not candidate_answer or len(candidate_answer.strip()) < 5:
        return 0.0

    # 1. Clean semantic similarity between question prompt and candidate answer
    sem_score = calculate_semantic_similarity(question_text, candidate_answer)

    # 2. Blend with observed theme/keyword coverage if expected themes provided
    if expected_themes:
        try:
            current_dir = Path(__file__).resolve().parent
            if str(current_dir) not in sys.path:
                sys.path.append(str(current_dir))
            from keyword_extraction import check_concept_coverage
            coverage_ratio, _, _ = check_concept_coverage(
                candidate_answer,
                expected_themes,
                star_components=star_components
            )
            final_score = (sem_score * 0.65) + (coverage_ratio * 0.35)
        except Exception:
            final_score = sem_score
    else:
        final_score = sem_score

    # 3. If candidate structured a strong behavioral answer (STAR >= 3 components),
    # reinforce relevance alignment
    if star_components and sum(1 for v in star_components.values() if v) >= 3:
        final_score = max(final_score, min(0.98, final_score + 0.08))

    return round(max(0.0, min(1.0, final_score)), 4)


if __name__ == "__main__":
    q = "Describe a situation where you had a disagreement with a team member and how you resolved it."
    ans_good = "When working on our database architecture, a teammate wanted NoSQL while I preferred PostgreSQL. We benchmarked queries together, listened to each other's use cases, and agreed on a hybrid solution."
    ans_irrelevant = "I enjoy playing cricket on weekends and hanging out with my college friends."

    print("=== RELEVANCE TEST ===")
    score_good = calculate_relevance(q, ans_good, "teamwork; disagreement; resolution")
    score_bad = calculate_relevance(q, ans_irrelevant, "teamwork; disagreement; resolution")
    print(f"Good Answer Relevance : {score_good * 100:.1f}%")
    print(f"Irrelevant Answer Rel : {score_bad * 100:.1f}%")

