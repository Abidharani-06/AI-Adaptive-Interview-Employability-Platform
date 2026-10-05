import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# 1. LOAD DATASET
# ============================================================

data = pd.read_csv(
    "ai_ml/data/interview_answers.csv"
)

X_text = data["candidate_answer"]
y = data["answer_score"]


# ============================================================
# 2. TF-IDF FEATURE EXTRACTION
# ============================================================

vectorizer = TfidfVectorizer(
    stop_words="english"
)

X = vectorizer.fit_transform(X_text)


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42
)


# ============================================================
# 4. TRAIN ML MODEL
# ============================================================

model = LinearRegression()

model.fit(
    X_train,
    y_train
)


# ============================================================
# 5. MODEL EVALUATION
# ============================================================

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("===================================")
print("AI ANSWER EVALUATION MODEL")
print("===================================")

print(
    "Training samples:",
    X_train.shape[0]
)

print(
    "Testing samples:",
    X_test.shape[0]
)

print(
    "\nMean Absolute Error:",
    round(mae, 4)
)

print(
    "R2 Score:",
    round(r2, 4)
)


# ============================================================
# 6. LOAD SEMANTIC SIMILARITY MODEL
# ============================================================

semantic_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# 7. ANSWER EVALUATION FUNCTION
# ============================================================

def evaluate_answer(
    expected_answer,
    candidate_answer
):

    # --------------------------------------------------------
    # ML Prediction
    # --------------------------------------------------------

    new_features = vectorizer.transform(
        [candidate_answer]
    )

    ml_score = model.predict(
        new_features
    )[0]

    # Keep score between 0 and 1

    ml_score = max(
        0,
        min(1, ml_score)
    )


    # --------------------------------------------------------
    # Semantic Similarity
    # --------------------------------------------------------

    embeddings = semantic_model.encode([
        expected_answer,
        candidate_answer
    ])

    semantic_score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]


    # --------------------------------------------------------
    # Combined Score
    # --------------------------------------------------------

    final_score = (
        (ml_score * 0.4) +
        (semantic_score * 0.6)
    )


    return (
        ml_score,
        semantic_score,
        final_score
    )


# ============================================================
# 8. TEST THE ANSWER EVALUATION
# ============================================================

if __name__ == "__main__":

    expected_answer = """
    Object oriented programming is a programming paradigm
    based on classes and objects. It supports inheritance,
    polymorphism and encapsulation.
    """


    candidate_answer = """
    OOP uses classes and objects to organize programs.
    It supports inheritance and polymorphism.
    """


    # --------------------------------------------------------
    # Evaluate Candidate Answer
    # --------------------------------------------------------

    (
        ml_score,
        semantic_score,
        final_score
    ) = evaluate_answer(
        expected_answer,
        candidate_answer
    )


    # --------------------------------------------------------
    # Display Results
    # --------------------------------------------------------

    print("\n-----------------------------------")
    print("CANDIDATE ANSWER EVALUATION")
    print("-----------------------------------")

    print("\nExpected Answer:")
    print(
        expected_answer.strip()
    )

    print("\nCandidate Answer:")
    print(
        candidate_answer.strip()
    )

    print(
        "\nML Score:",
        round(ml_score, 4)
    )

    print(
        "Semantic Similarity:",
        round(semantic_score, 4)
    )

    print(
        "Final Answer Score:",
        round(final_score, 4)
    )

    print("-----------------------------------")