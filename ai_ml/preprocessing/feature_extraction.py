import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def extract_features(text_data):
    """
    Convert text into numerical TF-IDF features.
    """

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=100
    )

    features = vectorizer.fit_transform(text_data)

    return features, vectorizer


if __name__ == "__main__":

    # Load our interview question dataset
    data = pd.read_csv("ai_ml/data/questions.csv")

    # Extract questions
    questions = data["question"]

    # Convert questions into numerical features
    features, vectorizer = extract_features(questions)

    print("Number of questions:", len(questions))
    print("Feature matrix shape:", features.shape)

    print("\nSample extracted features:")
    print(features.toarray()[:2])