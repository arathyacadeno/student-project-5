
from sqlalchemy import Column, Integer, String
from database import Base

class Student(Base):

    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash = Column(String(255), nullable=False)

from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)

    student_id = Column(
        Integer,
        ForeignKey("students.id"),
        unique=True,
        nullable=False
    )

    course = Column(String(100))
    stream = Column(String(100))
    academic_level = Column(String(50))
    learning_goal = Column(String(255))
