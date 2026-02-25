from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from app.core.database import engine, Base
from app.api import auth, admin, jobs, employers, job_seekers, categories, uploads, contact, notifications
from app.models.contact import ContactRequest
from app.models.notification import Notification
from app.core.init_db import init_db
import traceback
import logging
import sys
from fastapi.openapi.docs import get_swagger_ui_html
from app.core.context import set_base_url
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging to write to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("uvicorn.error")

import sys
print("="*50)
print("APP LOADING: main.py is being executed")
print(f"PYTHON VERSION: {sys.version}")
print("="*50)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize DB (create admin if needed)
init_db()

app = FastAPI(
    title="Jobway API", 
    version="1.0.0",
    docs_url=None, # Disable default docs
    openapi_url="/api/schema",
    redoc_url=None,
    debug=True
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://jobway.uz",
        "https://www.jobway.uz",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_favicon_url="/admin-ui/images/jobway.png",
    )
    
    # Inject our custom CSS and JS
    custom_head = """
    <link rel="stylesheet" href="/admin-ui/swagger-dark.css">
    <script src="/admin-ui/swagger-ui-config.js" defer></script>
    """
    
    # Get the static HTML content
    content = html_response.body.decode()
    
    # Insert custom head before </head>
    if "</head>" in content:
        content = content.replace("</head>", f"{custom_head}</head>")
    else:
        content = content.replace("<head>", f"<head>{custom_head}")
        
    return HTMLResponse(content=content)

@app.get("/")
def read_root():
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not Found")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.mount("/admin-ui", StaticFiles(directory="app/static/admin"), name="admin-ui")

@app.get("/admin", include_in_schema=False)
async def admin_panel():
    return FileResponse("app/static/admin/index.html")

@app.middleware("http")
async def context_and_log_middleware(request: Request, call_next):
    # Detect and set base URL dynamically
    scheme = request.url.scheme
    netloc = request.url.netloc
    base_url = f"{scheme}://{netloc}"
    set_base_url(base_url)
    
    logger.info(f"Incoming request: {request.method} {request.url} | Detected Base URL: {base_url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        traceback.print_exc()
        raise e

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("="*50)
    logger.error(f"CRITICAL ERROR: {request.method} {request.url}")
    logger.error(f"ERROR DETAILS: {exc}")
    traceback.print_exc()
    logger.error("="*50)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)},
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("app/static/admin/images/jobway.png")

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(employers.router, prefix="/api")
app.include_router(job_seekers.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(admin.router, prefix="/api") 
app.include_router(uploads.router, prefix="/api")
app.include_router(contact.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
