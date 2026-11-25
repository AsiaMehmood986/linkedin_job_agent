"""Job agent. Run:  python main.py --help"""
import argparse
import time

import config
from cv_reader import extract_skills_from_folder
from emailer import send_digest, send_email
from linkedin_search import search_all
from matcher import match_jobs
from utils import load_seen, log, save_seen


def get_skills():
    log(f"CV reader: reading PDFs in {config.CV_FOLDER}")
    skills = extract_skills_from_folder(
        config.CV_FOLDER, blocked=config.BLOCKED_SKILLS, extra=config.EXTRA_SKILLS)
    log(f"CV reader: final skills = {skills}")
    return skills


def split_tables(jobs):
    """Lahore table: jobs located in Lahore. Worldwide table: everything else."""
    lahore = [j for j in jobs if "lahore" in j["location"].lower()]
    lahore_ids = {j["id"] for j in lahore}
    worldwide = [j for j in jobs if j["id"] not in lahore_ids]
    worldwide.sort(key=lambda j: 0 if j["mode"] == "Remote" else 1)
    return lahore[:config.MAX_PER_TABLE], worldwide[:config.MAX_PER_TABLE]


def run_once(dry_run=False):
    seen = load_seen(config.SEEN_FILE)
    skills = get_skills()
    jobs = search_all(skills)
    good = match_jobs(jobs, skills, seen)
    lahore, worldwide = split_tables(good)
    if dry_run:
        for label, group in (("LAHORE", lahore), ("WORLDWIDE", worldwide)):
            print(f"\n== {label} ({len(group)})")
            for j in group:
                print(f"- [{j['score']}%] {j['title']} | {j['company']} | "
                      f"{j['mode']} | {j['location']}\n  {j['url']}")
        log("Dry run: no email sent, seen list not saved.")
        return
    send_digest(lahore, worldwide)     # ONE email: Lahore table + Worldwide table
    save_seen(config.SEEN_FILE, seen)  # saved only after the email went out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show-skills", action="store_true", help="only show skills found in CVs")
    ap.add_argument("--test-email", action="store_true", help="send a test email")
    ap.add_argument("--dry-run", action="store_true", help="print matches, send nothing")
    ap.add_argument("--loop", action="store_true", help="repeat every CHECK_EVERY_HOURS")
    args = ap.parse_args()

    if args.show_skills:
        get_skills()
        return
    if args.test_email:
        send_email("Job agent test", "Your email settings work.", "<p>Your email settings work.</p>")
        log("Test email sent.")
        return
    if not args.loop:
        run_once(args.dry_run)
        return

    log(f"Loop mode: every {config.CHECK_EVERY_HOURS} hours. Ctrl+C to stop.")
    while True:
        try:
            run_once(args.dry_run)
        except Exception as e:
            log(f"Run failed: {e}")
        time.sleep(config.CHECK_EVERY_HOURS * 3600)


if __name__ == "__main__":
    main()
