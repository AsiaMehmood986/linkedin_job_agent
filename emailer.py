"""Step 4: email through Resend (resend.com).
One email with two tables: Lahore jobs first, then Worldwide jobs.
Columns: Job title | Location | Work type | Link."""
import html
import sys

import requests

import config
from utils import log

RESEND_URL = "https://api.resend.com/emails"


def send_email(subject, text_body, html_body, attachments=None):
    if not config.RESEND_API_KEY:
        sys.exit("Set RESEND_API_KEY in .env first.")
    if not config.EMAIL_TO:
        sys.exit("Set EMAIL_TO in .env first (the address that receives the jobs).")
    payload = {
        "from": config.EMAIL_FROM,
        "to": [x.strip() for x in config.EMAIL_TO.split(",") if x.strip()],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }
    if attachments:
        payload["attachments"] = attachments
    headers = {
        "Authorization": f"Bearer {config.RESEND_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "job-agent/1.0",
    }
    try:
        r = requests.post(RESEND_URL, json=payload, headers=headers, timeout=60)
    except requests.RequestException as e:
        sys.exit(f"Could not reach Resend ({type(e).__name__}). Check your internet.")
    if r.status_code >= 400:
        sys.exit(f"Resend error {r.status_code}: {r.text}\n"
                 "Common causes: wrong API key; using onboarding@resend.dev while EMAIL_TO "
                 f"({config.EMAIL_TO}) is not the email you signed up to Resend with; or EMAIL_FROM "
                 f"({config.EMAIL_FROM}) uses a domain you have not verified in Resend.")
    return r.json()


def _esc(value):
    return html.escape(str(value or ""))


def _html_table(title, jobs):
    if not jobs:
        return f"<h2>{title}</h2><p>No new matching jobs in this run.</p>"
    rows = "".join(
        "<tr>"
        f"<td><b>{_esc(j['title'])}</b><br><small>{_esc(j['company'])} &middot; "
        f"match {j['score']}%</small></td>"
        f"<td>{_esc(j['location'])}</td>"
        f"<td>{_esc(j['mode'])}</td>"
        f"<td><a href='{_esc(j['url'])}'>Apply</a></td>"
        "</tr>"
        for j in jobs
    )
    return (
        f"<h2>{title} ({len(jobs)})</h2>"
        "<table border='1' cellpadding='6' cellspacing='0' "
        "style='border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px'>"
        "<tr style='background:#eee'><th>Job title</th><th>Location</th>"
        "<th>Work type</th><th>Link</th></tr>"
        f"{rows}</table>"
    )


def _text_table(title, jobs):
    if not jobs:
        return f"{title}: no new matching jobs in this run.\n"
    lines = [f"- {j['title']} | {j['company']} | {j['location']} | {j['mode']} | {j['url']}"
             for j in jobs]
    return f"{title} ({len(jobs)})\n" + "\n".join(lines) + "\n"


def send_digest(lahore, worldwide):
    """Send one email with the Lahore table and the Worldwide table."""
    if not lahore and not worldwide and not config.SEND_EMPTY_DIGEST:
        log("Emailer: no matching jobs this run, no email sent.")
        return
    if lahore or worldwide:
        subject = f"Job digest: {len(lahore)} in Lahore, {len(worldwide)} worldwide"
    else:
        subject = "Job digest: no new matches this run"
    text_body = _text_table("LAHORE JOBS", lahore) + "\n" + _text_table("WORLDWIDE JOBS", worldwide)
    html_body = (
        "<html><body style='font-family:Arial,sans-serif'>"
        + _html_table("Lahore Jobs", lahore) + "<br>"
        + _html_table("Worldwide Jobs", worldwide)
        + "<p><small>Review each posting before you apply. The agent does not apply for you.</small></p>"
        "</body></html>"
    )
    send_email(subject, text_body, html_body)
    log(f"Emailer: ONE email sent with {len(lahore)} Lahore and {len(worldwide)} worldwide jobs "
        f"to {config.EMAIL_TO}")
