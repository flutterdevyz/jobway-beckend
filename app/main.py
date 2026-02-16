from fastapi import FastAPI, Request
from app.core.database import engine, Base
from app.api import auth, admin, jobs, employers, job_seekers
from app.core.init_db import init_db

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize DB (create admin if needed)
init_db()

app = FastAPI(title="Jobway API", version="1.0.0")

@app.middleware("http")
async def add_download_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/openapi.json":
        response.headers["Content-Disposition"] = 'attachment; filename="openapi.json"'
    return response

app.include_router(auth.router)
app.include_router(employers.router)
app.include_router(job_seekers.router)
app.include_router(admin.router)
app.include_router(jobs.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Jobway API"}
