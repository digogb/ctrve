from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, checklists, users
from app.core.config import settings
from app.database import create_db_and_tables
from app.services.checklist_service import ChecklistError
from app.services.user_service import UserError


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(UserError)
async def user_error_handler(request: Request, exc: UserError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "message": exc.message, "fields": exc.fields},
    )


@app.exception_handler(ChecklistError)
async def checklist_error_handler(request: Request, exc: ChecklistError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "message": exc.message, "fields": exc.fields},
    )


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(checklists.router, prefix="/api/v1")
