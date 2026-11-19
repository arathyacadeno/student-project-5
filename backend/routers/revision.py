import os
import json
import datetime
import requests
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Student, SkillProfile
from auth import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class RevisionNotesRequest(BaseModel):
    topic_name: str
    subject_name: Optional[str] = "General"


class PracticeQuestionItem(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


class RevisionNotesResponse(BaseModel):
    topic_name: str
    subject_name: str
    overview: str
    key_concepts: List[str]
    practical_example: str
    common_pitfalls: List[str]
    practice_questions: List[Dict[str, Any]]
    generated_at: str


def _generate_ai_revision_content(topic_name: str, subject_name: str) -> Dict[str, Any]:
    """Call Gemini to generate structured revision notes for a weak topic."""
    prompt = f"""You are an expert tutor creating targeted revision notes for a student who is struggling with:
Subject: {subject_name}
Topic: {topic_name}

Generate a concise, pedagogical revision note in valid JSON format with these exact keys:
{{
  "overview": "A clear, simple 2-3 sentence explanation of the topic without confusing jargon.",
  "key_concepts": [
    "Core concept 1 with key formula or principle",
    "Core concept 2",
    "Core concept 3"
  ],
  "practical_example": "A clear step-by-step example with code or calculation showing how to solve a problem in this topic.",
  "common_pitfalls": [
    "Common mistake students make and how to avoid it",
    "Second common misconception"
  ],
  "practice_questions": [
    {{
      "question": "Practice question 1?",
      "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
      "correct_answer": "B",
      "explanation": "Why B is correct."
    }},
    {{
      "question": "Practice question 2?",
      "options": ["A) opt 1", "B) opt 2", "C) opt 3", "D) opt 4"],
      "correct_answer": "A",
      "explanation": "Explanation here."
    }}
  ]
}}

Return ONLY valid JSON. Do not wrap in markdown quotes if possible."""

    api_key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        return _fallback_revision(topic_name, subject_name)

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1500,
            "responseMimeType": "application/json"
        }
    }

    models_to_try = [
        DEFAULT_GEMINI_MODEL,
        "gemini-3.8-flash",
        "gemini-3.5-flash",
    ]

    for model in models_to_try:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            res = requests.post(url, json=body, headers=headers, timeout=12)
            if res.status_code == 200:
                raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                # Parse JSON
                clean_json = raw_text.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                parsed = json.loads(clean_json.strip())
                return parsed
        except Exception:
            continue

    return _fallback_revision(topic_name, subject_name)


def _fallback_revision(topic_name: str, subject_name: str) -> Dict[str, Any]:
    return {
        "overview": f"{topic_name} is a fundamental concept in {subject_name}. Mastering it enables a solid foundation for advanced problem solving.",
        "key_concepts": [
            f"Understand the core definitions and axioms governing {topic_name}.",
            "Break down multi-step problems into modular components.",
            "Verify edge cases and constraints before arriving at final answers."
        ],
        "practical_example": f"Review standard textbook exercises for {topic_name}. Practice step-by-step substitution and verify with known solutions.",
        "common_pitfalls": [
            "Skipping foundational prerequisite concepts before tackling advanced formulas.",
            "Rushing through boundary condition checks."
        ],
        "practice_questions": [
            {
                "question": f"Which approach best characterizes problem-solving in {topic_name}?",
                "options": ["A) Guess and check", "B) Systematic step-by-step derivation", "C) Ignoring edge cases", "D) Memorizing answers without proofs"],
                "correct_answer": "B",
                "explanation": "Systematic step-by-step derivation ensures correctness across all test cases."
            }
        ]
    }


@router.post("/revision/generate", response_model=RevisionNotesResponse)
def generate_revision_notes(
    req: RevisionNotesRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Module 10: AI Revision Notes Generator.
    Produces simple explanations, important concepts, examples, and practice questions for a weak topic.
    """
    ai_content = _generate_ai_revision_content(req.topic_name, req.subject_name)

    return RevisionNotesResponse(
        topic_name=req.topic_name,
        subject_name=req.subject_name,
        overview=ai_content.get("overview", ""),
        key_concepts=ai_content.get("key_concepts", []),
        practical_example=ai_content.get("practical_example", ""),
        common_pitfalls=ai_content.get("common_pitfalls", []),
        practice_questions=ai_content.get("practice_questions", []),
        generated_at=datetime.datetime.utcnow().isoformat(),
    )
