"""Step 4: email through Resend (resend.com).
One styled email: Lahore jobs first, then worldwide remote jobs."""
import html
import sys

import requests

import config
from utils import log

RESEND_URL = "https://api.resend.com/emails"
BRAND = "AsHa Job Alert"

# ---- Colours and layout (change these to restyle the email) ----
COLS = ["44%", "22%", "14%", "20%"]        # job title, location, work type, link
PRIMARY = "#4338ca"        # header banner colour (indigo)
LAHORE_ACCENT = "#0f766e"  # Lahore section colour (teal)
WORLD_ACCENT = "#4338ca"   # worldwide section colour (indigo)
BADGE = {
    "Remote": ("#dcfce7", "#166534"),
    "Hybrid": ("#fef3c7", "#92400e"),
    "On-site": ("#dbeafe", "#1e40af"),
}


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


def _pill(text):
    return (f"<span style='display:inline-block;padding:5px 12px;border-radius:999px;"
            f"background:#ffffff;color:{PRIMARY};font-size:13px;font-weight:600'>{text}</span>")


def _badge(mode):
    bg, fg = BADGE.get(mode, ("#e5e7eb", "#374151"))
    return (f"<span style='display:inline-block;padding:3px 10px;border-radius:999px;"
            f"background:{bg};color:{fg};font-size:12px;font-weight:600'>{_esc(mode)}</span>")


def _cell(content, align="left"):
    return (f"<td align='{align}' style='padding:12px 14px;vertical-align:middle;"
            f"border-top:1px solid #e2e8f0;font-size:14px;color:#334155'>{content}</td>")


def _section(title, accent, jobs):
    heading = (f"<div style='font-size:18px;font-weight:700;color:#0f172a;margin:22px 0 10px;"
               f"border-left:5px solid {accent};padding-left:10px'>{title} "
               f"<span style='color:#64748b;font-weight:400'>({len(jobs)})</span></div>")
    if not jobs:
        return heading + "<p style='margin:0 0 8px;color:#64748b;font-size:14px'>No matches in this run.</p>"

    cols = "<colgroup>" + "".join(f"<col style='width:{w}'>" for w in COLS) + "</colgroup>"
    th = "padding:12px 14px;color:#ffffff;font-size:13px;font-weight:600"
    head = (f"<tr style='background:{accent}'>"
            f"<th align='left' style='{th}'>Job title</th>"
            f"<th align='left' style='{th}'>Location</th>"
            f"<th align='left' style='{th}'>Work type</th>"
            f"<th align='center' style='{th}'>Link</th></tr>")

    rows = []
    for n, j in enumerate(jobs):
        bg = "#ffffff" if n % 2 == 0 else "#f8fafc"
        title_cell = (
            f"<div style='font-weight:700;color:#0f172a;font-size:14px'>{_esc(j['title'])}</div>"
            f"<div style='margin-top:4px;color:#64748b;font-size:12px'>{_esc(j['company'])} &middot; "
            f"<span style='color:{accent};font-weight:600'>{j['score']}% match</span></div>")
        link = (f"<a href='{_esc(j['url'])}' style='display:inline-block;padding:7px 14px;"
                f"background:{accent};color:#ffffff;text-decoration:none;border-radius:6px;"
                "font-size:12px;font-weight:600'>Apply</a>")
        rows.append(f"<tr style='background:{bg}'>"
                    + _cell(title_cell)
                    + _cell(_esc(j["location"]))
                    + _cell(_badge(j["mode"]))
                    + _cell(link, align="center")
                    + "</tr>")
    return (heading
            + "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' "
              "style='width:100%;table-layout:fixed;border-collapse:collapse;"
              "border:1px solid #e2e8f0'>"
            + cols + head + "".join(rows) + "</table>")


def _text_table(title, jobs):
    if not jobs:
        return f"{title}: no new matching jobs in this run.\n"
    lines = [f"- {j['title']} | {j['company']} | {j['location']} | {j['mode']} | {j['url']}"
             for j in jobs]
    return f"{title} ({len(jobs)})\n" + "\n".join(lines) + "\n"


def build_digest(lahore, worldwide):
    """Return (subject, text_body, html_body) for the digest email."""
    if lahore or worldwide:
        subject = f"🎯 {BRAND}: {len(lahore)} Lahore + {len(worldwide)} remote matches"
    else:
        subject = f"{BRAND}: no new matches this run"

    preheader = "Fresh matches from the last 24 hours, sorted by how well they fit you."
    html_body = (
        "<!DOCTYPE html><html><body style='margin:0;padding:0;background:#f1f5f9;"
        "font-family:Arial,Helvetica,sans-serif'>"
        f"<span style='display:none;max-height:0;overflow:hidden;opacity:0'>{preheader}</span>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' "
        "style='background:#f1f5f9'><tr><td align='center' style='padding:24px 12px'>"
        "<table role='presentation' width='640' cellpadding='0' cellspacing='0' "
        "style='width:640px;max-width:100%;background:#ffffff;border-radius:14px'>"
        f"<tr><td style='background:{PRIMARY};padding:26px 28px;color:#ffffff;border-radius:14px 14px 0 0'>"
        f"<div style='font-size:12px;letter-spacing:2px;opacity:.85'>{BRAND.upper()}</div>"
        "<div style='font-size:24px;font-weight:700;margin-top:6px'>Your matches for today</div>"
        f"<div style='margin-top:14px'>{_pill(f'{len(lahore)} in Lahore')} &nbsp; "
        f"{_pill(f'{len(worldwide)} remote worldwide')}</div>"
        "</td></tr>"
        "<tr><td style='padding:22px 28px 4px;color:#334155;font-size:15px;line-height:1.6'>"
        "Jobs that mention your skills, posted in the last 24 hours. Open each one with "
        "<b>Apply</b>, review it, then apply yourself."
        "</td></tr>"
        "<tr><td style='padding:0 28px 8px'>"
        + _section("Lahore jobs", LAHORE_ACCENT, lahore) +
        "</td></tr>"
        "<tr><td style='padding:0 28px 24px'>"
        + _section("Worldwide remote jobs", WORLD_ACCENT, worldwide) +
        "</td></tr>"
        "<tr><td style='background:#f8fafc;padding:16px 28px;color:#64748b;font-size:12px;"
        "text-align:center;border-radius:0 0 14px 14px'>"
        f"Sent by {BRAND}. The agent never applies for you."
        "</td></tr>"
        "</table></td></tr></table></body></html>"
    )
    text_body = _text_table("LAHORE JOBS", lahore) + "\n" + _text_table("WORLDWIDE JOBS", worldwide)
    return subject, text_body, html_body


def send_digest(lahore, worldwide):
    """Send one styled email with the Lahore table and the worldwide table."""
    if not lahore and not worldwide and not config.SEND_EMPTY_DIGEST:
        log("Emailer: no matching jobs this run, no email sent.")
        return
    subject, text_body, html_body = build_digest(lahore, worldwide)
    send_email(subject, text_body, html_body)
    log(f"Emailer: ONE email sent with {len(lahore)} Lahore and {len(worldwide)} worldwide jobs "
        f"to {config.EMAIL_TO}")
