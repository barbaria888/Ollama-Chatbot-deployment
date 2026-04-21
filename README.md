
---

#  🦙 Ollama Chatbot Deployment (FastAPI + Ollama + Kubernetes)

A production-style, Kubernetes-native AI chatbot system using **FastAPI + WebSockets + Ollama (TinyLlama)** with CI/CD-based Docker builds and scalable deployment architecture.

---

## About Project

* Real-time **streaming AI chat (WebSocket-based)**
* Self-hosted **LLM inference (Ollama + TinyLlama)**
* Kubernetes-native **microservice architecture**
* CI/CD-driven **Docker build & deployment workflow**
* Scalable API layer with **multiple replicas**
* Production-style **service communication via Kubernetes DNS**

---

## 🧠 System Architecture

```text
Client (Browser / websocat)
        ↓
FastAPI (WebSocket Gateway)
        ↓
Kubernetes Service (ai-api-service)
        ↓
AI API Pods (ai-app)
        ↓
Ollama Service (ollama:11434)
        ↓
TinyLlama Model (CPU inference)
        ↓
Streamed response back to client
```

---

## Features

* Real-time token streaming (ChatGPT-like typing effect)
*  Fully Kubernetes-deployed AI stack
*  Local LLM inference (no external APIs)
*  Horizontal scaling (API replicas)
*  Internal service communication via DNS (`ollama-service`)
*  CLI + browser WebSocket support
*  CI-based Docker image build & push (no manual build needed)

---

## 📁 Repo Structure

```text
api/
 ├── main.py              # FastAPI WebSocket server
 ├── requirements.txt     # fastapi, uvicorn[standard], websockets, requests
 ├── Dockerfile           # container for API (used in CI only)

k8s/
 ├── ollama-deployment.yaml
 ├── ollama-service.yaml
 ├── api-deployment.yaml
 ├── api-service.yaml
```

---

##  Design

###  Ollama Layer

* Runs `ollama/ollama` container
* Hosts `tinyllama` model
* Exposes: `http://ollama-service:11434`

### API Layer (FastAPI)

* WebSocket endpoint: `/ws/chat`
* Forwards prompts to Ollama
* Streams response back token-by-token

###  Client Layer

* Browser WebSocket OR CLI (`websocat`)
* Receives live AI responses

---

## 💬 API Endpoints

### 1. WebSocket Chat (Main Feature)

```text
ws://<host>/ws/chat
```

### Flow:

1. Client sends prompt
2. API calls Ollama (`stream: true`)
3. Response is streamed back instantly

---

### 🧪 Browser test(only on local devices)

```js
const ws = new WebSocket("ws://localhost:8000/ws/chat");

ws.onmessage = (e) => console.log("AI:", e.data);
ws.onopen = () => ws.send("Explain Kubernetes simply");
```

---

### 🧪 CLI test

```bash
websocat ws://localhost:8000/ws/chat
```

---

## ☸️ Kubernetes Deployment

### Deploy everything

```bash
kubectl apply -f k8s/
```

---

###  Verify

```bash
kubectl get pods
kubectl get svc
```

Expected services:

* `ollama-service` (ClusterIP)
* `ai-api-service` (NodePort)

---

###  Access API (local or vm)

```bash
kubectl port-forward svc/ai-api-service 8000:80
```

Then:

* HTTP: `http://localhost:8000`
* WebSocket: `ws://localhost:8000/ws/chat`

---

### Access via NodePort

```bash
kubectl get svc ai-api-service
```

Then:

```text
http://<NODE_IP>:<NODE_PORT>
ws://<NODE_IP>:<NODE_PORT>/ws/chat
```

---

## 🐳 CI/CD 

### Docker build is NOT manual

This project uses **CI pipeline automation**:

### Pipeline handles:

* Docker build
* Image tagging
* Push to DockerHub
* Kubernetes rollout update

### Manual build (only for debugging):

```bash
docker build -t hardik0811/ai-app:latest .
docker push hardik0811/ai-app:latest
```

---

## 📦 Resources & Limits

### Ollama (LLM Runtime)

* CPU: 1–2 cores
* RAM: 3–6 GB
* Storage: ephemeral (`emptyDir`)

### API Layer

* Replicas: 2
* CPU: 250m–500m
* RAM: 256–512Mi

---

## 🧠 Model Configuration

Default model:

```text
tinyllama
```

Ensure model exists:

```bash
kubectl exec -it deploy/ollama -- ollama pull tinyllama
```

---

## 🧪 Troubleshooting

### ❌ WebSocket not working

Fix:

```txt
Ensure uvicorn[standard] is installed
```

---

### Ollama not reachable

```bash
kubectl exec -it deploy/ai-app -- curl http://ollama-service:11434/api/tags
```

---

### Look for potential Model issues

```bash
kubectl logs deploy/ollama
```

---

###  API image mismatches

Update:

```yaml
image: hardk/ai-app:latest
```

---

## This is not just a chatbot.

It is a:
* Kubernetes-native inference platform (CPU Only)
* Streaming WebSocket API service
* CI/CD-driven deployment pipeline
---

## ⤴️ Future upgrades

* Redis chat memory (multi-turn context)
* Ingress + TLS WebSockets (production exposure)
* Prometheus + Grafana observability
* React ChatGPT UI frontend
* Multi-model switching (Mistral, Llama, etc.)
* Horizontal autoscaling (HPA)

---

