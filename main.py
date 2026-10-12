import time
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGIN = "https://dash-4mvb2w.example.com"
EMAIL = "23f2001563@ds.study.iitm.ac.in"

app = FastAPI()

# CORS added first so the header middleware below wraps it (outermost),
# which means preflight and rejected responses also carry the custom headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],   # exact match, no wildcard
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)


@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
async def stats(values: Optional[str] = None):
    if values is None or not values.strip():
        raise HTTPException(status_code=422, detail="values is required")
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=422, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=422, detail="no values provided")
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }
