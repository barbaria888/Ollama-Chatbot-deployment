# Ollama Chatbot Deployment (FastAPI + Ollama + Kubernetes)

A minimal, production-oriented example of deploying an **Ollama-backed chatbot** in Kubernetes.

This repo contains:
- A **FastAPI** application that exposes a **WebSocket chat endpoint** and streams model output back to the client.
- Kubernetes manifests to deploy **Ollama** (model runtime) and the **API** service.
- A Dockerfile to containerize the API.

---

## What you get

- **Streaming chat** over WebSocket: `ws://.../ws/chat`
- **Kubernetes-ready** setup with:
  - `ollama/ollama` deployment + internal service (`ollama-service:11434`)
  - API deployment + NodePort service for external access
- **Simple architecture**: Client → FastAPI → Ollama `/api/generate` → streamed tokens → Client

---

## Architecture

**In-cluster communication**
- The API calls Ollama using Kubernetes DNS:
  - `http://ollama-service:11434/api/generate`

**Streaming**
- The API uses Ollama’s `stream: true` responses and forwards chunks to the WebSocket client until it sends a final `"[DONE]"`.

---

## Repo structure

- `api/`
  - `main.py` — FastAPI app (WebSocket endpoint)
  - `requirements.txt` — `fastapi`, `uvicorn`, `requests`
  - `Dockerfile` — runs `uvicorn main:app --host 0.0.0.0 --port 8000`
- `k8s/`
  - `ollama-deployment.yaml` — deploys `ollama/ollama` with CPU/memory requests/limits and an `emptyDir` volume
  - `ollama-service.yaml` — ClusterIP service named `ollama-service` on port `11434`
  - `api-deployment.yaml` — deploys the API (`hardik0811/ai-app:latest`) with 2 replicas
  - `api-service.yaml` — NodePort service exposing the API on port `80` → `8000`

---

## API: Chatting Endpoints

### WebSocket Chat (streaming)

**Endpoint**
- `GET /ws/chat` (WebSocket upgrade)

**How it works**
- Client sends a text message (your prompt)
- Server forwards it to Ollama `/api/generate` with:
  - `model: "tinyllama"`
  - `prompt: <your message>`
  - `stream: true`
- Server streams partial text back as WebSocket messages (chunked), then sends:
  - `"[DONE]"`

**WebSocket message flow**
1. Client → Server: `"Hello, who are you?"`
2. Server → Client: `"I am ..."`
3. Server → Client: `" an AI ..."`
4. ...
5. Server → Client: `"[DONE]"`

**Quick test from the browser console**
```js
const ws = new WebSocket("ws://localhost:8000/ws/chat");

ws.onmessage = (e) => console.log("recv:", e.data);
ws.onopen = () => ws.send("Say hi in one sentence");
```

> If you are accessing via Kubernetes NodePort, replace `localhost:8000` with `http://<NODE_IP>:<NODE_PORT>` (and use `ws://`).

---

### Health endpoint

**Endpoint**
- `GET /`

**Response**
```json
{ "status": "running" }
```

---

## Kubernetes deployment

### 1) Deploy everything

From repo root:
```bash
kubectl apply -f k8s/
```

Verify:
```bash
kubectl get pods
kubectl get svc
```

You should see services:
- `ollama-service` (internal, port `11434`)
- `ai-api-service` (NodePort, port `80` → container `8000`)

---

### 2) Access the API externally (NodePort)

Get the assigned node port:
```bash
kubectl get svc ai-api-service
```

Then:
- Health: `http://<NODE_IP>:<NODE_PORT>/`
- WebSocket: `ws://<NODE_IP>:<NODE_PORT>/ws/chat`

If using **minikube**:
```bash
minikube service ai-api-service --url
```

Use the returned URL as your base.

---
}
🐳 Docker (INFO ONLY)

Docker build/push is handled by CI pipeline.

The Dockerfile exists only for CI:

api/Dockerfile

Local build is optional for debugging only:

docker build -t ai-api .
📦 Resources
Ollama
CPU: 1–2 cores
RAM: 3–6GB
Storage: ephemeral (emptyDir)
API
replicas: 2
CPU: 250m–500m
RAM: 256–512Mi

> Important: The API code is configured to call `http://ollama-service:11434/api/generate`, which is meant for Kubernetes. If you run Docker locally without Kubernetes DNS, the API won’t be able to reach Ollama unless you adapt the URL.

---

## Model notes

The API requests this model:
- `tinyllama`

Make sure your Ollama instance has it available (pulled). If the model isn’t present, Ollama will error.

---

## Troubleshooting

### Ollama is running but responses fail
Common causes:
❌ WebSocket connects but no response

Check:
```bash
kubectl get pods
kubectl logs deploy/ollama
kubectl logs deploy/ai-app
```
❌ Model not found

Fix:
```bash
kubectl exec -it deploy/ollama -- ollama pull tinyllama
```
### API image mismatch
`k8s/api-deployment.yaml` uses:
- `hardik0811/ai-app:latest`

If you build your own image, update that field to your image name/tag.

---

## License

MIT (see `LICENSE`).
