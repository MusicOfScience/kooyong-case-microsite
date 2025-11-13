import streamlit as st
from datetime import date

def visa_form():
    st.subheader("Visa & Immigration Issues – Triage")

    with st.form("visa_form", clear_on_submit=False):
        actor = st.radio("Are you the applicant or a representative?", ["Applicant", "Representative"])
        kooyong_resident = st.radio(
            "Is the applicant a resident of the Kooyong electorate?",
            ["Yes", "No", "Unsure"],
            help="If not a Kooyong resident, please contact your local MP for assistance."
        )

        if kooyong_resident == "No":
            st.warning(
                "If the applicant does **not** live in Kooyong, please contact your **local federal MP** via the AEC website."
            )

        st.markdown("**Applicant details (required for all cases)**")
        full_name = st.text_input("Applicant full name *")
        dob = st.date_input("Applicant date of birth *", value=date(1990,1,1))
        passport_or_id = st.text_input("Passport number (or National ID if no passport)")
        address_on_file = st.text_input("Address currently on file with Department")
        home_affairs_ref = st.text_input("Home Affairs reference / application number")
        visa_subclass = st.text_input("Visa subclass applied for *")
        application_date = st.date_input("Date of application *")

        contact_email = st.text_input("Applicant contact email *")
        contact_phone = st.text_input("Applicant contact phone")

        st.markdown("**Status checks performed**")
        status_checks = st.multiselect(
            "What have you already checked or contacted?",
            [
                "Home Affairs online portal",
                "Global Service Centre (131 881)",
                "Global Feedback Unit escalation",
                "Processing time page + circumstances affecting processing",
                "Other"
            ]
        )

        st.markdown("**Representative details (if applicable)**")
        rep_name = rep_email = rep_phone = ""
        form_956_confirm = "N/A"
        form_956_upload = None

        if actor == "Representative":
            rep_name = st.text_input("Representative full name *")
            rep_email = st.text_input("Representative email *")
            rep_phone = st.text_input("Representative phone")
            form_956_confirm = st.radio("Has **Form 956** been completed and lodged by the applicant for you?", ["Yes", "No"])
            form_956_upload = st.file_uploader("Upload Form 956 (optional)")

        st.markdown("**Issue summary and assistance requested**")
        issue_summary = st.text_area("What is the issue? *")
        assistance = st.text_area("What assistance are you seeking from our office? *")

        submitted = st.form_submit_button("Submit Visa Enquiry")

    if submitted:
        data = {
            "category": "Visa",
            "actor": actor,
            "kooyong_resident": kooyong_resident,
            "full_name": full_name,
            "dob": str(dob),
            "passport_or_id": passport_or_id,
            "address_on_file": address_on_file,
            "home_affairs_ref": home_affairs_ref,
            "visa_subclass": visa_subclass,
            "application_date": str(application_date),
            "contact_email": contact_email,
            "contact_phone": contact_phone,
            "status_checks": status_checks,
            "rep_name": rep_name,
            "rep_email": rep_email,
            "rep_phone": rep_phone,
            "form_956_confirm": form_956_confirm,
            "issue_summary": issue_summary,
            "assistance": assistance,
        }

        saved_files = []
        if form_956_upload is not None:
            path = f"generated_docs/visa_956_{(rep_email or 'rep').replace('@','_at_')}_{form_956_upload.name}"
            with open(path, "wb") as f:
                f.write(form_956_upload.getbuffer())
            saved_files.append(path)

        return True, data, saved_files

    return False, None, None
