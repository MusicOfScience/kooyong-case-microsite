import streamlit as st

def meeting_form():
    st.subheader("Meeting Request")

    with st.form("meeting_form", clear_on_submit=False):
        meeting_title = st.text_input("Meeting Title *")
        location = st.text_input("Location")
        meeting_dt = st.text_input("Date and time (free text or 2025-11-13 14:00)")
        attendees = st.text_area("Attendees")
        contact_person = st.text_input("Contact person")
        contact_phone = st.text_input("Contact phone")
        contact_email = st.text_input("Contact email")
        purpose = st.text_area("What is the purpose of the meeting? *")
        previous_engagements = st.text_area("Notes on previous meetings/engagements")
        initiated_by = st.text_input("Who initiated the meeting?")
        agenda = st.text_area("Agenda (if available)")
        background = st.text_area("Background notes")
        notes = st.text_area("Notes from meeting")

        submitted = st.form_submit_button("Submit Meeting Request")

    if submitted:
        data = {
            "category": "Meeting Request",
            "meeting_title": meeting_title,
            "location": location,
            "meeting_dt": meeting_dt,
            "attendees": attendees,
            "contact_person": contact_person,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "purpose": purpose,
            "previous_engagements": previous_engagements,
            "initiated_by": initiated_by,
            "agenda": agenda,
            "background": background,
            "notes": notes,
        }
        return True, data
    return False, None
