from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud, auth
from database import SessionLocal, engine, get_db
from datetime import timedelta

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Planner API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = auth.verify_token(token, credentials_exception)
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "админ":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges"
        )
    return current_user

@app.post("/token")
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# User endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.User).all()

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Project endpoints
@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    projects = crud.get_projects(db, skip=skip, limit=limit)
    return projects

@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    print(project.progress)
    # Check if user is allowed to create projects (e.g. admin or планировщик or руководитель)
    if current_user.role not in ["админ", "планировщик", "руководитель"]:
        raise HTTPException(status_code=403, detail="Not authorized to create projects")
    return crud.create_project(db=db, project=project)

@app.patch("/projects/{project_id}/status", response_model=schemas.Project)
def update_project_status(project_id: int, status_update: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Simple status update logic
    return crud.update_project_status(db=db, project_id=project_id, status=status_update)

@app.patch("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_project = crud.update_project(db=db, project_id=project_id, project=project)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

# MiniTasks and Problems
@app.post("/projects/{project_id}/tasks/", response_model=schemas.MiniTask)
def create_task_for_project(project_id: int, task: schemas.MiniTaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_mini_task(db=db, mini_task=task, project_id=project_id)

@app.post("/projects/{project_id}/problems/", response_model=schemas.Problem)
def create_problem_for_project(project_id: int, problem: schemas.ProblemCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_problem(db=db, problem=problem, project_id=project_id)
