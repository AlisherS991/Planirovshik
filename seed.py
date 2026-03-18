from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, crud, schemas
from datetime import date

# Create tables
models.Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin = crud.get_user_by_email(db, "admin@planner.com")
        if not admin:
            admin_data = schemas.UserCreate(
                email="admin@planner.com",
                password="adminpassword123",
                name="Админ",
                surname="Системы",
                role="админ"
            )
            admin = crud.create_user(db, admin_data)
            print(f"Created admin user: {admin.email}")

        # Create other roles for testing
        users_to_create = [
            ("ivanov@planner.com", "Иванов", "А.С.", "руководитель"),
            ("petrova@planner.com", "Петрова", "Е.В.", "планировщик"),
            ("sidorov@planner.com", "Сидоров", "К.М.", "исполнитель"),
            ("kozlova@planner.com", "Козлова", "Н.П.", "главный исполнитель")
        ]

        created_users = {}
        for email, name, surname, role in users_to_create:
            user = crud.get_user_by_email(db, email)
            if not user:
                user_data = schemas.UserCreate(
                    email=email,
                    password="password123",
                    name=name,
                    surname=surname,
                    role=role
                )
                user = crud.create_user(db, user_data)
                print(f"Created user: {user.email} with role {user.role}")
            created_users[f"{name} {surname}"] = user

        # Seed projects if empty
        if len(crud.get_projects(db)) == 0:
            projects_data = [
                {
                    "title": 'Реновация офиса',
                    "date": date(2026, 2, 25),
                    "priority": 'Высокий',
                    "department": 'Департамент агрегации данных',
                    "resources": 12,
                    "performed": 'Испол.8/12',
                    "responsible_name": 'Иванов А.С.',
                    "budget": '2500000',
                    "status": 'problems',
                    "tasks": [
                        {'text': 'Демонтаж перегородок', 'done': True},
                        {'text': 'Закупка мебели', 'done': False},
                        {'text': 'Покраска стен', 'done': False}
                    ],
                    "problems": [
                        {'text': 'Задержка поставки материалов на 2 недели'},
                        {'text': 'Нехватка рабочих в ночную смену'}
                    ]
                },
                {
                    "title": 'Запуск маркетинга',
                    "date": date(2026, 3, 15),
                    "priority": 'Средний',
                    "department": 'Департамент агрегации данных',
                    "resources": 5,
                    "performed": 'Испол.2/5',
                    "responsible_name": 'Петрова Е.В.',
                    "budget": '1200000',
                    "status": 'inprogress',
                    "tasks": [
                        {'text': 'Утверждение концепции', 'done': True},
                        {'text': 'Создание креативов', 'done': True},
                        {'text': 'Запуск рекламы в соцсетях', 'done': False}
                    ],
                    "problems": []
                }
            ]

            for p_dict in projects_data:
                responsible_name = p_dict.get("responsible_name")
                if not responsible_name:
                    continue
                resp_user = created_users.get(str(responsible_name))
                if resp_user:
                    res_val = p_dict.get("resources", 0)
                    resources = int(res_val) if isinstance(res_val, (int, str)) else 0
                    
                    proj_schema = schemas.ProjectCreate(
                        title=str(p_dict.get("title", "")),
                        date=p_dict.get("date"),
                        priority=str(p_dict.get("priority", "")),
                        department=str(p_dict.get("department", "")),
                        resources=resources,
                        budget=str(p_dict.get("budget", "")),
                        status=str(p_dict.get("status", "")),
                        performed=str(p_dict.get("performed", "")),
                        responsible_id=resp_user.id
                    )
                    db_project = crud.create_project(db, proj_schema)
                    
                    tasks = p_dict.get("tasks", [])
                    if isinstance(tasks, list):
                        for t in tasks:
                            crud.create_mini_task(db, schemas.MiniTaskCreate(**t), db_project.id)
                    
                    problems = p_dict.get("problems", [])
                    if isinstance(problems, list):
                        for pr in problems:
                            crud.create_problem(db, schemas.ProblemCreate(**pr), db_project.id)
            
            print("Successfully seeded projects")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
