"""
StudyMatch AI - Random Forest Topic Strength Classifier Training Pipeline
Uses Pandas, NumPy, Scikit-learn, and Joblib to train a Random Forest model
that classifies student topic performance into 'weak', 'average', or 'strong'.
"""
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_FILE = os.path.join(MODEL_DIR, "topic_strength_rf.joblib")

FEATURE_NAMES = [
    "score_pct",
    "correct_answers",
    "incorrect_answers",
    "avg_time_per_q",
    "attempt_number",
    "historical_accuracy",
]

CLASS_LABELS = {0: "weak", 1: "average", 2: "strong"}
LABEL_TO_INT = {"weak": 0, "average": 1, "strong": 2}


def generate_training_data(n_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Simulate realistic quiz records.

    Each student has a hidden true mastery (0-1) for a topic. Quiz results are
    noisy samples of it: correct answers ~ Binomial(n_questions, mastery), so short
    quizzes are unreliable. The label is the TRUE mastery band, NOT the quiz score band,
    so the model must combine score, history and speed instead of re-learning a threshold.
    """
    rng = np.random.default_rng(random_seed)

    records = []
    for _ in range(n_samples):
        tier = rng.choice(["weak", "average", "strong"], p=[0.35, 0.40, 0.25])
        loc, scale = {"weak": (0.33, 0.13), "average": (0.62, 0.09), "strong": (0.87, 0.07)}[tier]
        mastery = float(np.clip(rng.normal(loc, scale), 0.02, 0.99))

        n_q = int(rng.choice([3, 4, 5, 6, 8, 10]))
        attempt_num = int(rng.choice([1, 2, 3, 4], p=[0.55, 0.25, 0.15, 0.05]))

        # Current attempt plus earlier attempts, each a noisy sample of mastery
        accuracies = [rng.binomial(n_q, mastery) / n_q for _ in range(attempt_num)]
        correct = int(round(accuracies[-1] * n_q))
        incorrect = n_q - correct
        score_pct = accuracies[-1] * 100.0
        hist_acc = float(np.mean(accuracies) * 100.0)  # matches quiz.py: history includes this attempt

        # Stronger students tend to answer faster, but with a lot of individual variation
        avg_time = float(np.clip(rng.normal(70 - 45 * mastery, 18), 8, 120))

        # True label = hidden mastery band
        label = 0 if mastery < 0.50 else (1 if mastery < 0.75 else 2)

        records.append({
            "score_pct": round(score_pct, 2),
            "correct_answers": correct,
            "incorrect_answers": incorrect,
            "avg_time_per_q": round(avg_time, 2),
            "attempt_number": attempt_num,
            "historical_accuracy": round(hist_acc, 2),
            "target": label,
        })

    return pd.DataFrame(records)


def train_model():
    print("=" * 60)
    print("StudyMatch AI - Training Random Forest Topic Strength Model")
    print("=" * 60)

    # 1. Generate & prepare dataset
    df = generate_training_data(n_samples=1800, random_seed=42)
    print(f"Dataset generated: {len(df)} samples across 3 classes:")
    print(df["target"].value_counts().rename(index=CLASS_LABELS))

    X = df[FEATURE_NAMES]
    y = df["target"]

    # 2. Train-test split (80-20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"\nTrain set: {len(X_train)} samples | Test set: {len(X_test)} samples")

    # 3. Train Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
    )
    rf.fit(X_train, y_train)

    # 4. Evaluation
    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Evaluation Accuracy: {acc * 100:.2f}%\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Weak", "Average", "Strong"]))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Feature importances
    importances = pd.Series(rf.feature_importances_, index=FEATURE_NAMES).sort_values(ascending=False)
    print("\nFeature Importances:")
    for feat, imp in importances.items():
        print(f"  • {feat:20s}: {imp * 100:.2f}%")

    # 5. Save model bundle with Joblib
    bundle = {
        "model": rf,
        "feature_names": FEATURE_NAMES,
        "class_labels": CLASS_LABELS,
        "label_to_int": LABEL_TO_INT,
        "accuracy": acc,
        "version": "1.0.0",
    }
    joblib.dump(bundle, MODEL_FILE)
    print(f"\n✓ Trained model successfully saved to: {MODEL_FILE}")
    print("=" * 60)
    return bundle


if __name__ == "__main__":
    train_model()
