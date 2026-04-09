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
        status=project.status
    )
    
    # Add responsible users
    if project.responsible_ids:
        # Enforce 3 user limit for responsible
        ids = project.responsible_ids[:3]
        responsible_users = db.query(models.User).filter(models.User.id.in_(ids)).all()
        db_project.responsible_users = responsible_users
        if ids:
            db_project.responsible_id = ids[0] # Legacy support
            
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

def update_project(db: Session, project_id: int, project: schemas.ProjectUpdate):

    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        return None
    
    update_data = project.dict(exclude_unset=True)
    
    # Handle relationships
    if "responsible_ids" in update_data:
        ids = update_data.pop("responsible_ids")
        if ids:
            responsible_users = db.query(models.User).filter(models.User.id.in_(ids)).all()
            db_project.responsible_users = responsible_users
            db_project.responsible_id = ids[0]
        else:
            db_project.responsible_users = []
            db_project.responsible_id = None
            
    if "performer_ids" in update_data:
        ids = update_data.pop("performer_ids")
        performers = db.query(models.User).filter(models.User.id.in_(ids)).all()
        db_project.performers = performers

    if "mini_tasks" in update_data:
        tasks_data = update_data.pop("mini_tasks")
        db_project.mini_tasks = [models.MiniTask(**task_data) for task_data in tasks_data]

    if "problems" in update_data:
        problems_data = update_data.pop("problems")
        db_project.problems = [models.Problem(**problem_data) for problem_data in problems_data]

    for key, value in update_data.items():
        setattr(db_project, key, value)
        
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

def delete_project(db: Session, project_id: int):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project
