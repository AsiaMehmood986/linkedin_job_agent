"""All settings live here. Values come from the .env file (or GitHub Actions secrets).
An empty value (e.g. a secret that was never set) falls back to the default."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env(name, default):
    value = (os.getenv(name) or "").strip()
    return value if value else default


def _list(name, default, sep=","):
    return [x.strip() for x in _env(name, default).split(sep) if x.strip()]


def _bool(name, default):
    return _env(name, "true" if default else "false").lower() in ("1", "true", "yes")


CV_FOLDER = _env("CV_FOLDER", str(Path(__file__).resolve().parent))
BLOCKED_SKILLS = _list("BLOCKED_SKILLS", "huawei,islamabad")  # words to ignore
EXTRA_SKILLS = _list("EXTRA_SKILLS", "")                       # skills to always add

# LAHORE table: searches here return remote, hybrid and on-site jobs.
ONSITE_LOCATIONS = _list("ONSITE_LOCATIONS", "Lahore, Pakistan|Lahore, Punjab, Pakistan", "|")

# WORLDWIDE table: one worldwide search per keyword.
REMOTE_LOCATIONS = ["Worldwide"]
# Used ONLY if the Worldwide search returns nothing (LinkedIn needs some location)
REMOTE_FALLBACK = ["United States", "United Kingdom", "Canada", "Germany", "Netherlands",
                   "Australia", "United Arab Emirates", "Singapore"]
# Work types allowed in the Worldwide table. The Lahore table always takes every type.
WORLDWIDE_WORK_TYPES = _list("WORLDWIDE_WORK_TYPES", "remote")

# Search depth
MAX_SEARCH_KEYWORDS = int(_env("MAX_SEARCH_KEYWORDS", "5"))
MAX_PAGES_PER_SEARCH = int(_env("MAX_PAGES_PER_SEARCH", "3"))   # LinkedIn gives 25 jobs per page
MAX_DETAIL_FETCH = int(_env("MAX_DETAIL_FETCH", "200"))         # job pages read per run
POSTED_WITHIN_HOURS = int(_env("POSTED_WITHIN_HOURS", "24"))

# Relevance
MIN_MATCHED_SKILLS = int(_env("MIN_MATCHED_SKILLS", "1"))  # a job needs at least this many of your skills
MIN_SCORE = int(_env("MIN_SCORE", "0"))                  # optional extra % threshold (0 = off)
EMAIL_ALL_JOBS = _bool("EMAIL_ALL_JOBS", False)          # False = only jobs that match your skills
MAX_PER_TABLE = int(_env("MAX_PER_TABLE", "200"))
SEND_EMPTY_DIGEST = _bool("SEND_EMPTY_DIGEST", False)    # True = email even when nothing matched
CHECK_EVERY_HOURS = float(_env("CHECK_EVERY_HOURS", "3"))

# Email (Resend: resend.com)
RESEND_API_KEY = _env("RESEND_API_KEY", "")
EMAIL_FROM = _env("EMAIL_FROM", "Job Agent <onboarding@resend.dev>")
EMAIL_TO = _env("EMAIL_TO", "")

# Tailored CVs (not used in the current flow)
TAILOR_CVS = _bool("TAILOR_CVS", True)
TAILOR_TOP_N = int(_env("TAILOR_TOP_N", "16"))
BASE_CV = _env("BASE_CV", "")
OUTPUT_DIR = Path(__file__).resolve().parent / "tailored_cvs"

SEEN_FILE = str(Path(__file__).resolve().parent / "seen_jobs.json")
