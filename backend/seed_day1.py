"""
StudyMatch AI - Day 1 Curriculum Seed Script
Populates core Subjects and Topics according to the Module 3 specification.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Subject, Topic, Question

CURRICULUM_DATA = [
    {
        "name": "Python Programming",
        "code": "CS-101",
        "description": "Core computer programming fundamentals using Python 3.",
        "topics": [
            ("Variables & Expressions", 1, "Variable declarations, basic arithmetic expressions, and input/output."),
            ("Data Types & Collections", 2, "Lists, tuples, dictionaries, sets, and string manipulation."),
            ("Functions & Scope", 3, "User-defined functions, parameters, return values, and variable scope."),
            ("Loops & Control Flow", 4, "if/elif/else branching, while loops, for loops, and list comprehensions."),
            ("Object-Oriented Programming", 5, "Classes, objects, inheritance, polymorphism, and encapsulation."),
        ]
    },
    {
        "name": "Database Management Systems",
        "code": "CS-202",
        "description": "Relational database concepts, schema design, and SQL querying.",
        "topics": [
            ("SQL Fundamentals", 1, "SELECT, INSERT, UPDATE, DELETE queries and table constraints."),
            ("Table Joins", 2, "INNER JOIN, LEFT JOIN, RIGHT JOIN, and multi-table relationships."),
            ("Subqueries & Nested Queries", 3, "Correlated subqueries, EXISTS, IN, and scalar subqueries."),
            ("Schema Normalization", 4, "Functional dependencies, 1NF, 2NF, 3NF, and BCNF."),
            ("ACID Transactions", 5, "Atomicity, Consistency, Isolation, Durability, and database locks."),
        ]
    },
    {
        "name": "Machine Learning",
        "code": "AI-301",
        "description": "Supervised, unsupervised machine learning algorithms and evaluation.",
        "topics": [
            ("Linear & Logistic Regression", 1, "Cost functions, gradient descent, and classification boundaries."),
            ("Classification Algorithms", 2, "K-Nearest Neighbors, Naive Bayes, and Support Vector Machines."),
            ("K-Means Clustering", 3, "Unsupervised centroid-based clustering and elbow method."),
            ("Decision Trees & Ensembles", 4, "Information gain, entropy, Random Forests, and bagging."),
            ("Evaluation Metrics", 5, "Confusion matrix, Precision, Recall, F1-Score, and ROC-AUC curve."),
        ]
    },
    {
        "name": "Applied Mathematics",
        "code": "MATH-102",
        "description": "Mathematical foundations for science, engineering, and data analysis.",
        "topics": [
            ("Calculus & Limits", 1, "Continuity, derivatives, product rule, and chain rule."),
            ("Linear Algebra & Matrices", 2, "Matrix operations, eigenvalues, eigenvectors, and determinants."),
            ("Probability & Bayes Theorem", 3, "Conditional probability, independence, and Bayes theorem applications."),
            ("Descriptive Statistics", 4, "Mean, median, variance, standard deviation, and normal distributions."),
        ]
    },
    {
        "name": "Biological Sciences",
        "code": "BIO-101",
        "description": "Cellular biology, genetics, and organismal physiology.",
        "topics": [
            ("Cell Biology & Mitosis", 1, "Cell organelles, cellular respiration, mitosis, and meiosis."),
            ("Genetics & DNA", 2, "Mendelian genetics, DNA replication, transcription, and translation."),
            ("Plant Physiology", 3, "Photosynthesis, transpiration, and plant hormone signaling."),
            ("Human Anatomy", 4, "Circulatory, nervous, and endocrine body systems."),
        ]
    }
]


def seed_curriculum():
    db = SessionLocal()
    try:
        print("--- Seeding Subjects and Topics (Day 1) ---")
        for s_data in CURRICULUM_DATA:
            subject = db.query(Subject).filter(Subject.name == s_data["name"]).first()
            if not subject:
                subject = Subject(
                    name=s_data["name"],
                    code=s_data["code"],
                    description=s_data["description"]
                )
                db.add(subject)
                db.commit()
                db.refresh(subject)
                print(f"✓ Created Subject: {subject.name} ({subject.code})")
            else:
                print(f"• Subject exists: {subject.name}")

            for t_name, order_idx, desc in s_data["topics"]:
                topic = db.query(Topic).filter(
                    Topic.subject_id == subject.id,
                    Topic.name == t_name
                ).first()
                if not topic:
                    topic = Topic(
                        subject_id=subject.id,
                        name=t_name,
                        order_index=order_idx,
                        description=desc
                    )
                    db.add(topic)
                    db.commit()
                    db.refresh(topic)
                    print(f"  + Added Topic: {topic.name}")

        total_subjects = db.query(Subject).count()
        total_topics = db.query(Topic).count()
        print(f"\nSeeding complete! Total Subjects: {total_subjects}, Total Topics: {total_topics}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_curriculum()
