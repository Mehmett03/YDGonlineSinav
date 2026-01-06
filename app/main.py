"""
FastAPI Application Entry Point
Online Sınav Sistemi (YDG Projesi)
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import init_db, get_db, SessionLocal
from app.routers import auth, admin, student
from app.models.user import User, UserRole
from app.services.auth_service import get_password_hash

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup: Initialize database
    init_db()
    
    # Create default admin user if not exists
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@ydg.edu.tr",
                full_name="Sistem Yöneticisi",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("✅ Default admin user created: admin / admin123")
    finally:
        db.close()
    
    yield
    
    # Shutdown: Cleanup if needed
    print("👋 Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Online Sınav Sistemi",
    description="YDG Dersi - Yazılım Doğrulama ve Geçerleme Projesi",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(student.router)


# ==================== Root Endpoints ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Home page - redirect to login."""
    return RedirectResponse(url="/auth/login-page", status_code=303)


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/CI."""
    return {"status": "healthy", "app": settings.app_name}


@app.get("/api/docs-info")
async def api_info():
    """API documentation info."""
    return {
        "title": "Online Sınav Sistemi API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# ==================== Error Handlers ====================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Sayfa bulunamadı", "code": 404},
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "error": "Sunucu hatası", "code": 500},
        status_code=500
    )
