"""
Honest evaluation of the topic-strength Random Forest.
Run from the backend folder:  python -m ml.evaluate_rf
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

from ml.train_rf import generate_training_data, FEATURE_NAMES, CLASS_LABELS
from ml.predictor import predict_topic_strength


def rule_baseline(score_pct):
    """Plain threshold rule. If the forest can't beat this, it adds nothing."""
    return np.where(score_pct < 50, 0, np.where(score_pct < 75, 1, 2))


def make_rf():
    return RandomForestClassifier(n_estimators=100, max_depth=6, min_samples_split=4,
                                  min_samples_leaf=2, random_state=42)


def main():
    df = generate_training_data(n_samples=1800, random_seed=42)
    X, y = df[FEATURE_NAMES], df["target"]

    print("=" * 60)
    print("1. Hold-out and cross-validation (synthetic data)")
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    rf = make_rf().fit(X_tr, y_tr)
    pred = rf.predict(X_te)
    print(f"Hold-out accuracy : {accuracy_score(y_te, pred):.3f}")
    print(f"Hold-out macro F1 : {f1_score(y_te, pred, average='macro'):.3f}")
    print("Confusion matrix (rows=true weak/avg/strong):")
    print(confusion_matrix(y_te, pred))
    cv = cross_val_score(make_rf(), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    print(f"5-fold CV accuracy: {cv.mean():.3f} +/- {cv.std():.3f}")

    print("=" * 60)
    print("2. Does the forest beat a simple score threshold?")
    base = rule_baseline(X_te["score_pct"].values)
    print(f"Threshold rule accuracy: {accuracy_score(y_te, base):.3f}")
    print(f"Random Forest accuracy : {accuracy_score(y_te, pred):.3f}")

    print("=" * 60)
    print("3. Forest trained on score_pct ONLY")
    rf1 = make_rf().fit(X_tr[["score_pct"]], y_tr)
    print(f"Accuracy: {accuracy_score(y_te, rf1.predict(X_te[['score_pct']])):.3f}")
    print("If this is close to the full model, the other features add almost nothing.")

    print("=" * 60)
    print("4. Robustness: add noise to test features")
    rng = np.random.default_rng(0)
    noisy = X_te.copy()
    noisy["score_pct"] = np.clip(noisy["score_pct"] + rng.normal(0, 8, len(noisy)), 0, 100)
    noisy["historical_accuracy"] = np.clip(noisy["historical_accuracy"] + rng.normal(0, 10, len(noisy)), 0, 100)
    print(f"Accuracy on noisy inputs: {accuracy_score(y_te, rf.predict(noisy)):.3f}")

    print("=" * 60)
    print("5. Real quiz attempts in your database")
    try:
        from database import SessionLocal
        from models import QuizAttempt
        db = SessionLocal()
        attempts = db.query(QuizAttempt).all()
        db.close()
        if not attempts:
            print("No attempts found.")
            return
        rows = []
        for a in attempts:
            pct = 100.0 * a.score / a.total_marks if a.total_marks else 0.0
            res = predict_topic_strength(
                score_pct=pct, correct_answers=int(a.score),
                incorrect_answers=int(a.total_marks - a.score),
                avg_time_per_q=(a.time_taken_sec or 0) / max(a.total_marks, 1),
                historical_accuracy=a.accuracy or pct)
            rows.append({"total_marks": a.total_marks, "pct": pct,
                         "model": res["predicted_status"],
                         "rule": CLASS_LABELS[int(rule_baseline(np.array([pct]))[0])],
                         "conf": res["confidence"]})
        r = pd.DataFrame(rows)
        print(f"Attempts: {len(r)}")
        print("Questions per quiz (total_marks):")
        print(r["total_marks"].value_counts().to_string())
        print(f"Model agrees with threshold rule: {(r['model'] == r['rule']).mean():.1%}")
        print(f"Mean confidence: {r['conf'].mean():.1f}%")
        print("Disagreements:")
        print(r[r["model"] != r["rule"]].head(10).to_string(index=False))
    except Exception as exc:
        print(f"Skipped (database unavailable): {exc}")


if __name__ == "__main__":
    main()