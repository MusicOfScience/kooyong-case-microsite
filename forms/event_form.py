import streamlit as st

def event_form():
    st.subheader("Event Invitation")

    with st.form("event_form", clear_on_submit=False):
        event_name = st.text_input("Name of event *")
        location = st.text_input("Location")
        purpose = st.text_area("Purpose of event and MR’s attendance *")
        date = st.text_input("Date (free text or 2025-11-13)")
        start = st.text_input("Start time")
        end = st.text_input("End time")
        staff = st.text_area("Staff attending")
        volunteers = st.text_area("Volunteers attending")
        contact_name = st.text_input("Key contact name")
        contact_phone = st.text_input("Key contact phone")
        contact_email = st.text_input("Key contact email")
        who_meets = st.text_input("Who will meet MR?")
        other_invitees = st.text_area("Notes on other invitees")
        previous = st.text_area("Previous engagements w/ group")
        initiated_by = st.text_input("Who initiated invitation?")
        parking = st.text_area("Carparking details")
        duties = st.text_area("Speech/official duties")
        dress = st.text_input("Dress code")
        background = st.text_area("Background to Organization and Event")

        submitted = st.form_submit_button("Submit Event Invitation")

    if submitted:
        data = {
            "category": "Event Invitation",
            "event_name": event_name,
            "location": location,
            "purpose": purpose,
            "date": date,
            "start": start,
            "end": end,
            "staff": staff,
            "volunteers": volunteers,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "who_meets": who_meets,
            "other_invitees": other_invitees,
            "previous": previous,
            "initiated_by": initiated_by,
            "parking": parking,
            "duties": duties,
            "dress": dress,
            "background": background,
        }
        return True, data
    return False, None
