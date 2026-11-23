"""
StudyMatch AI - Machine Learning Topic Strength Predictor
Loads the trained Random Forest Classifier bundle and provides real-time predictions.
"""
import os
import joblib
import pandas as pd
from typing import Dict, Any

MODEL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "topic_strength_rf.joblib")

_MODEL_BUNDLE = None


def get_model_bundle() -> Dict[str, Any]:
    global _MODEL_BUNDLE
    if _MODEL_BUNDLE is None:
        if not os.path.exists(MODEL_FILE):
            # If model file is not present, train it on the fly
            from ml.train_rf import train_model
            _MODEL_BUNDLE = train_model()
        else:
            _MODEL_BUNDLE = joblib.load(MODEL_FILE)
    return _MODEL_BUNDLE


def predict_topic_strength(
    score_pct: float,
    correct_answers: int,
    incorrect_answers: int,
    avg_time_per_q: float = 45.0,
    attempt_number: int = 1,
    historical_accuracy: float = None,
) -> Dict[str, Any]:
    """
    Accepts student quiz performance metrics and predicts topic strength
    using the trained Random Forest Classifier.

    Returns:
        dict: {
            "predicted_status": 'weak' | 'average' | 'strong',
            "confidence": float (0-100),
            "probabilities": {"weak": p0, "average": p1, "strong": p2},
            "features_used": {...}
        }
    """
    bundle = get_model_bundle()
    if historical_accuracy is None:
        historical_accuracy = score_pct
    rf = bundle["model"]
    feature_names = bundle["feature_names"]
    class_labels = bundle["class_labels"]

    input_df = pd.DataFrame([{
        "score_pct": float(score_pct),
        "correct_answers": int(correct_answers),
        "incorrect_answers": int(incorrect_answers),
        "avg_time_per_q": float(avg_time_per_q),
        "attempt_number": int(attempt_number),
        "historical_accuracy": float(historical_accuracy),
    }])[feature_names]

    # Predict class & probabilities
    pred_class_idx = int(rf.predict(input_df)[0])
    pred_probs = rf.predict_proba(input_df)[0]

    predicted_label = class_labels[pred_class_idx]
    confidence = float(pred_probs[pred_class_idx]) * 100.0

    probs_dict = {
        class_labels[i]: round(float(pred_probs[i]) * 100.0, 2)
        for i in range(len(class_labels))
    }

    return {
        "predicted_status": predicted_label,
        "confidence": round(confidence, 2),
        "probabilities": probs_dict,
        "features_used": input_df.to_dict(orient="records")[0],
    }
