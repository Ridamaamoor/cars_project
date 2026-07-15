# Hybrid Edge-Cloud Autonomous Fleet Management Service

A distributed RESTful AI system designed for real-time obstacle avoidance and remote human-operator interaction within Unmanned Ground Vehicle (UGV) fleets.

## The problem in my research that this project solves
This project addresses the integration of computer vision and deep learning techniques with distributed computing paradigms (cloud, edge, fog computing) to support autonomous vehicle fleet management. The goal is to design hybrid architectures that leverage local computing power for real-time inference (obstacle detection, object identification, visual navigation) and cloud resources for model training, data aggregation, and fleet coordination. By processing real-time object detection natively at the local edge, the system reduces critical data latency, while the remote cloud orchestration layer provides contextualized safety routing directives and voice-hailing pipelines to base-station engineers without compromising on-board battery life or localized perimeter security boundaries.

## System Prerequisites & Local Models
Before booting the server, you must ensure the local fallback component model is running in your background memory workspace:
1. Download and install **Ollama** inside your environment space.
2. Pull and start the local model engine by executing:
   ```bash
   ollama run llama3.2:3b
   ```

## Local Codebase Architecture Layout
```text
fleet-management-service/
├── certs/
│   ├── server.crt                 # SSL Public Certificate Chain
│   └── server.key                 # SSL Private Encryption Key (Ignored by Git)
├── client/
│   ├── client.py                  # Main Native Live Camera Driver Loop
│   └── network_client.py          # Custom SSL Transport Adapter Layer
├── server/
│   └── main.py                    # Main 3-Endpoint FastAPI Architecture Logic
├── .env.example                   # Environment Variables Credentials Template
├── .gitignore                     # Git Tracking Security Filter Block
├── readme.md                      # Academic Project System Documentation
└── requirements.txt               # Freezed Python Dependency Version Tree
```

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

# 3. Configure your API security credentials
cp .env.example .env
# Open the newly generated .env file and paste your valid GEMINI_API_KEY and GROQ_API_KEY inside

# 4. Boot the secure microservice with local SSL certificate encryption
uvicorn server.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt --reload
```

## Endpoints, Schemas & `curl` Operational Examples

Because this server operates over local SSL parameters with a self-signed encryption handshake wrapper, **every `curl` statement must include the `-k` or `--insecure` parameter flag** to bypass corporate root authority certificate validation steps cleanly.

### 1. Endpoint: `/health` [GET]
* **Purpose**: System-wide synchronization and networking gateway uptime validation test.
* **Input Parameters**: None
* **curl Execution Example**:
  ```bash
  curl -k https://localhost:8443/health
  ```
* **Expected JSON Response Payload**:
  ```json
  {
    "status": "synchronized"
  }
  ```

### 2. Endpoint: `/fleet/edge/detect` [POST]
* **Purpose**: Simulates the localized Edge Layer. Runs a local **YOLO11** component model on an uploaded frame image to extract real-time obstacle coordinates without cloud reliance.
* **Input Parameters**: Multipart Form-Data payload containing an image binary block (`-F "file=@path_to_image.jpg"`).
* **curl Execution Example**:
  ```bash
  curl -k -X POST https://localhost:8443/fleet/edge/detect -F "file=@test.jpg"
  ```
* **Expected JSON Response Payload**:
  ```json
  {
    "fleet_node_status": "PROCESSED_AT_EDGE",
    "detections": [
      {
        "obstacle_class": "laptop",
        "confidence": 0.91,
        "bounding_box": [363, 198, 599, 568]
      },
      {
        "obstacle_class": "person",
        "confidence": 0.46,
        "bounding_box": [28, 335, 481, 895]
      }
    ]
  }
  ```

### 3. Endpoint: `/fleet/cloud/decision` [POST]
* **Purpose**: Centralized Cloud Orchestration Control. Transmits edge targets to **Gemini 2.5 Flash** to calculate real-time navigational routing directives. Includes a resilient failover checking algorithm that automatically routes to your local **Ollama Llama 3.2** model if the daily cloud quota boundary is exhausted.
* **Input Parameters**: Raw JSON raw string body object mapping vehicle descriptors and target array metrics.
* **curl Execution Example**:
  ```bash
  curl -k -X POST https://localhost:8443/fleet/cloud/decision -H "Content-Type: application/json" -d '{"ugv_id": "UGV_TEST_NODE", "detected_obstacles": ["person", "car"]}'
  ```
* **Expected JSON Response Payload**:
  ```json
  {
    "orchestration_layer": "CENTRALIZED_CLOUD_AI",
    "navigation_directive": "SLOW_PROCEDURE: Human presence and vehicular obstacle identified in trajectory tracking boundaries. Adjust speed vector parameters immediately."
  }
  ```

### 4. Endpoint: `/fleet/telemetry/voice-alert` [POST]
* **Purpose**: Advanced Multimodal Voice Interface layer. Translates incoming radio audio signals using **Groq Whisper (STT)**, maps them against stateful server memory trackers to identify context, and streams back a raw audio spoken report using **gTTS (TTS)**.
* **Input Parameters**: Multipart Form-Data payload containing an audio recording binary block (`-F "audio=@path_to_voice.wav"`).
* **curl Execution Example**:
  ```bash
  curl -k -X POST https://localhost:8443/fleet/telemetry/voice-alert -F "audio=@hail.wav" --output system_vocal_response.mp3
  ```
* **Expected Transmission Behavior**: The terminal downloads the resulting streaming bytes and outputs a playable audio track named `system_vocal_response.mp3` onto your disk layout space while flashing clean string logging metrics across tracking headers.