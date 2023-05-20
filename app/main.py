from fastapi import FastAPI, HTTPException, Request
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from .templates import templates
from .utils import is_browser
from starlette.exceptions import HTTPException as SHTTPException

# currently using alembic to manage tables
# models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TestAPI",
)

app.mount("/static", StaticFiles(directory="static"), name="static")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SHTTPException)
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if is_browser(request=request):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "status_code": exc.status_code, "detail": exc.detail},
        )
    else:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)


@app.get("/")
def default(request: Request):
    data = {"message": "hello"}
    if is_browser(request=request):
        return templates.TemplateResponse(
            "index.html", {"request": request, "data": data}
        )
    else:
        return data
