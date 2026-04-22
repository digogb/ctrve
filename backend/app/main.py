from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
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


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    missing = [
        str(e["loc"][-1])
        for e in exc.errors()
        if e.get("type") == "missing" and e.get("loc")
    ]
    if missing:
        fields_str = ", ".join(missing)
        return JSONResponse(
            status_code=422,
            content={
                "detail": "MSG-005",
                "message": f"Os seguintes campos obrigatórios não foram preenchidos: {fields_str}. Preencha-os para continuar.",
                "fields": missing,
            },
        )
    fields = list({str(e["loc"][-1]) for e in exc.errors() if e.get("loc")})
    return JSONResponse(
        status_code=422,
        content={
            "detail": "VALIDATION_ERROR",
            "message": "Dados inválidos na requisição.",
            "fields": fields,
        },
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
