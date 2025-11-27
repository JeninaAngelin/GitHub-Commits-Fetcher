import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
AUTHOR_EMAIL = os.getenv("AUTHOR_EMAIL")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REQUEST_DELAY = 0.7   # seconds

def get_user_repos(username):
    """Fetch all repositories owned by the user."""
    url = f"https://api.github.com/users/{username}/repos"
    params = {"per_page": 100, "type": "owner"}

    time.sleep(REQUEST_DELAY)
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    return [repo["name"] for repo in response.json()]


def fetch_commits(repo):
    """Fetch ALL commits from a repo by author email (with pagination & delay)."""
    commits = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/commits"
        params = {
            "author": AUTHOR_EMAIL,
            "per_page": 100,
            "page": page
        }

        time.sleep(REQUEST_DELAY)
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"⚠️ Failed to fetch commits from {repo}. Skipping...")
            break

        page_data = response.json()
        if not page_data:
            break  # no more commits

        for commit in page_data:
            commits.append({
                "Repository": repo,
                "CommitID": commit["sha"],
                "Message": commit["commit"]["message"].strip(),
                "Date": commit["commit"]["author"]["date"]
            })

        page += 1

    return commits


print("\n📌 Fetching repositories for:", GITHUB_USERNAME)
repos = get_user_repos(GITHUB_USERNAME)

all_commits = []
for repo in repos:
    print(f"🔍 Fetching commits from: {repo}")
    all_commits.extend(fetch_commits(repo))

df = pd.DataFrame(all_commits)

if df.empty:
    print("\n❌ No commits found for this author email.")
    exit()

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(by="Date", ascending=False)

output_file = "github_commits.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"\n✅ Commit history saved to: {output_file}")
print(f"📈 Total commits found: {len(df)}")
