import os
import streamlit as st

from forms.ndis_form import ndis_form
from forms.visa_form import visa_form
from forms.meeting_form import meeting_form
from forms.event_form import event_form

from utils.email_utils import send_email
from utils.docx_utils import generate_meeting_docx, generate_event_docx
from utils.json_utils import store_json_snapshot
from utils.webhook_utils import post_to_power_automate
from utils.retry_queue import enqueue, start_worker

st.set_page_config(
    page_title="Kooyong Case Support Portal",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Start retry worker for webhook queue
start_worker()

# Brand styles
with open("assets/brand.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Kooyong Case Support Portal")
st.caption("Accessible triage for constituents and community groups (WCAG 2.1)")

st.sidebar.header("Submit a request")

nav = st.sidebar.radio(
    "Admin & Tools",
    ["Main Forms", "Retry Queue Admin"],
    index=0,
)

def email_subject(data: dict) -> str:
    cat = data.get("category", "General")
    base = {
        "NDIS": "NDIS",
        "Visa": "Visa Issue",
        "Meeting Request": "Meeting Request",
        "Event Invitation": "Event Invitation",
    }.get(cat, cat)
    name = data.get("participant_name") or data.get("full_name") or data.get("event_name") or data.get("meeting_title") or ""
    extra = data.get("visa_subclass") or data.get("actor") or ""
    # append ISO timestamp & family name for consistency
    stamp = data.get("timestamp_iso", "")
    family = data.get("family_name", "")
    parts = [base, name, extra, family, stamp]
    return " | ".join([p for p in parts if p])

def email_body(data: dict) -> str:
    lines = [f"{k}: {v}" for k,v in data.items()]
    return "Submission details\n\n" + "\n".join(lines)

if nav == "Main Forms":
    category = st.sidebar.radio(
        "Request type",
        [
            "NDIS",
            "Visa and Immigration Issues",
            "Meeting Request",
            "Event Invitation",
        ]
    )

    st.sidebar.markdown("---")
    st.sidebar.write("Emails route to the voter ID inbox with standardised subject lines.")
    st.sidebar.write("Attachments (where applicable) are included.")

    if category == "NDIS":
        ok, data, files = ndis_form()
        if ok:
            # store + enrich
            json_path, enriched = store_json_snapshot(data, prefix="ndis")
            # webhook
            if not post_to_power_automate(enriched):
                enqueue(enriched)
            # email
            subject = email_subject(enriched)
            body = email_body(enriched)
            send_email(subject, body, attachments=(files or []) + [json_path])
            st.success("NDIS enquiry submitted. We’ll be in touch.")

    elif category == "Visa and Immigration Issues":
        ok, data, files = visa_form()
        if ok:
            json_path, enriched = store_json_snapshot(data, prefix="visa")
            if not post_to_power_automate(enriched):
                enqueue(enriched)
            subject = email_subject(enriched)
            body = email_body(enriched)
            send_email(subject, body, attachments=(files or []) + [json_path])
            if enriched.get("kooyong_resident") == "No":
                st.warning("We’ve noted the applicant is not a Kooyong resident. Please contact your local MP.")
            if enriched.get("actor") == "Representative" and enriched.get("form_956_confirm") == "No":
                st.warning("Representative flagged without Form 956. Home Affairs will not act without it.")
            st.success("Visa enquiry submitted.")

    elif category == "Meeting Request":
        ok, data = meeting_form()
        if ok:
            json_path, enriched = store_json_snapshot(data, prefix="meeting")
            if not post_to_power_automate(enriched):
                enqueue(enriched)
            fpath = generate_meeting_docx(enriched)
            subject = email_subject(enriched)
            body = email_body(enriched) + f"\n\nAttached: {os.path.basename(fpath)}"
            send_email(subject, body, attachments=[fpath, json_path])
            st.success("Meeting request submitted.")

    elif category == "Event Invitation":
        ok, data = event_form()
        if ok:
            json_path, enriched = store_json_snapshot(data, prefix="event")
            if not post_to_power_automate(enriched):
                enqueue(enriched)
            fpath = generate_event_docx(enriched)
            subject = email_subject(enriched)
            body = email_body(enriched) + f"\n\nAttached: {os.path.basename(fpath)}"
            send_email(subject, body, attachments=[fpath, json_path])
            st.success("Event invitation submitted.")

elif nav == "Retry Queue Admin":
    from admin.queue_admin import queue_admin
    queue_admin()
