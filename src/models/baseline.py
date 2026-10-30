
from sklearn.linear_model import LogisticRegression


def create_baseline(random_state: int = 42) -> LogisticRegression:
    """Create the Logistic Regression baseline."""

    return LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=random_state,
    )
