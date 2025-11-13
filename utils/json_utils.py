import os, json, uuid
from datetime import datetime, timezone

SUBMISSION_DIR = os.path.join(os.getcwd(), "submissions")
os.makedirs(SUBMISSION_DIR, exist_ok=True)

def _family_from_name(name: str) -> str:
    if not name:
        return ""
    return name.strip().split()[-1].title()

def enrich_submission(data: dict) -> dict:
    ts = datetime.now(timezone.utc)
    data["submission_id"] = str(uuid.uuid4())
    data["timestamp_iso"] = ts.isoformat()
    name_fields = [
        data.get("participant_name"),
        data.get("full_name"),
        data.get("enquirer_name"),
        data.get("rep_name"),
        data.get("event_name"),
        data.get("meeting_title"),
    ]
    data["family_name"] = _family_from_name(next((n for n in name_fields if n), ""))
    return data

def store_json_snapshot(data: dict, prefix: str = "submission"):
    enriched = enrich_submission(data)
    ts_tag = enriched["timestamp_iso"].replace(":", "").replace("-", "")
    fname = f"{prefix}_{enriched['family_name'] or 'anon'}_{ts_tag}.json"
    fpath = os.path.join(SUBMISSION_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    return fpath, enriched
