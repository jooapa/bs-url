
import os
from fastapi import FastAPI

from tasks import analyze_urls, get_urls_json
from models import AnalyzeRequest

app = FastAPI()

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_urls(request)

@app.get("/urls")
def get_urls():
    return get_urls_json()
