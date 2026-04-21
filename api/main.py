from fastapi import FastAPI, WebSocket
import requests
import json
import asyncio

app = FastAPI()

OLLAMA_URL = "http://ollama-service:11434/api/generate"

@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()

    while True:
        prompt = await websocket.receive_text()

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "tinyllama",
                "prompt": prompt,
                "stream": True
            },
            stream=True
        )

        buffer = ""

        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))

                token = data.get("response", "")
                buffer += token

                # Send in chunks instead of every token
                if len(buffer) >= 3:
                    await websocket.send_text(buffer)
                    await asyncio.sleep(0.02)  
                    buffer = ""

        # flush remaining text
        if buffer:
            await websocket.send_text(buffer)

        await websocket.send_text("[DONE]")
