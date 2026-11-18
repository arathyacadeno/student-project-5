
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import Student, StudentProfile
from schemas import ProfileCreate, ProfileResponse
from database import Base, engine, get_db
from models import Student
from schemas import StudentRegister, StudentResponse

app = FastAPI(title="StudyMatch AI")
from pydantic import BaseModel, EmailStr

class StudentLogin(BaseModel):
    email: EmailStr
    password: str
# React connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


@app.get("/")
def home():
    return {"message": "StudyMatch AI Backend Working"}


@app.post("/register", response_model=StudentResponse)
def register_student(
    student: StudentRegister,
    db: Session = Depends(get_db)
):

    existing = db.query(Student).filter(
        Student.email == student.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_student = Student(
        name=student.name,
        email=student.email,
        password_hash=pwd_context.hash(student.password)
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student





@app.post("/login")
def login_student(
    student: StudentLogin,
    db: Session = Depends(get_db)
):
    existing = db.query(Student).filter(
        Student.email == student.email
    ).first()

    if not existing:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not pwd_context.verify(
        student.password,
        existing.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "message": "Login successful",
        "student_id": existing.id,
        "name": existing.name,
        "email": existing.email
    }


@app.post("/profile", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db)
):
    existing_student = db.query(Student).filter(
        Student.id == profile.student_id
    ).first()

    if not existing_student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_profile = db.query(StudentProfile).filter(
        StudentProfile.student_id == profile.student_id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists"
        )

    new_profile = StudentProfile(**profile.model_dump())

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile
