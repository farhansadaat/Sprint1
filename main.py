from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.protected import router as protected_router
from routers.jobs import router as jobs_router

app = FastAPI(title="ATS SaaS Backend", version="1.0.0")

app.include_router(auth_router, prefix="/api")
app.include_router(protected_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)