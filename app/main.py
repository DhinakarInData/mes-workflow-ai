from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from extractor import extract_workflow


app = FastAPI()


# ==========================================
# ENABLE CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/")
def home():

    return {
        "message": "MES Workflow AI Backend Running"
    }


# ==========================================
# WORKFLOW EXTRACTION API
# ==========================================

@app.post("/extract")
def extract(data: dict):

    text = data.get("text", "")

    workflow = extract_workflow(text)

    return workflow.model_dump()