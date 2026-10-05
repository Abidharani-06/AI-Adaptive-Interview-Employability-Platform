import pandas as pd


def generate_questions(topic, difficulty, number_of_questions=3):
    """
    Select interview questions based on topic and difficulty.
    """

    data = pd.read_csv("ai_ml/data/questions.csv")

    filtered_questions = data[
        (data["topic"].str.lower() == topic.lower()) &
        (data["difficulty"].str.lower() == difficulty.lower())
    ]

    if filtered_questions.empty:
        return []

    questions = filtered_questions.head(number_of_questions)

    return questions["question"].tolist()


if __name__ == "__main__":

    topic = "OOP"
    difficulty = "Medium"

    questions = generate_questions(
        topic,
        difficulty,
        number_of_questions=3
    )

    print("AI Question Generator")
    print("---------------------")
    print("Topic:", topic)
    print("Difficulty:", difficulty)

    print("\nGenerated Questions:")

    for number, question in enumerate(questions, start=1):
        print(f"{number}. {question}")
        