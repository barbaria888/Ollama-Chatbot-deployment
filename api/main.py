from fastapi import FastAPI
import requests

app = FastAPI()

OLLAMA_URL = "http://ollama-service:11434/api/generate"

@app.get("/")
def health():
    return {"status": "running"}

@app.post("/chat")
def chat(prompt: str):
    response = requests.post(OLLAMA_URL, json={
        "model": "tinyllama",
        "prompt": prompt,
        "stream": False
    })
    return response.json()
