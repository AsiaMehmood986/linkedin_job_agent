"""Step 3: apply the location and work-type rules, then score jobs against your skills.

Lahore table   : any work type located in Lahore, plus remote jobs elsewhere in Pakistan.
Worldwide table: work types listed in WORLDWIDE_WORK_TYPES (default remote, hybrid, on-site).
A job is kept when it mentions at least MIN_MATCHED_SKILLS of your skills (default 1).
Jobs are sorted by how many of your skills they match.
"""
import random
import re
import time

import config
from linkedin_search import fetch_description
from utils import log

HYBRID = re.compile(r"\bhybrid\b", re.I)
ONSITE = re.compile(r"\bon[- ]?site\b|\bin[- ]office\b|\bin[- ]person\b", re.I)
REMOTE = re.compile(r"\bremote\b", re.I)


def _norm(s):
    return s.lower().replace("-", "").replace(" ", "")


WORLDWIDE_TYPES = {_norm(x) for x in config.WORLDWIDE_WORK_TYPES}


def _has(skill, text):
    return re.search(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", text) is not None


def skill_hit(skill, text):
    """True if the skill phrase is present, or (for 2-word skills) both words are present."""
    if _has(skill, text):
        return True
    words = skill.split()
    return len(words) > 1 and all(_has(w, text) for w in words)


def work_mode(job, description):
    """Check the title and location first, then the description."""
    for text in (f"{job['title']} {job['location']}", description):
        if HYBRID.search(text):
            return "Hybrid"
        if REMOTE.search(text):
            return "Remote"
        if ONSITE.search(text):
            return "On-site"
    return "Not stated"


def in_lahore(job):
    return "lahore" in job["location"].lower()


def fits_rules(job, description):
    mode = work_mode(job, description)
    if in_lahore(job):
        return True, ""
    if job["work_type"] == "lahore":          # Lahore search, but located elsewhere
        if mode == "Remote":
            return True, ""
        return False, "not in Lahore and not remote"
    kind = _norm("Remote" if mode == "Not stated" else mode)   # worldwide search
    if kind not in WORLDWIDE_TYPES:
        return False, f"{mode} not in your worldwide types"
    return True, ""


def score_job(job, skills, description):
    text = f"{job['title']} {description}".lower()
    matched = [s for s in skills if skill_hit(s, text)]
    score = min(80, int(len(matched) / max(1, min(len(skills), 8)) * 80))
    if any(skill_hit(s, job["title"].lower()) for s in skills):
        score += 20
    return min(score, 100), matched


def match_jobs(jobs, skills, seen):
    fresh = [j for j in jobs if j["id"] not in seen][:config.MAX_DETAIL_FETCH]
    log(f"Matcher: reading {len(fresh)} new jobs")
    keep = []
    for job in fresh:
        desc = fetch_description(job["id"])
        time.sleep(random.uniform(2, 4))
        if not desc:
            log(f"  SKIPPED (could not read job page, will retry next run): {job['title']}")
            continue
        seen[job["id"]] = job["title"]

        ok, why = fits_rules(job, desc)
        if not ok:
            log(f"  REJECTED [{why}] {job['title']} | {job['company']} | {job['location']}")
            continue

        job["mode"] = work_mode(job, desc)
        job["score"], job["matched"] = score_job(job, skills, desc)
        job["is_match"] = (len(job["matched"]) >= config.MIN_MATCHED_SKILLS
                           and job["score"] >= config.MIN_SCORE)
        tag = "MATCH" if job["is_match"] else "low  "
        log(f"  {tag} {job['score']:>3}% | {job['mode']} | {job['title']} | "
            f"{job['company']} | {job['location']}")
        if job["is_match"] or config.EMAIL_ALL_JOBS:
            keep.append(job)
    keep.sort(key=lambda j: j["score"], reverse=True)
    log(f"Matcher: {len(keep)} jobs for the email (out of {len(fresh)} read)")
    return keep
