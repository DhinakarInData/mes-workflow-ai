import os

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from api.workflow_api import router


app = FastAPI()

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
configured_origins = os.environ.get("FRONTEND_ORIGINS", "")
allowed_origins.extend(
    origin.strip()
    for origin in configured_origins.split(",")
    if origin.strip()
)

# ===================================
# CORS CONFIGURATION
# ===================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ===================================
# REGISTER ROUTES
# ===================================

app.include_router(router)