
from pydantic import BaseModel, EmailStr, ConfigDict

class StudentRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class StudentResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)



from pydantic import BaseModel, ConfigDict

class ProfileCreate(BaseModel):
    student_id: int
    course: str
    stream: str
    academic_level: str
    learning_goal: str

class ProfileResponse(ProfileCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)
