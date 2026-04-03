from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# MiniTask schemas
class MiniTaskBase(BaseModel):
    text: str
    done: bool = False

class MiniTaskCreate(MiniTaskBase):
    pass

class MiniTask(MiniTaskBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True

# Problem schemas
class ProblemBase(BaseModel):
    text: str

class ProblemCreate(ProblemBase):
    pass

class Problem(ProblemBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    name: str
    surname: str
    role: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Project schemas
class ProjectBase(BaseModel):
    title: str
    date: date
    priority: str
    department: Optional[str] = None
    resources: Optional[int] = None
    budget: Optional[str] = None
    description: Optional[str] = None
    performed: Optional[str] = None
    progress: Optional[str] = None
    status: str # 'plan', 'inprogress', 'problems'

class ProjectCreate(ProjectBase):
    responsible_ids: List[int] = []
    performer_ids: List[int] = []

class Project(ProjectBase):
    id: int
    responsible_ids: List[int] = []
    responsible_users: List[User] = []
    mini_tasks: List[MiniTask] = []
    problems: List[Problem] = []
    
    # We might want to return simplified performer info
    performers: List[User] = []

    class Config:
        from_attributes = True
