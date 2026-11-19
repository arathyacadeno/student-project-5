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
    Generate realistic labelled diagnostic quiz performance records.
    Considers score, accuracy, attempt progression, and problem-solving speed.
    """
    np.random.seed(random_seed)

    records = []
    # Distribute samples evenly across performance tiers with natural variance
    for _ in range(n_samples):
        profile_tier = np.random.choice(["weak", "average", "strong"], p=[0.35, 0.40, 0.25])
        attempt_num = np.random.choice([1, 2, 3, 4], p=[0.55, 0.25, 0.15, 0.05])

        if profile_tier == "weak":
            score_pct = np.clip(np.random.normal(loc=32, scale=12), 0, 49.9)
            correct = int(np.round(score_pct / 10))
            incorrect = 10 - correct
            avg_time = np.clip(np.random.normal(loc=65, scale=20), 15, 120)
            hist_acc = np.clip(np.random.normal(loc=30, scale=12), 0, 52)
            label = 0 # weak

        elif profile_tier == "average":
            score_pct = np.clip(np.random.normal(loc=62, scale=7), 50.0, 74.9)
            correct = int(np.round(score_pct / 10))
            incorrect = 10 - correct
            avg_time = np.clip(np.random.normal(loc=45, scale=15), 12, 90)
            hist_acc = np.clip(np.random.normal(loc=60, scale=8), 45, 75)
            label = 1 # average

        else: # strong
            score_pct = np.clip(np.random.normal(loc=88, scale=7), 75.0, 100.0)
            correct = int(np.round(score_pct / 10))
            incorrect = 10 - correct
            avg_time = np.clip(np.random.normal(loc=28, scale=10), 8, 60)
            hist_acc = np.clip(np.random.normal(loc=85, scale=7), 72, 100)
            label = 2 # strong

        records.append({
            "score_pct": float(round(score_pct, 2)),
            "correct_answers": int(correct),
            "incorrect_answers": int(incorrect),
            "avg_time_per_q": float(round(avg_time, 2)),
            "attempt_number": int(attempt_num),
            "historical_accuracy": float(round(hist_acc, 2)),
            "target": int(label),
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
