import streamlit as st
import json, os, requests, glob, io, zipfile
from datetime import datetime, date

from utils.retry_queue import _load_queue, _save_queue
from utils.webhook_utils import WEBHOOK_URL

def _zip_submissions():
    folder = "submissions"
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".json") and not f.startswith("_retry_queue"):
                    fpath = os.path.join(root, f)
                    arcname = os.path.relpath(fpath, folder)
                    zf.write(fpath, arcname)
    mem_zip.seek(0)
    return mem_zip

def _filter_submissions(start_date=None, end_date=None, case_types=None):
    folder = "submissions"
    files = glob.glob(os.path.join(folder, "*.json"))
    filtered = []
    for fpath in files:
        if "_retry_queue" in fpath:
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = data.get("timestamp_iso", "")
            cat = data.get("category", "")
            ts_dt = None
            try:
                ts_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                pass
            if start_date and ts_dt and ts_dt.date() < start_date:
                continue
            if end_date and ts_dt and ts_dt.date() > end_date:
                continue
            if case_types and cat not in case_types:
                continue
            filtered.append((fpath, data))
        except Exception as e:
            print(f"[WARN] Skipping {fpath}: {e}")
    return filtered

def _zip_filtered_submissions(filtered):
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fpath, _ in filtered:
            arcname = os.path.basename(fpath)
            zf.write(fpath, arcname)
    mem_zip.seek(0)
    return mem_zip

def _csv_from_filtered(filtered):
    """Create a CSV text from filtered submissions (one row per JSON)."""
    import csv
    from io import StringIO
    # Choose a useful set of columns for a summary. Extra fields are appended as needed.
    columns = [
        "submission_id","timestamp_iso","category","family_name",
        "full_name","participant_name","enquirer_name","actor","kooyong_resident",
        "visa_subclass","home_affairs_ref","application_date",
        "contact_email","contact_phone",
        "issue_summary","desired_outcome","assistance"
    ]
    # Collect rows
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    for _, data in filtered:
        writer.writerow(data)
    return output.getvalue()

def queue_admin():
    st.header("📬 Submission Retry Queue")

    # Optional admin key gate (set ADMIN_KEY in Streamlit secrets / env)
    ADMIN_KEY = os.getenv("ADMIN_KEY", "")
    if ADMIN_KEY:
        key_try = st.text_input("Enter admin key", type="password")
        if key_try != ADMIN_KEY:
            st.stop()

    if not WEBHOOK_URL:
        st.warning("No Power Automate webhook configured (set POWER_AUTOMATE_WEBHOOK).")

    q = _load_queue()
    if not q:
        st.success("🎉 The queue is empty — all submissions have been delivered.")
    else:
        st.info(f"There are currently **{len(q)}** queued submissions awaiting delivery.")

        for item in q:
            with st.expander(f"{item.get('category','?')} | {item.get('family_name','')} | {item.get('timestamp_iso','')}"):
                st.json(item)
                col1, col2 = st.columns(2)
                if col1.button(f"Resend {item.get('submission_id')}", key=f"send_{item['submission_id']}"):
                    try:
                        resp = requests.post(WEBHOOK_URL, json=item, timeout=10)
                        if resp.status_code in (200, 202):
                            st.success("✅ Sent successfully — removing from queue.")
                            q = [x for x in q if x["submission_id"] != item["submission_id"]]
                            _save_queue(q)
                        else:
                            st.error(f"Failed: HTTP {resp.status_code}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                if col2.button(f"Delete {item.get('submission_id')}", key=f"del_{item['submission_id']}"):
                    q = [x for x in q if x["submission_id"] != item["submission_id"]]
                    _save_queue(q)
                    st.warning("🗑️ Deleted from queue.")

        if st.button("Purge entire queue"):
            try:
                os.remove(os.path.join("submissions", "_retry_queue.json"))
                st.success("Queue cleared.")
            except FileNotFoundError:
                st.info("Queue already empty.")

    st.markdown("---")
    st.subheader("📦 Export filtered submissions")

    col1, col2, col3 = st.columns(3)
    with col1:
        start = st.date_input("Start date", value=None)
    with col2:
        end = st.date_input("End date", value=None)
    with col3:
        case_types = st.multiselect(
            "Case types",
            ["NDIS", "Visa", "Meeting Request", "Event Invitation"],
            default=[]
        )

    colz1, colz2 = st.columns(2)
    if colz1.button("Filter & Download ZIP"):
        filtered = _filter_submissions(start, end, case_types)
        if not filtered:
            st.warning("No submissions match the chosen filters.")
        else:
            zip_data = _zip_filtered_submissions(filtered)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label=f"Download {len(filtered)} filtered submissions (ZIP)",
                data=zip_data,
                file_name=f"submissions_filtered_{ts}.zip",
                mime="application/zip"
            )

    if colz2.button("Filter & Download CSV Summary"):
        filtered = _filter_submissions(start, end, case_types)
        if not filtered:
            st.warning("No submissions match the chosen filters.")
        else:
            csv_text = _csv_from_filtered(filtered)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label=f"Download CSV ({len(filtered)} rows)",
                data=csv_text,
                file_name=f"submissions_summary_{ts}.csv",
                mime="text/csv"
            )
