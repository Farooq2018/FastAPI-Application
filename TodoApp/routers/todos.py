from fastapi import Depends, APIRouter, Request, Form
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette import status
from ..models import Base, Todos
from ..database import engine, SessionLocal
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="TodoApp/templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    todos = db.query(Todos).filter(Todos.owner_id == 1).all()

    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request):
    return templates.TemplateResponse("add-todo.html", {"request": request})


@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(title: str = Form(...), description: str = Form(...),
                      priority: int = Form(...), db: Session = Depends(get_db)):
    todo_model = Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority
    todo_model.complete = False
    todo_model.owner_id = 1

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo})


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, title: str = Form(...),
                           description: str = Form(...), priority: int = Form(...),
                           db: Session = Depends(get_db)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    todo_model.title = title
    todo_model.description = description
    todo_model.priority = priority

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
