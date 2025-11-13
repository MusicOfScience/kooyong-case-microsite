import streamlit as st

def ndis_form():
    st.subheader("NDIS – Enquiry / Representation")

    with st.form("ndis_form", clear_on_submit=False):
        st.markdown("**Participant / Enquirer details**")
        participant_name = st.text_input("Participant Name *", help="As it appears to NDIA")
        enquirer_name = st.text_input("Enquirer Name (if different)")
        ndis_number = st.text_input("Participant NDIS Number")
        dob = st.date_input("Participant DOB")
        address = st.text_input("Participant Address")
        enquirer_phone = st.text_input("Enquirer Phone Number")
        enquirer_email = st.text_input("Enquirer Email Address")

        st.markdown("**Consent**")
        consent_has_authority = st.radio(
            "Does the enquirer have authority to act on behalf of the participant?",
            ["Yes", "No"],
            help="Plan Nominee / Authorised Representative / Child Representative / consent directly from participant"
        )

        consent_evidence = None
        if consent_has_authority == "Yes":
            consent_roles = st.multiselect(
                "Select all that apply",
                ["Plan Nominee", "Authorised Representative", "Child Representative", "Consent obtained by office from participant"]
            )
            consent_evidence = st.file_uploader("Upload evidence of consent (optional)")
        else:
            st.info("If no consent yet, our office will attempt to seek consent. You may upload any available consent form.")
            consent_evidence = st.file_uploader("Upload consent form (optional)")

        st.markdown("**Has the participant/enquirer attempted to resolve the issue via NDIS contacts?**")
        attempted = st.multiselect(
            "Select all that apply",
            ["1800 800 110", "Local Area Coordinator / ECEI Coordinator", "NDIS Contact", "Not yet"]
        )

        st.markdown("**Issue details & desired outcome**")
        issue_summary = st.text_area("Issue Summary *")
        desired_outcome = st.text_area("Desired Outcome / Action *")

        submitted = st.form_submit_button("Submit NDIS Enquiry")

    if submitted:
        data = {
            "category": "NDIS",
            "participant_name": participant_name,
            "enquirer_name": enquirer_name,
            "ndis_number": ndis_number,
            "dob": str(dob) if dob else "",
            "address": address,
            "enquirer_phone": enquirer_phone,
            "enquirer_email": enquirer_email,
            "consent_has_authority": consent_has_authority,
            "issue_summary": issue_summary,
            "desired_outcome": desired_outcome,
            "attempted_contacts": attempted,
        }

        saved_files = []
        if consent_evidence is not None:
            path = f"generated_docs/ndis_consent_{(enquirer_email or 'anon').replace('@','_at_')}_{consent_evidence.name}"
            with open(path, "wb") as f:
                f.write(consent_evidence.getbuffer())
            saved_files.append(path)

        return True, data, saved_files

    return False, None, None
