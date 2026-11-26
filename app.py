from pathlib import Path
from threading import Lock
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pixelrag import ask
app=FastAPI()
lock=Lock()
class Query(BaseModel):
    question: str=Field(min_length=1,max_length=500)
    data: dict
    people: str
    budget: str
    reserve: str
@app.get('/')
def home():
    return FileResponse(Path(__file__).with_name('index.html'))
@app.post('/api/ask')
def query(body:Query):
    try:
        with lock:
            return ask(body.question,body.model_dump(exclude={'question'}))
    except Exception as exc:
        raise HTTPException(500,detail=str(exc)) from exc
