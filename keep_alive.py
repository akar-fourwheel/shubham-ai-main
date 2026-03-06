import threading
import requests
import time
from pathlib import Path
import config

UPLOAD_DIR = Path("uploads")

def keep_alive():
    def ping():
        while True:
            try:
                from voice import synthesize_speech
                audio = synthesize_speech(
                    "Namaste! Main Priya bol rahi hoon, Shubham Motors Hero MotoCorp se, Jaipur. Aap ka call receive karke bahut khushi hui! Kaise madad kar sakti hoon aapki?",
                    "hinglish"
                )
                if audio:
                    (UPLOAD_DIR / "opening_warmup.mp3").write_bytes(audio)
                    print(f"[KeepAlive] Pinged + audio warmed ({len(audio)} bytes)")
                else:
                    requests.get(f"{config.PUBLIC_URL}/health", timeout=5)
                    print("[KeepAlive] Pinged (audio warmup failed)")
            except Exception as e:
                print(f"[KeepAlive] Failed: {e}")
            time.sleep(240)

    t = threading.Thread(target=ping, daemon=True)
    t.start()