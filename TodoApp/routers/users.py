from fastapi import APIRouter, Depends, Request, Form
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from ..database import SessionLocal
from .auth import get_current_user, verify_password, get_password_hash
from ..models import Users
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={404: {'description': 'Not Found'}}
)

templates = Jinja2Templates(directory="TodoApp/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str = Field(min_length=6)


@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("edit-user-password.html",
                                      {"request": request, "user": user})


@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request, username: str = Form(...),
                               password: str = Form(...), password2: str = Form(...),
                               db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(Users).filter(Users.username == username).first()

    msg = "Invalid username or password"

    if user_data is not None:
        if username == user_data.username and verify_password(password, user_data.hashed_password):
            user_data.hashed_password = get_password_hash(password2)
            db.add(user_data)
            db.commit()

            msg = 'Password Updated'

    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user, "msg": msg})