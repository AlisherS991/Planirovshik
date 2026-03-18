from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Date
from sqlalchemy.orm import relationship
from database import Base

# Association table for project performers
project_performers = Table(
    "project_performers",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("project_id", Integer, ForeignKey("projects.id"))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    role = Column(String)  # планировщик, исполнитель, главный исполнитель, руководитель, админ
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Projects where this user is the main responsible person
    responsible_projects = relationship("Project", back_populates="responsible_user")
    
    # Projects where this user is a performer
    projects = relationship("Project", secondary=project_performers, back_populates="performers")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    date = Column(Date)
    priority = Column(String)
    department = Column(String)
    resources = Column(Integer)
    budget = Column(String)
    description = Column(String)
    performed = Column(String) # e.g. "Испол.8/12"
    progress = Column(String)
    status = Column(String)  # plan, inprogress, problems
    
    responsible_id = Column(Integer, ForeignKey("users.id"))
    responsible_user = relationship("User", back_populates="responsible_projects")
    
    performers = relationship("User", secondary=project_performers, back_populates="projects")
    mini_tasks = relationship("MiniTask", back_populates="project", cascade="all, delete-orphan")
    problems = relationship("Problem", back_populates="project", cascade="all, delete-orphan")


class MiniTask(Base):
    __tablename__ = "mini_tasks"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    done = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="mini_tasks")

class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"))

    project = relationship("Project", back_populates="problems")
