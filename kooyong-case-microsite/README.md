# Kooyong Case Support Portal (Streamlit)

Accessible triage microsite for NDIS, Visa, Meeting, and Event requests.
- Monique-branded UI (assets/brand.css)
- JSON snapshot on every submission (submissions/)
- Email routing to **hudson@moniqueryan.com.au** with DOCX + JSON attachment
- Power Automate webhook for live ingestion (+ retry queue + admin UI)
- Admin tools: retry queue view, resend/delete, purge, filtered ZIP/CSV export

## 1) Folder Structure

```
case-microsite/
├── app.py
├── assets/
│   └── brand.css
├── admin/
│   └── queue_admin.py
├── forms/
│   ├── ndis_form.py
│   ├── visa_form.py
│   ├── meeting_form.py
│   └── event_form.py
├── utils/
│   ├── email_utils.py
│   ├── docx_utils.py
│   ├── json_utils.py
│   ├── webhook_utils.py
│   └── retry_queue.py
├── templates/
│   ├── (place your DOCX templates here: Meeting/Event/NDIS/Visa)
├── generated_docs/
├── submissions/
├── requirements.txt
└── README.md
```

## 2) Local Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Required: SMTP creds (Gmail App Password recommended)
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER="YOUR_GMAIL_ADDRESS"
export SMTP_PASS="YOUR_APP_PASSWORD"

# Optional: Power Automate Webhook
export POWER_AUTOMATE_WEBHOOK="https://prod-.../invoke?..."
# Optional: Admin key for the queue admin page
export ADMIN_KEY="some-strong-secret"

streamlit run app.py
```

- **Email address** is hard-coded to send to **hudson@moniqueryan.com.au** in `utils/email_utils.py` (`DEFAULT_TO`). Change if needed.
- **Webhook URL** is set via `POWER_AUTOMATE_WEBHOOK`. If blank, webhook POSTs are skipped and queued for retry.
- **SharePoint/Dataverse** pointers live *in your Flow*, not in this app. Configure your Flow to accept our JSON and route into your lists/tables/libraries.

## 3) Deploy on Streamlit Cloud

1. Push this folder to a **public GitHub repo**.
2. In Streamlit Cloud:
   - Point to `app.py`
   - Set **Secrets / Environment Variables**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `POWER_AUTOMATE_WEBHOOK`, `ADMIN_KEY` (optional)
3. Deploy. The retry worker runs in the background thread.

## 4) What Gets Saved/Sent

- **JSON Snapshot**: `submissions/{prefix}_{family}_{timestamp}.json` with:
  - `submission_id` (UUID4)
  - `timestamp_iso` (ISO-8601, UTC)
  - `family_name` (derived from best-available name field)
  - All form fields
- **DOCX**: Meeting/Event briefs in `generated_docs/` with filename `*_{family}_{timestamp}.docx`
- **Email**: Subject includes category, name, family name, ISO timestamp. Attachments include DOCX (when applicable) and the JSON snapshot.

## 5) Admin Console

Sidebar → **Retry Queue Admin**:
- View queued JSONs
- Resend or delete single items
- Purge entire queue
- Export **filtered** JSONs as ZIP
- Export **CSV summary** for chosen date range and case types

*(Protect with `ADMIN_KEY` if needed.)*

## 6) Where to change things

- **Email recipient**: `utils/email_utils.py` → `DEFAULT_TO`
- **From address**: Set `DEFAULT_FROM` env var or rely on `SMTP_USER`
- **Webhook URL**: `POWER_AUTOMATE_WEBHOOK` env var (in Streamlit Secrets)
- **Branding**: `assets/brand.css`
- **Form fields**: `forms/*.py`
- **DOCX layout**: `utils/docx_utils.py` (we can later map to content-controls)

## 7) Notes on Templates

Place your real Word templates in `templates/` for reference. Current DOCX generation uses plain text fields that mirror your structures. We can add a docxtpl-based merge to map into true Content Controls in a subsequent pass.

## 8) Troubleshooting

- Emails not sending? Check `SMTP_USER/PASS` and Gmail App Passwords.
- Webhook not receiving? Confirm the Flow URL and that the trigger is set to “When an HTTP request is received”.
- Queue not clearing? Use the Admin console to resend or purge.
