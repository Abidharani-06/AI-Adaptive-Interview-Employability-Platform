def select_next_difficulty(previous_score):
    """
    Select the difficulty of the next interview question
    based on the candidate's previous answer score.
    """

    if previous_score < 0.40:
        return "Easy"

    elif previous_score < 0.70:
        return "Medium"

    else:
        return "Hard"


if __name__ == "__main__":

    test_scores = [0.30, 0.55, 0.85]

    print("Adaptive Difficulty Selection")
    print("-----------------------------")

    for score in test_scores:

        difficulty = select_next_difficulty(score)

        print(
            f"Previous Score: {score:.2f} "
            f"-> Next Difficulty: {difficulty}"
        )