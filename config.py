"""All settings live here.
Change the numbers and words in the SETTINGS section below. Only the API keys and
email addresses come from GitHub Secrets (or a local .env file)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ============================================================
#  SETTINGS YOU CAN CHANGE (edit the numbers/words below)
# ============================================================
# Search depth
MAX_SEARCH_KEYWORDS = 8        # how many of your skills are used as search words
MAX_PAGES_PER_SEARCH = 3       # pages per search, 25 jobs each (3 = up to 75 jobs)
MAX_DETAIL_FETCH = 200         # job pages read per run
POSTED_WITHIN_HOURS = 72       # only jobs posted in the last N hours

# Matching
MIN_MATCHED_SKILLS = 1         # a job must mention at least this many of your skills
MIN_SCORE = 0                  # extra % threshold (0 = off)
EMAIL_ALL_JOBS = False         # False = only skill matches are emailed

# Tables
WORLDWIDE_WORK_TYPES = ["remote"]          # worldwide table: remote only
MAX_PER_TABLE = 200                        # max rows per table
ONSITE_LOCATIONS = ["Lahore, Pakistan", "Lahore, Punjab, Pakistan"]  # Lahore searches

# Email
SEND_EMPTY_DIGEST = False      # True = also send an email when nothing matched
CHECK_EVERY_HOURS = 3          # used only with: python main.py --loop

# Words to ignore when reading CVs, and skills to always add
BLOCKED_SKILLS = ["huawei", "islamabad"]
EXTRA_SKILLS = []

# ============================================================
#  Technical settings (no need to change)
# ============================================================
def _env(name, default):
    value = (os.getenv(name) or "").strip()
    return value if value else default


# CV PDFs are read from the code folder unless CV_FOLDER is set
CV_FOLDER = _env("CV_FOLDER", str(Path(__file__).resolve().parent))

# Worldwide table uses a single worldwide search per keyword
REMOTE_LOCATIONS = ["Worldwide"]
REMOTE_FALLBACK = ["United States", "United Kingdom", "Canada", "Germany", "Netherlands",
                   "Australia", "United Arab Emirates", "Singapore"]
PAGE_SIZE = 25

# Email (Resend: resend.com). Keys come from GitHub Secrets.
RESEND_API_KEY = _env("RESEND_API_KEY", "")
EMAIL_FROM = _env("EMAIL_FROM", "Job Agent <onboarding@resend.dev>")
EMAIL_TO = _env("EMAIL_TO", "")

# Tailored CVs (not used in the current flow)
TAILOR_CVS = False
TAILOR_TOP_N = 16
BASE_CV = ""
OUTPUT_DIR = Path(__file__).resolve().parent / "tailored_cvs"

SEEN_FILE = str(Path(__file__).resolve().parent / "seen_jobs.json")
