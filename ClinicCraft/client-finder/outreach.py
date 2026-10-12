#!/usr/bin/env python3
"""Prepare and optionally send approved ClinicCraft outreach. Safe by default."""
import argparse, csv, os, re, smtplib, ssl, sqlite3, sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
CSV_PATH = DATA / "outreach_queue.csv"
DB_PATH = DATA / "outreach_state.sqlite3"
MAX_DAILY = min(max(int(os.getenv("MAX_EMAILS_PER_DAY", "20")), 1), 20)
FIELDS = ["lead_id","organization","contact_name","email","source_url","why_relevant","service","contact_basis","approved","status","opt_out","bounced","replied","last_sent_utc","notes"]
VALID_BASIS = {"public_request", "explicit_permission", "existing_business_relationship"}

def connect():
    db = sqlite3.connect(DB_PATH)
    db.execute("CREATE TABLE IF NOT EXISTS events (lead_id TEXT PRIMARY KEY, email TEXT NOT NULL, status TEXT NOT NULL, sent_utc TEXT, updated_utc TEXT NOT NULL, notes TEXT DEFAULT '')")
    db.execute("CREATE TABLE IF NOT EXISTS suppressions (email TEXT PRIMARY KEY, reason TEXT NOT NULL, created_utc TEXT NOT NULL)")
    return db

def ensure_csv():
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()

def read_queue():
    ensure_csv()
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def write_queue(rows):
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})

def norm(s): return (s or "").strip().lower()
def valid_email(s): return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", (s or "").strip()))

def make_message(row):
    org = row.get("organization","").strip() or "there"
    service = row.get("service","").strip() or "presentation and document formatting"
    reason = row.get("why_relevant","").strip()
    reason_line = f"I noticed your public request about {reason[:220]}. " if reason else ""
    return (
        f"Subject: Help with {service}\n\n"
        f"Hello {row.get('contact_name','').strip() or org} team,\n\n"
        f"{reason_line}I run ClinicCraft, a small student-led service for clear presentation and document formatting. "
        f"I can help with {service}. PowerPoint cleanup starts at ₹299 for up to 10 slides, and document/report layout starts at ₹249. "
        f"You can see the service details here: https://aether56tk.github.io/ME/ClinicCraft/\n\n"
        f"If this is relevant, I’d be happy to discuss the scope and turnaround before you decide. If not, no action is needed.\n\n"
        f"Regards,\nClinicCraft\ncliniccraft.studio@gmail.com\n"
        f"If you prefer not to receive further messages from ClinicCraft, reply “unsubscribe”."
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--drafts", action="store_true")
    ap.add_argument("--send", action="store_true")
    args = ap.parse_args()
    ensure_csv()
    db = connect()
    rows = read_queue()
    if args.init:
        print(f"Created review queue: {CSV_PATH}")
        print("Add individually relevant leads manually; do not bulk-harvest email addresses.")
        return
    if args.drafts:
        for row in rows:
            if norm(row.get("status")) in {"", "new", "draft"}:
                print("="*72)
                print(f"Lead: {row.get('organization')} | {row.get('email')} | {row.get('source_url')}")
                print(make_message(row))
        return
    if not args.send:
        print("Dry-run only. Use --drafts to preview. Sending requires --send and ENABLE_EMAIL_SENDING=true.")
        print(f"Queue rows: {len(rows)}; daily cap: {MAX_DAILY}")
        return
    if os.getenv("ENABLE_EMAIL_SENDING","").lower() != "true":
        sys.exit("Blocked: ENABLE_EMAIL_SENDING must be explicitly set to true.")
    host = os.getenv("SMTP_HOST","smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT","465"))
    username = os.getenv("SMTP_USERNAME","")
    password = os.getenv("SMTP_APP_PASSWORD","")
    if not username or not password:
        sys.exit("Blocked: configure SMTP_USERNAME and SMTP_APP_PASSWORD as environment secrets.")
    today = datetime.now(timezone.utc).date().isoformat()
    sent_today = db.execute("SELECT COUNT(*) FROM events WHERE status='sent' AND substr(sent_utc,1,10)=?",(today,)).fetchone()[0]
    remaining = max(0, MAX_DAILY - sent_today)
    if remaining == 0: sys.exit(f"Daily sending cap ({MAX_DAILY}) reached.")
    sent = 0
    for row in rows:
        if sent >= remaining: break
        email = norm(row.get("email"))
        status = norm(row.get("status"))
        approved = norm(row.get("approved")) in {"yes","true","approved"}
        flags = any(norm(row.get(k)) in {"yes","true","1"} for k in ("opt_out","bounced","replied"))
        basis = norm(row.get("contact_basis"))
        lead_id = (row.get("lead_id") or "").strip()
        if not lead_id or not valid_email(email) or not approved or status not in {"approved","draft","new"}: continue
        if basis not in VALID_BASIS or flags or not row.get("source_url","").strip() or not row.get("why_relevant","").strip(): continue
        if db.execute("SELECT 1 FROM suppressions WHERE email=?",(email,)).fetchone(): continue
        if db.execute("SELECT 1 FROM events WHERE lead_id=? OR email=?",(lead_id,email)).fetchone(): continue
        raw = make_message(row)
        subject = raw.splitlines()[0].removeprefix("Subject: ").strip()
        body = "\n".join(raw.splitlines()[2:])
        msg = EmailMessage()
        msg["From"] = username; msg["To"] = email; msg["Subject"] = subject; msg["Reply-To"] = username
        msg.set_content(body)
        try:
            with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=20) as server:
                server.login(username, password)
                server.send_message(msg)
            now = datetime.now(timezone.utc).isoformat()
            db.execute("INSERT INTO events(lead_id,email,status,sent_utc,updated_utc) VALUES(?,?,?,?,?)",(lead_id,email,"sent",now,now))
            row["status"] = "sent"; row["last_sent_utc"] = now
            sent += 1; db.commit()
            print(f"Sent approved message to {email}")
        except Exception as exc:
            row["status"] = "send_error"
            row["notes"] = (row.get("notes","") + f" | send error: {type(exc).__name__}").strip(" |")
            print(f"Failed for {email}: {type(exc).__name__}")
    write_queue(rows)
    print(f"Sent {sent}; cap {MAX_DAILY}/day. This prototype does not automatically read replies/bounces; mark those promptly and suppress opt-outs.")

if __name__ == "__main__": main()
