from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from ai_engine.agent import run_agent

app = FastAPI(title="Local ERP AI Engine", version="0.2")

class Query(BaseModel):
    user_id: int = 1
    prompt: str
    mode: str = "staff" # staff or customer

@app.get("/")
def read_root():
    return {"message": "AI Engine is running"}

@app.post("/ask/")
async def ask_agent(query: Query):
    try:
        response = run_agent(query.prompt, mode=query.mode)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
