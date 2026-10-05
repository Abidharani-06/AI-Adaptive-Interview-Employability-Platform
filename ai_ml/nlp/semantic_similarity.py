from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load a pretrained sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(expected_answer, candidate_answer):
    """
    Calculate semantic similarity between
    expected and candidate answers.
    """

    embeddings = model.encode([
        expected_answer,
        candidate_answer
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    return similarity


if __name__ == "__main__":

    expected_answer = """
    Inheritance allows a child class to acquire
    properties and methods from a parent class.
    """

    candidate_answer = """
    A derived class can reuse attributes and
    functions of its base class.
    """

    score = calculate_similarity(
        expected_answer,
        candidate_answer
    )

    print("Expected Answer:")
    print(expected_answer)

    print("\nCandidate Answer:")
    print(candidate_answer)

    print("\nSemantic Similarity Score:")
    print(round(score, 4))