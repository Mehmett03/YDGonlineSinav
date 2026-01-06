"""
Authentication router for login, register, and user management.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import (
    authenticate_user, create_user, create_access_token, 
    get_current_user, get_password_hash
)
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


# ==================== API Endpoints ====================

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kullanıcı adı zaten kullanılıyor"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email adresi zaten kayıtlı"
        )
    
    user = create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role=user_data.role
    )
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "user_id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


# ==================== Web Form Endpoints ====================

@router.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login-form")
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process login form submission."""
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Kullanıcı adı veya şifre hatalı"}
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Redirect based on role
    if user.role == UserRole.ADMIN:
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        response = RedirectResponse(url="/student/dashboard", status_code=303)
    
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response


@router.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request):
    """Render register page."""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register-form")
def register_form(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db)
):
    """Process registration form submission."""
    # Validate passwords match
    if password != password_confirm:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Şifreler eşleşmiyor"}
        )
    
    # Check if username exists
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Bu kullanıcı adı zaten kullanılıyor"}
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Bu email adresi zaten kayıtlı"}
        )
    
    # Create user
    create_user(
        db=db,
        username=username,
        email=email,
        full_name=full_name,
        password=password,
        role=UserRole.STUDENT
    )
    
    return RedirectResponse(url="/auth/login-page?registered=true", status_code=303)


@router.get("/logout")
def logout():
    """Logout and clear session."""
    response = RedirectResponse(url="/auth/login-page", status_code=303)
    response.delete_cookie(key="access_token")
    return response
