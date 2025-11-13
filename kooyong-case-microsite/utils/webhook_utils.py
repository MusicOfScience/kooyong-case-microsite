import os, requests

WEBHOOK_URL = os.getenv("POWER_AUTOMATE_WEBHOOK", "").strip()

def post_to_power_automate(data: dict) -> bool:
    if not WEBHOOK_URL:
        print("[WARN] No POWER_AUTOMATE_WEBHOOK set; skipping webhook send.")
        return False
    try:
        resp = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if resp.status_code in (200, 202):
            print("[OK] Submission delivered to Power Automate.")
            return True
        else:
            print(f"[WARN] Webhook returned {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Webhook post failed: {e}")
        return False
