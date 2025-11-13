import os, json, time, threading, requests

QUEUE_FILE = os.path.join(os.getcwd(), "submissions", "_retry_queue.json")
MAX_RETRIES = 5
WEBHOOK_URL = os.getenv("POWER_AUTOMATE_WEBHOOK", "").strip()

def _load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    try:
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_queue(q):
    os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(q, f, indent=2)

def enqueue(data: dict):
    q = _load_queue()
    data["_retry_count"] = data.get("_retry_count", 0)
    q.append(data)
    _save_queue(q)
    print(f"[QUEUE] Stored for retry ({len(q)} total)")

def _retry_worker():
    if not WEBHOOK_URL:
        print("[QUEUE] No webhook configured; retry worker disabled.")
        return
    while True:
        time.sleep(300)   # every 5 minutes
        q = _load_queue()
        if not q:
            continue
        remaining = []
        for item in q:
            try:
                resp = requests.post(WEBHOOK_URL, json=item, timeout=10)
                if resp.status_code not in (200, 202):
                    raise RuntimeError(f"HTTP {resp.status_code}")
                print(f"[QUEUE] Delivered queued submission {item.get('submission_id')}")
            except Exception as e:
                item["_retry_count"] = item.get("_retry_count", 0) + 1
                if item["_retry_count"] < MAX_RETRIES:
                    remaining.append(item)
                    print(f"[QUEUE] Retry {item.get('submission_id')} failed ({item['_retry_count']}); will retry.")
                else:
                    print(f"[QUEUE] Dropping {item.get('submission_id')} after {MAX_RETRIES} attempts.")
        _save_queue(remaining)

def start_worker():
    t = threading.Thread(target=_retry_worker, daemon=True)
    t.start()
