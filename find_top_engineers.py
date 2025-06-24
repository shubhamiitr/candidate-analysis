import os
from datetime import datetime, timedelta
from pathlib import Path
import pytz
import sys
import re
import argparse
from analyze_candidate import analyze_candidate
import shutil

CANDIDATES_DIR = Path("candidates")
CANDIDATES_DIR.mkdir(exist_ok=True)
PROCESSED_CANDIDATES_FILE = "processed_candidates.txt"

# Top LLM/AI repositories to analyze
INFLUENCER_REPOS = [
    ("Shubhamsaboo", "awesome-llm-apps"),
    ("aishwaryanr", "awesome-generative-ai-guide")
]

# Initialize cutoff date (make it timezone-aware)
CUTOFF_DAYS = 90
cutoff = datetime.now(pytz.UTC) - timedelta(days=CUTOFF_DAYS)

# --- Utility functions ---
def get_candidate_dir(github_url):
    if not github_url:
        return None
    dirname = github_url.rstrip('/').split('/')[-1]
    candidate_dir = CANDIDATES_DIR / dirname
    candidate_dir.mkdir(exist_ok=True)
    return candidate_dir

def get_report_path(github_url):
    if not github_url:
        return None
    return get_candidate_dir(github_url) / "report.md"

def is_candidate_processed(github_url):
    try:
        if not github_url or not os.path.exists(PROCESSED_CANDIDATES_FILE):
            return False
        with open(PROCESSED_CANDIDATES_FILE, 'r') as f:
            processed = set(line.strip() for line in f)
            return github_url in processed
    except Exception as e:
        print(f"Error checking processed candidates: {str(e)}")
        return False

def mark_candidate_processed(github_url):
    try:
        if github_url:
            with open(PROCESSED_CANDIDATES_FILE, 'a') as f:
                f.write(f"{github_url}\n")
    except Exception as e:
        print(f"Error marking candidate as processed: {str(e)}")
        sys.exit(1)

def move_report_to_status_folder(report_path):
    """Move the report to a subfolder based on the recommendation in the report."""
    with open(report_path, 'r') as f:
        content = f.read()
    recommendation_match = re.search(r'\*\*Recommendation:\*\*\s*([^\n]+)', content)
    if recommendation_match:
        recommendation = recommendation_match.group(1).strip().lower()
        base_dir = Path("candidates")
        if "strongly shortlist" in recommendation:
            folder = base_dir / "strongly_shortlist"
        elif "shortlist" in recommendation:
            folder = base_dir / "shortlist"
        else:
            folder = base_dir / "reject"
        folder.mkdir(exist_ok=True)
        shutil.move(str(report_path), str(folder / report_path.name))
        return folder / report_path.name
    return report_path

def analyze_user(user, repo, force_reanalysis=False):
    try:
        if not force_reanalysis and is_candidate_processed(user.html_url):
            return None
        p = user  # Use the PyGithub NamedUser object directly
        user_updated = p.updated_at.replace(tzinfo=pytz.UTC) if p.updated_at.tzinfo is None else p.updated_at
        if user_updated < cutoff:
            return None
        analysis = analyze_candidate(github_url=p.html_url)
        if analysis:
            report_path = get_report_path(p.html_url)
            if report_path:
                with open(report_path, 'w') as f:
                    f.write(analysis)
                # Move report to status folder
                new_report_path = move_report_to_status_folder(report_path)
            mark_candidate_processed(p.html_url)
            return {
                "login": p.login,
                "url": p.html_url,
                "analysis": analysis
            }
        return None
    except Exception as e:
        print(f"Fatal error analyzing user {user.login}: {str(e)}")
        sys.exit(1)

def get_shortlisted_candidates():
    all_candidates = {}
    base_dir = Path("candidates")
    for status_folder in ["shortlist", "strongly_shortlist"]:
        folder = base_dir / status_folder
        if not folder.exists():
            continue
        for report_path in folder.glob("*/report.md"):
            with open(report_path, 'r') as f:
                content = f.read()
                eval_status = re.search(r'\*\*Recommendation:\*\*\s*([^\n]+)', content)
                name = re.search(r'\*\*Name:\*\*\s*([^\n]+)', content)
                location = re.search(r'\*\*Location:\*\*\s*([^\n]+)', content)
                linkedin = re.search(r'\*\*LinkedIn:\*\*\s*([^\n]+)', content)
                github = re.search(r'\*\*GitHub:\*\*\s*([^\n]+)', content)
                candidate_info = {
                    'name': name.group(1).strip() if name else 'Unknown',
                    'location': location.group(1).strip() if location else 'Unable to verify',
                    'linkedin': linkedin.group(1).strip() if linkedin else 'Unable to verify',
                    'github': github.group(1).strip() if github else 'Unknown',
                    'evaluation_status': eval_status.group(1).strip() if eval_status else 'Limited',
                    'report_path': str(report_path),
                    'last_updated': os.path.getmtime(report_path)
                }
                key = github.group(1).strip() if github else None
                if key:
                    all_candidates[key] = candidate_info
    shortlisted = sorted(all_candidates.values(), key=lambda x: x['last_updated'], reverse=True)
    return shortlisted

def main():
    parser = argparse.ArgumentParser(description='Find top shortlisted product engineering candidates')
    parser.add_argument('--force-reanalysis', action='store_true', help='Force reanalysis of cached users')
    parser.add_argument('--top-n', type=int, default=20, help='Number of shortlisted candidates to show')
    args = parser.parse_args()

    import github
    gh = github.Github(os.getenv('GITHUB_TOKEN'))
    shortlisted = get_shortlisted_candidates()
    processed_users = set()
    for c in shortlisted:
        processed_users.add(c['github'])

    print("\nAnalyzing candidates until at least 20 are shortlisted...")
    for owner, repo_name in INFLUENCER_REPOS:
        repo = gh.get_repo(f"{owner}/{repo_name}")
        stargazers = repo.get_stargazers()
        for user in stargazers:
            if len(shortlisted) >= args.top_n:
                break
            if user.html_url in processed_users:
                continue
            result = analyze_user(user, repo, args.force_reanalysis)
            if result:
                processed_users.add(result['url'])
                shortlisted = get_shortlisted_candidates()
    if not shortlisted:
        print("\nNo suitable candidates found!")
        sys.exit(1)
    print(f"\nTop {args.top_n} Shortlisted Product Engineering Candidates:")
    print("=" * 50)
    for i, engineer in enumerate(shortlisted[:args.top_n], 1):
        print(f"\n{i}. {engineer['name']}")
        print(f"   Location: {engineer['location']}")
        print(f"   LinkedIn: {engineer['linkedin']}")
        print(f"   GitHub: {engineer['github']}")
        print(f"   Evaluation Status: {engineer['evaluation_status']}")
        print(f"   Report: {engineer['report_path']}")

if __name__ == "__main__":
    main()
