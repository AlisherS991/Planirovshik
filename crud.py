from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email, 
        hashed_password=hashed_password, 
        name=user.name, 
        surname=user.surname, 
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(
        title=project.title,
        date=project.date,
        priority=project.priority,
        department=project.department,
        resources=project.resources,
        budget=project.budget,
        description=project.description,
        performed=project.performed,
        progress=project.progress,
        status=project.status,
        responsible_id=project.responsible_id
    )
    
    # Add performers
    if project.performer_ids:
        performers = db.query(models.User).filter(models.User.id.in_(project.performer_ids)).all()
        db_project.performers = performers
        
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project_status(db: Session, project_id: int, status: str):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db_project.status = status
        db.commit()
        db.refresh(db_project)
    return db_project

def create_mini_task(db: Session, mini_task: schemas.MiniTaskCreate, project_id: int):
    db_mini_task = models.MiniTask(**mini_task.dict(), project_id=project_id)
    db.add(db_mini_task)
    db.commit()
    db.refresh(db_mini_task)
    return db_mini_task

def create_problem(db: Session, problem: schemas.ProblemCreate, project_id: int):
    db_problem = models.Problem(**problem.dict(), project_id=project_id)
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem
