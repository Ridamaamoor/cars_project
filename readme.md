# Hybrid Edge-Cloud Autonomous Fleet Management Service

A distributed RESTful AI system designed for real-time obstacle avoidance and remote human-operator interaction within Unmanned Ground Vehicle (UGV) fleets.

## The problem in my research that this project solves
This project addresses the integration of computer vision and deep learning techniques with distributed computing paradigms (cloud, edge, fog computing) to support autonomous vehicle fleet management. The goal is to design hybrid architectures that leverage local computing power for real-time inference (obstacle detection, object identification, visual navigation) and cloud resources for model training, data aggregation, and fleet coordination. By processing real-time object detection natively at the local edge, the system reduces critical data latency, while the remote cloud orchestration layer provides contextualized safety routing directives and voice-hailing pipelines to base-station engineers without compromising on-board battery life or localized perimeter security boundaries.

## Architecture & Endpoints

| Method | Path | Input | Layer Profile | Output Function |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/fleet/edge/detect` | Image File | Edge Inference (YOLO11) | Bounding box coordinates |
| `POST` | `/fleet/cloud/decision` | JSON Object | Cloud Logic (Gemini/Ollama) | Centralized path routing directives |
| `POST` | `/fleet/telemetry/voice-alert` | Audio File | Human Interface (Groq/gTTS) | Context-aware vocal status stream |

## System Setup
```bash
# 1. Clone the repository and enter the directory
git clone https://github.com/Ridamaamoor/cars_project
cd fleet-management-service

# 2. Rebuild the environment stack
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Apply your credentials
cp .env.example .env
# Populate your live GEMINI_API_KEY and GROQ_API_KEY variables inside .env

# 4. Boot the secure microservice with local SSL certificate encryption
uvicorn server.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt --reload
```

## Local Evaluation Testing Demos

### 1. Local Edge Detection Test
```bash
curl -k -X POST https://localhost:8443/fleet/edge/detect -F "file=@ugv_camera_snapshot.jpg"
```

### 2. Cloud Decision Routing Test
```bash
curl -k -X POST https://localhost:8443/fleet/cloud/decision -H "Content-Type: application/json" -d '{"ugv_id": "UGV_04", "detected_obstacles": ["person", "chair"]}'
```

### 3. Contextual Operator Voice Test
```bash
curl -k -X POST https://localhost:8443/fleet/telemetry/voice-alert -F "audio=@hail_command.wav" --output base_reply.mp3
```
