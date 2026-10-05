import pandas as pd
import re


def clean_text(text):
    """
    Clean a candidate's interview answer.
    """

    # Convert to string
    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Remove special characters
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


if __name__ == "__main__":

    # Load candidate answers
    data = pd.read_csv("ai_ml/data/interview_answers.csv")

    print("Total answers:", len(data))

    # Clean candidate answers
    data["cleaned_answer"] = data["candidate_answer"].apply(clean_text)

    print("\nOriginal Answer:")
    print(data["candidate_answer"].iloc[0])

    print("\nCleaned Answer:")
    print(data["cleaned_answer"].iloc[0])