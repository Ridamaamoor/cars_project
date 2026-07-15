# server/main_object_detection.py
import io
import os
import time
import requests
from fastapi import FastAPI, UploadFile, File, Response, Request
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv

# Fleet AI Stack
from ultralytics import YOLO
from google import genai
from google.genai import types
from groq import Groq
from gtts import gTTS

load_dotenv()

app = FastAPI(title="Hybrid Edge-Cloud Autonomous Fleet Management Service", version="2.5")

# Initialize Models
yolo = YOLO("yolo11n.pt")
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- PHD PARADIGM LAYER: FLIGHT STORAGE MEMORY CACHE ---
# This dictionary shares vision tracking metrics instantly with the voice subsystem
FLEET_MEMORY_CACHE = {
    "last_detected_obstacles": "no obstacles detected yet",
    "last_navigation_directive": "System initialized. Waiting for vehicle telemetry."
}

@app.middleware("http")
async def log_fleet_latency(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    response.headers["X-Fleet-Process-Time"] = f"{latency:.4f}s"
    return response

@app.get("/health")
def fleet_health():
    return {"status": "synchronized"}

# ---- ENDPOINT 1: EDGE/FOG INFERENCE LAYER (YOLO11) ----
@app.post("/fleet/edge/detect")
async def local_edge_inference(file: UploadFile = File(...)):
    img_bytes = await file.read()
    img = Image.open(io.BytesIO(img_bytes))
    results = yolo(img, verbose=False)[0]
    detections = []
    
    for b in results.boxes:
        raw_box = b.xyxy[0].tolist()
        detections.append({
            "obstacle_class": yolo.names[int(b.cls)],
            "confidence": round(float(b.conf), 2),
            "bounding_box": [int(coord) for coord in raw_box]
        })
        
    return {"fleet_node_status": "PROCESSED_AT_EDGE", "detections": detections}

# ---- ENDPOINT 2: CLOUD DECISION LAYER (Gemini 2.5 Flash + Memory Injection) ----
class FleetDecisionRequest(BaseModel):
    ugv_id: str
    detected_obstacles: list

@app.post("/fleet/cloud/decision")
def cloud_fleet_coordination(req: FleetDecisionRequest):
    obstacle_string = ", ".join(req.detected_obstacles) if req.detected_obstacles else "no obstacles"
    
    # Cache the detected objects inside our global fleet memory string wrapper
    FLEET_MEMORY_CACHE["last_detected_obstacles"] = obstacle_string
    
    prompt = (
        f"Autonomous fleet management telemetry packet received from UGV node '{req.ugv_id}'. "
        f"Local edge vision sensors have identified these obstacles/navigation targets: {obstacle_string}. "
        "Act as a centralized fleet coordination safety matrix. Provide a brief one-sentence navigational "
        "routing recommendation or speed override command for the vehicle path."
    )
    
    try:
        decision = gemini.models.generate_content(model="gemini-2.5-flash", contents=prompt).text
        directive = decision.strip()
    except Exception:
        # Local model backup failover sequence
        ollama_payload = {
            "model": "llama3.2:3b",
            "prompt": f"System Directive: You are an autonomous fleet navigation router. Respond in one short sentence.\n\nContext: {prompt}",
            "stream": False
        }
        try:
            r = requests.post("http://127.0.0", json=ollama_payload, timeout=10)
            directive = r.json()["response"].strip()
        except Exception:
            directive = f"EMERGENCY BRAKE MANDATE: Objects [{obstacle_string}] blocking vector."

    # Cache the final directive text so the vocal module can read it out loud
    FLEET_MEMORY_CACHE["last_navigation_directive"] = directive
    return {"orchestration_layer": "CENTRALIZED_CLOUD_AI", "navigation_directive": directive}

# ---- ENDPOINT 3: CONTEXT-AWARE OPERATOR INTERFACE (Voice Response) ----
@app.post("/fleet/telemetry/voice-alert")
async def voice_hailing_channel(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    
    # 1. Speech-to-Text translation via Groq Whisper
    operator_voice_command = groq.audio.transcriptions.create(
        file=(audio.filename, audio_bytes), model="whisper-large-v3-turbo", response_format="text"
    )
    
    # Extract the shared tracking context values from our global fleet memory cache
    current_obstacles = FLEET_MEMORY_CACHE["last_detected_obstacles"]
    current_directive = FLEET_MEMORY_CACHE["last_navigation_directive"]
    
    # 2. Feed the shared context directly to Gemini so the vocal assistant knows exactly what was seen
    voice_system_prompt = (
        f"You are the vocal assistant for an autonomous fleet mission control room. "
        f"The vehicle vision sensors currently see these specific objects: {current_obstacles}. "
        f"The cloud server has issued this exact movement directive: {current_directive}. "
        f"The human engineer just hailed you on the microphone and asked: '{operator_voice_command}'. "
        "Formulate a friendly, brief one-sentence vocal response answering the engineer. "
        "Directly state what objects were found or what the system is doing based on the context data."
    )
    
    reply = gemini.models.generate_content(model="gemini-2.5-flash", contents=voice_system_prompt).text
    
    # 3. Generate spoken audio stream file bytes (gTTS)
    buf = io.BytesIO()
    gTTS(text=reply.strip(), lang="en").write_to_fp(buf)
    
    clean_operator = str(operator_voice_command).replace("\n", " ").strip().encode("ascii", "ignore").decode("ascii")
    clean_reply = str(reply).replace("\n", " ").strip().encode("ascii", "ignore").decode("ascii")
    
    return Response(
        content=buf.getvalue(),
        media_type="audio/mpeg",
        headers={"operator_command": clean_operator, "fleet_status_reply": clean_reply}
    )
