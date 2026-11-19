"""
StudyMatch AI - Day 2 Diagnostic Quiz Questions Seed Script
Seeds topic-specific multiple-choice questions for all academic topics.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Subject, Topic, Question

TOPIC_QUESTIONS = {
    # ── Python Programming ──
    "Variables & Expressions": [
        {
            "text": "Which of the following is an invalid variable name in Python?",
            "options": ["_score_100", "totalMarks", "2nd_attempt", "student_average"],
            "correct": 2,
            "explanation": "In Python, variable names cannot begin with a number.",
            "difficulty": "easy"
        },
        {
            "text": "What is the result of evaluating 17 // 4 + 17 % 4 in Python?",
            "options": ["5", "4", "6", "8"],
            "correct": 0,
            "explanation": "17 // 4 performs floor division yielding 4. 17 % 4 is 1. 4 + 1 = 5.",
            "difficulty": "medium"
        },
        {
            "text": "Which built-in Python function returns the memory address identity of an object?",
            "options": ["mem()", "id()", "address()", "ref()"],
            "correct": 1,
            "explanation": "id() returns an integer representing the object's unique memory identity.",
            "difficulty": "easy"
        }
    ],
    "Data Types & Collections": [
        {
            "text": "Which Python collection is mutable, ordered, and allows duplicate elements?",
            "options": ["tuple", "set", "list", "frozenset"],
            "correct": 2,
            "explanation": "Lists are mutable, ordered sequences that permit duplicate items.",
            "difficulty": "easy"
        },
        {
            "text": "What is the time complexity of searching for a key in a standard Python dictionary (on average)?",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"],
            "correct": 0,
            "explanation": "Python dictionaries are implemented using hash tables, giving average O(1) key lookup.",
            "difficulty": "medium"
        }
    ],
    "Functions & Scope": [
        {
            "text": "Which keyword is used inside a function to rebind a variable in the enclosing outer function scope?",
            "options": ["global", "nonlocal", "outer", "super"],
            "correct": 1,
            "explanation": "The 'nonlocal' keyword allows variables in an enclosing (non-global) scope to be modified.",
            "difficulty": "medium"
        },
        {
            "text": "What does a Python function return by default if no return statement is executed?",
            "options": ["0", "False", "None", "empty string ''"],
            "correct": 2,
            "explanation": "Functions without an explicit return statement return None.",
            "difficulty": "easy"
        }
    ],
    "Loops & Control Flow": [
        {
            "text": "What is the output of [x**2 for x in range(5) if x % 2 == 1]?",
            "options": ["[1, 9]", "[0, 4, 16]", "[1, 4, 9]", "[0, 1, 4, 9, 16]"],
            "correct": 0,
            "explanation": "Odd numbers in range(5) are 1 and 3. Their squares are 1 and 9.",
            "difficulty": "medium"
        },
        {
            "text": "When is the 'else' block of a Python for-loop executed?",
            "options": [
                "Only when a break statement is hit",
                "When the loop terminates naturally without hitting a break",
                "At the start of every iteration",
                "Only when an exception occurs"
            ],
            "correct": 1,
            "explanation": "A loop's 'else' block executes only if the loop finishes without encountering a 'break'.",
            "difficulty": "hard"
        }
    ],
    "Object-Oriented Programming": [
        {
            "text": "What is the primary purpose of Python's super() function?",
            "options": [
                "To create a singleton instance",
                "To delegate method calls to the parent/superclass in the MRO",
                "To free object memory immediately",
                "To make instance variables private"
            ],
            "correct": 1,
            "explanation": "super() delegates method access to the next class in the Method Resolution Order (MRO).",
            "difficulty": "medium"
        }
    ],

    # ── Database Management Systems ──
    "SQL Fundamentals": [
        {
            "text": "Which SQL clause is used to filter records aggregated by a GROUP BY clause?",
            "options": ["WHERE", "HAVING", "LIMIT", "ORDER BY"],
            "correct": 1,
            "explanation": "HAVING filters aggregated grouped results, whereas WHERE filters individual rows before grouping.",
            "difficulty": "easy"
        },
        {
            "text": "Which constraint ensures that a column cannot contain duplicate values while allowing NULLs?",
            "options": ["PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK"],
            "correct": 2,
            "explanation": "UNIQUE ensures distinct values across rows while typically allowing NULL values.",
            "difficulty": "easy"
        }
    ],
    "Table Joins": [
        {
            "text": "Which join returns all rows from the left table, and matched rows from the right table?",
            "options": ["INNER JOIN", "LEFT OUTER JOIN", "CROSS JOIN", "FULL OUTER JOIN"],
            "correct": 1,
            "explanation": "LEFT JOIN returns all rows from the left table, filling unmatched right-table columns with NULL.",
            "difficulty": "easy"
        },
        {
            "text": "If Table A has 5 rows and Table B has 4 rows, how many rows does a CROSS JOIN produce?",
            "options": ["9", "20", "5", "1"],
            "correct": 1,
            "explanation": "A Cartesian product / CROSS JOIN produces 5 * 4 = 20 rows.",
            "difficulty": "medium"
        }
    ],
    "Subqueries & Nested Queries": [
        {
            "text": "A subquery that references a column from the outer query is called a:",
            "options": ["Scalar subquery", "Correlated subquery", "Derived table", "Materialized query"],
            "correct": 1,
            "explanation": "A correlated subquery executes repeatedly for each candidate row evaluated by the outer query.",
            "difficulty": "medium"
        }
    ],
    "Schema Normalization": [
        {
            "text": "A relation is in Second Normal Form (2NF) if it is in 1NF and contains no:",
            "options": [
                "Transitive dependencies",
                "Partial dependencies on candidate keys",
                "Multi-valued attributes",
                "Null values"
            ],
            "correct": 1,
            "explanation": "2NF requires eliminating partial dependencies where non-prime attributes depend on part of a composite key.",
            "difficulty": "medium"
        },
        {
            "text": "Third Normal Form (3NF) strictly eliminates which type of dependency?",
            "options": ["Partial dependency", "Transitive dependency", "Join dependency", "Trivial dependency"],
            "correct": 1,
            "explanation": "3NF requires that no non-prime attribute is transitively dependent on any candidate key.",
            "difficulty": "hard"
        }
    ],
    "ACID Transactions": [
        {
            "text": "Which ACID property guarantees that all database updates in a transaction succeed together or all rollback?",
            "options": ["Atomicity", "Consistency", "Isolation", "Durability"],
            "correct": 0,
            "explanation": "Atomicity ensures an 'all-or-nothing' execution model for transaction operations.",
            "difficulty": "easy"
        }
    ],

    # ── Machine Learning ──
    "Linear & Logistic Regression": [
        {
            "text": "What activation function is used in Logistic Regression to map outputs between 0 and 1?",
            "options": ["ReLU", "Sigmoid", "Softmax", "Tanh"],
            "correct": 1,
            "explanation": "The sigmoid (logistic) function maps real-valued numbers into probabilities between 0 and 1.",
            "difficulty": "easy"
        },
        {
            "text": "Which loss function is minimized in standard Linear Regression?",
            "options": ["Binary Cross-Entropy", "Mean Squared Error (MSE)", "Hinge Loss", "Kullback-Leibler Divergence"],
            "correct": 1,
            "explanation": "Ordinary Least Squares / Linear Regression minimizes Mean Squared Error.",
            "difficulty": "easy"
        }
    ],
    "Classification Algorithms": [
        {
            "text": "Which classification algorithm is based on Bayes theorem with a 'naive' assumption of feature independence?",
            "options": ["Support Vector Machine", "Naive Bayes", "K-Nearest Neighbors", "Random Forest"],
            "correct": 1,
            "explanation": "Naive Bayes assumes all predictive features are conditionally independent given the class label.",
            "difficulty": "easy"
        },
        {
            "text": "In Support Vector Machines (SVM), what are support vectors?",
            "options": [
                "The data points that lie closest to the decision hyperplane",
                "The centroid of each class cluster",
                "Outliers that are pruned away",
                "The kernel transformation matrices"
            ],
            "correct": 0,
            "explanation": "Support vectors are critical data points that directly determine the position and margin of the hyperplane.",
            "difficulty": "medium"
        }
    ],
    "K-Means Clustering": [
        {
            "text": "Which graphical method is commonly used to find the optimal number of clusters 'k' in K-Means?",
            "options": ["Elbow Method", "ROC Curve", "Box Plot", "Pareto Chart"],
            "correct": 0,
            "explanation": "The Elbow Method plots within-cluster sum of squares (WCSS) to find the point where distortion levels off.",
            "difficulty": "easy"
        }
    ],
    "Decision Trees & Ensembles": [
        {
            "text": "What ensemble technique does a Random Forest use to combine multiple decision trees?",
            "options": ["Gradient Boosting", "Bagging (Bootstrap Aggregation)", "Stacking", "Cascading"],
            "correct": 1,
            "explanation": "Random Forests use Bagging alongside random feature subspace selection.",
            "difficulty": "medium"
        }
    ],
    "Evaluation Metrics": [
        {
            "text": "What is the formula for Precision in a classification problem?",
            "options": [
                "TP / (TP + FN)",
                "TP / (TP + FP)",
                "(TP + TN) / Total",
                "2 * (Precision * Recall) / (Precision + Recall)"
            ],
            "correct": 1,
            "explanation": "Precision measures true positives out of all predicted positives: TP / (TP + FP).",
            "difficulty": "medium"
        },
        {
            "text": "What metric represents the harmonic mean of Precision and Recall?",
            "options": ["Accuracy", "ROC-AUC", "F1-Score", "Specificity"],
            "correct": 2,
            "explanation": "The F1-Score is 2 * (Precision * Recall) / (Precision + Recall).",
            "difficulty": "easy"
        }
    ],

    # ── Applied Mathematics ──
    "Calculus & Limits": [
        {
            "text": "What is the derivative of f(x) = x * ln(x)?",
            "options": ["ln(x) + 1", "1 / x", "ln(x)", "x + 1"],
            "correct": 0,
            "explanation": "Using the product rule: f'(x) = 1*ln(x) + x*(1/x) = ln(x) + 1.",
            "difficulty": "medium"
        },
        {
            "text": "What is lim(x -> 0) of sin(x) / x?",
            "options": ["0", "1", "Infinity", "Undefined"],
            "correct": 1,
            "explanation": "A fundamental calculus limit: lim(x -> 0) sin(x)/x = 1.",
            "difficulty": "easy"
        }
    ],
    "Linear Algebra & Matrices": [
        {
            "text": "If a square matrix has a determinant equal to zero, the matrix is:",
            "options": ["Orthogonal", "Singular / Non-invertible", "Identity", "Symmetric"],
            "correct": 1,
            "explanation": "A determinant of zero means the matrix is singular and does not have an inverse.",
            "difficulty": "easy"
        }
    ],
    "Probability & Bayes Theorem": [
        {
            "text": "If events A and B are independent, what is P(A and B)?",
            "options": ["P(A) + P(B)", "P(A) * P(B)", "P(A | B)", "P(A) / P(B)"],
            "correct": 1,
            "explanation": "For independent events, the joint probability is the product of their individual probabilities.",
            "difficulty": "easy"
        }
    ],

    # ── Biological Sciences ──
    "Cell Biology & Mitosis": [
        {
            "text": "Which organelle is considered the 'powerhouse of the cell' where ATP synthesis occurs?",
            "options": ["Golgi apparatus", "Ribosome", "Mitochondria", "Lysosome"],
            "correct": 2,
            "explanation": "Mitochondria produce cellular ATP through oxidative phosphorylation.",
            "difficulty": "easy"
        },
        {
            "text": "In which phase of mitosis do sister chromatids separate and move to opposite poles?",
            "options": ["Prophase", "Metaphase", "Anaphase", "Telophase"],
            "correct": 2,
            "explanation": "During Anaphase, spindle fibers pull separated sister chromatids toward opposite poles.",
            "difficulty": "medium"
        }
    ],
    "Genetics & DNA": [
        {
            "text": "Which nitrogenous base pairs with Adenine in a double-stranded DNA molecule?",
            "options": ["Cytosine", "Thymine", "Guanine", "Uracil"],
            "correct": 1,
            "explanation": "In DNA, Adenine (A) forms two hydrogen bonds specifically with Thymine (T).",
            "difficulty": "easy"
        }
    ]
}


def seed_questions():
    db = SessionLocal()
    print("--- Seeding Topic Diagnostic Quiz Questions (Day 2) ---")
    try:
        total_added = 0
        for topic_name, q_list in TOPIC_QUESTIONS.items():
            topic = db.query(Topic).filter(Topic.name == topic_name).first()
            if not topic:
                print(f"⚠️ Topic not found: {topic_name}. Skipping questions.")
                continue

            for q_data in q_list:
                existing = db.query(Question).filter(
                    Question.topic_id == topic.id,
                    Question.question_text == q_data["text"]
                ).first()
                if not existing:
                    q = Question(
                        topic_id=topic.id,
                        question_text=q_data["text"],
                        options=q_data["options"],
                        correct_answer=q_data["correct"],
                        explanation=q_data["explanation"],
                        difficulty=q_data["difficulty"]
                    )
                    db.add(q)
                    total_added += 1

        db.commit()
        total_questions = db.query(Question).count()
        print(f"✓ Added {total_added} new questions. Total diagnostic questions in database: {total_questions}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_questions()
