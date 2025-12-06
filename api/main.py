from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .routes import planner, assistant, teacher, practice, revision

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": f"An unexpected error occurred: {exc}"},
    )

app.include_router(planner.router, prefix="/study_plan")
app.include_router(assistant.router, prefix="/assistant")
app.include_router(teacher.router, prefix="/teacher")
app.include_router(practice.router, prefix="/practice")
app.include_router(revision.router, prefix="/revision")

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "Hello World"}
