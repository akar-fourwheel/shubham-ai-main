import threading
import requests
import time
import config

def keep_alive():
    def ping():
        while True:
            try:
                requests.get(f"{config.PUBLIC_URL}/health", timeout=5)
                print("[KeepAlive] Pinged")
            except Exception as e:
                print(f"[KeepAlive] Failed: {e}")
            time.sleep(240)  # ping every 4 minutes

    t = threading.Thread(target=ping, daemon=True)
    t.start()