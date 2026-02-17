from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base
from app.api import auth, admin, jobs, employers, job_seekers
from app.core.init_db import init_db

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize DB (create admin if needed)
init_db()

app = FastAPI(
    title="Jobway API", 
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/schema",
    redoc_url=None
)

@app.middleware("http")
async def add_download_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/api/schema":
        response.headers["Content-Disposition"] = 'attachment; filename="openapi.json"'
    return response

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(employers.router, prefix="/api")
app.include_router(job_seekers.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(admin.router) 

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Page not found (404)</title>
        <style>
            body {{ font-family: sans-serif; color: #333; margin: 0; background: #fff; }}
            #summary {{ background: #ffffcc; border-bottom: 1px solid #ddd; padding: 20px 40px; }}
            #summary h1 {{ font-weight: normal; margin: 10px 0; color: #444; }}
            #summary h1 span {{ color: #999; font-size: 0.6em; }}
            #summary p {{ margin: 5px 0; font-size: 0.95em; }}
            #explanation {{ background: #eee; padding: 10px 40px; border-bottom: 1px solid #ddd; }}
            #content {{ padding: 10px 40px; }}
            #content p {{ font-size: 0.9em; }}
            ol {{ list-style-type: decimal; padding-left: 30px; }}
            li {{ margin-bottom: 5px; font-family: monospace; font-size: 1em; }}
            code {{ font-family: monospace; background: #f9f9f9; padding: 2px 4px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <div id="summary">
            <h1>Page not found <span>(404)</span></h1>
            <p><strong>Request Method:</strong> GET</p>
            <p><strong>Request URL:</strong> {request.url}</p>
        </div>
        <div id="explanation">
            <p>Using the URLConf defined in <code>project.urls</code>, Django tried these URL patterns, in this order:</p>
            <ol>
                <li>admin/</li>
                <li>api/auth/</li>
                <li>api/schema/ [name='schema']</li>
                <li>api/docs/ [name='swagger-ui']</li>
            </ol>
            <p>The empty path didn't match any of these.</p>
        </div>
        <div id="content">
            <p>You're seeing this error because you have <code>DEBUG = True</code> in your Django settings file. Change that to <code>False</code>, and Django will display a standard 404 page.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=404)
