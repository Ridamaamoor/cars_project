# client.py
import cv2
import numpy as np
import urllib3
import sounddevice as sd
import soundfile as sf
import os
import io
from network_client import get_secure_session

urllib3.disable_warnings()

BASE_URL = "https://localhost:8443"
session = get_secure_session("partner.crt")

UGV_ID = "UGV_FLEET_NODE_04"
SAMPLE_RATE = 16000
CHANNELS = 1

print(f"=== Autonomous Fleet Operator Station Active: {UGV_ID} ===")
print("-> Press 'SPACEBAR' to capture telemetry, query the Cloud, and trigger Contextual Voice Hailing.")
print("-> Press 'ESC' to close the monitoring channel safely.")

cap = cv2.VideoCapture(0)
telemetry_banner = "UGV Status: Connected. Press SPACE to sync telemetry."

while True:
    ok, frame = cap.read()
    if not ok:
        break
        
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, h - 40), (w, h), (0, 0, 0), -1)
    cv2.putText(frame, telemetry_banner, (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    cv2.imshow("UGV Mounted Live Vision Monitor Feed", frame)
    key = cv2.waitKey(1)
    
    if key == 32:
        telemetry_banner = "UGV SYNC: Recording Voice Command + Capturing Inference Frame..."
        cv2.rectangle(frame, (0, h - 40), (w, h), (0, 0, 255), -1)
        cv2.putText(frame, telemetry_banner, (15, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.imshow("UGV Mounted Live Vision Monitor Feed", frame)
        cv2.waitKey(10)
        
        _, img_buf = cv2.imencode(".jpg", frame)
        
        # Record microphone speech
        audio_capture = sd.rec(int(3.0 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
        sd.wait()
        
        audio_io = io.BytesIO()
        sf.write(audio_io, audio_capture, SAMPLE_RATE, format='WAV', subtype='PCM_16')
        audio_io.seek(0)
        
        print(f"\n--- Processing Cascaded Fleet Architecture Pipeline Requests ---")
        labels = []
        
        try:
            # === ENDPOINT CALL 1: LOCAL EDGE VISION DETECTION ===
            print("[1/3] Uploading frame to Edge Layer for local obstacle detection...")
            r_detect = session.post(
                f"{BASE_URL}/fleet/edge/detect",
                files={"file": ("ugv_lens.jpg", img_buf.tobytes(), "image/jpeg")},
                timeout=10
            )
            
            if r_detect.status_code == 200:
                detection_data = r_detect.json()["detections"]
                labels = [obj["obstacle_class"] for obj in detection_data]
                print(f"   -> Edge Inference Result: Identified obstacles {labels}")
                
                for obj in detection_data:
                    x1, y1, x2, y2 = obj["bounding_box"]
                    label_name = obj["obstacle_class"]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cv2.putText(frame, f"OBSTACLE: {label_name}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.imshow("UGV Mounted Live Vision Monitor Feed", frame)
                cv2.waitKey(10)
            else:
                print(f"   -> Edge detection failed with code: {r_detect.status_code}")
                
            # === ENDPOINT CALL 2: SHIFT VISUAL LABELS INTO SERVER MEMORY LAYER ===
            print("[2/3] Shipping edge targets to Cloud Layer to populate system context...")
            r_decision = session.post(
                f"{BASE_URL}/fleet/cloud/decision",
                json={"ugv_id": UGV_ID, "detected_obstacles": labels},
                timeout=12
            )
            if r_decision.status_code == 200:
                print(f"   -> Cloud Routing Directive: {r_decision.json()['navigation_directive']}")
            
            # === ENDPOINT CALL 3: CALL VOICE CHATROOM WITH ACTIVE CACHED CONTEXT ===
            print("[3/3] Synchronizing operator voice track with context-aware base station...")
            r_voice = session.post(
                f"{BASE_URL}/fleet/telemetry/voice-alert",
                files={"audio": ("hail.wav", audio_io.read(), "audio/wav")},
                timeout=15
            )
            if r_voice.status_code == 200:
                print(f"   -> Operator Query (STT): {r_voice.headers.get('operator_command')}")
                print(f"   -> Context-Aware Reply (TTS): {r_voice.headers.get('fleet_status_reply')}")
                telemetry_banner = f"System: {r_voice.headers.get('fleet_status_reply')[:45]}..."
                
                with open("fleet_hail_reply.mp3", "wb") as f:
                    f.write(r_voice.content)
                
                audio_data, fs = sf.read("fleet_hail_reply.mp3")
                sd.play(audio_data, fs)
                sd.wait()
                
            print(f"-----------------------------------------------------------------")
            
        except Exception as network_error:
            telemetry_error = "Network Fault occurred during fleet synchronization loop."
            print(f"   -> Connection Routing Crash Error: {str(network_error)}")

    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()
print("\nFleet telemetry monitor channel safely offline.")
