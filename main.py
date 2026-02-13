import requests
import time
import os
import logging
import sqlite3

# --- Configuration via Environment Variables ---
# Use .env file for local development, or set these in your environment
GH_TOKEN = os.getenv("GH_TOKEN")
NTFY_TOKEN = os.getenv("NTFY_TOKEN")
NTFY_URL = os.getenv("NTFY_URL")
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300"))
DB_PATH = os.getenv("DB_PATH", "/app/data/notifications.db")

# Public GitHub icon URL for ntfy
GITHUB_ICON_URL = "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s'
)


def init_db():
    """
    Initializes the SQLite database to track notifications and prevent duplicates.
    Creates the necessary data directory if it doesn't exist.
    """
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS seen_notifs (thread_id TEXT PRIMARY KEY, updated_at TEXT)")
    conn.commit()
    return conn


def get_html_url(subject):
    """Parses GitHub API subject URLs into human-readable browser URLs."""
    api_url = subject.get('url')
    if not api_url:
        return "https://github.com/notifications"

    url = api_url.replace("api.github.com/repos", "github.com")
    url = url.replace("/pulls/", "/pull/").replace("/releases/", "/releases/tag/")

    if "check-runs" in url or "check-suites" in url:
        return url.replace("github.com/", "github.com/").split("/check-")[0] + "/actions"

    return url


def check_github_notifications(cursor, conn):
    """
    Fetches unread notifications from the GitHub API and filters them using a local database
    to avoid duplicate notifications.

    Args:
        cursor: SQLite cursor object for database queries.
        conn: SQLite connection object for committing transactions.
    """
    headers = {
        "Authorization": f"token {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Only fetch notifications that are not marked as read.
    params = {"all": "false"}

    try:
        response = requests.get(
            "https://api.github.com/notifications",
            headers=headers,
            params=params,
            timeout=15
        )
        response.raise_for_status()
        notifications = response.json()

        for n in notifications:
            thread_id = n['id']
            last_updated = n['updated_at']

            cursor.execute(
                "SELECT 1 FROM seen_notifs WHERE thread_id=? AND updated_at=?",
                (thread_id, last_updated)
            )

            if not cursor.fetchone():
                repo = n['repository']['full_name']
                subject = n['subject']
                title = subject['title']
                n_type = subject['type']
                reason = n['reason']
                web_url = get_html_url(subject)

                send_to_ntfy(repo, title, n_type, reason, web_url)

                cursor.execute(
                    "INSERT OR REPLACE INTO seen_notifs VALUES (?, ?)",
                    (thread_id, last_updated)
                )
                conn.commit()

    except Exception as e:
        logging.error(f"GitHub API sync failed: {e}")


def send_to_ntfy(repo, title, n_type, reason, web_url):
    """
    Sends a formatted notification to the ntfy server.

    Args:
        repo: The full name of the GitHub repository.
        title: The title of the notification subject.
        n_type: The type of notification (e.g., 'PullRequest', 'Issue').
        reason: The reason for the notification (e.g., 'mention', 'subscribed').
        web_url: The browser-friendly URL to the notification subject.
    """
    # Configuration for different notification types
    type_configs = {
        'PullRequest': {'tag': 'git,pull_request', 'prio': '4', 'emoji': '🔀'},
        'Issue': {'tag': 'memo,issue', 'prio': '3', 'emoji': '📌'},
        'Release': {'tag': 'package,shipit', 'prio': '5', 'emoji': '📦'},
        'RepositoryVulnerabilityAlert': {'tag': 'rotating_light,security', 'prio': '5', 'emoji': '🚨'},
        'CheckSuite': {'tag': 'x,no_entry', 'prio': '4', 'emoji': '❌'},
        'Discussion': {'tag': 'speech_balloon', 'prio': '3', 'emoji': '💬'},
        'Commit': {'tag': 'computer,pencil2', 'prio': '2', 'emoji': '💻'}
    }

    cfg = type_configs.get(n_type, {'tag': 'bell', 'prio': '3', 'emoji': '🔔'})
    tags = cfg['tag']
    priority = cfg['prio']

    if reason == 'mention':
        tags += ",loudspeaker"
        priority = '5'
    elif reason == 'review_requested':
        tags += ",eyes"
        priority = '4'

    headers = {
        "Authorization": f"Bearer {NTFY_TOKEN}",
        "Title": f"{cfg['emoji']} {n_type}: {repo}".encode('utf-8'),
        "Tags": tags,
        "Priority": priority,
        "Click": web_url,
        "Icon": GITHUB_ICON_URL,  # Set the official GitHub logo as notification icon
        "Actions": f'[{{"action": "view", "label": "Open on GitHub", "url": "{web_url}"}}]'
    }

    display_reason = reason.replace('_', ' ').upper()
    message = f"**{display_reason}**\n{title}"

    try:
        r = requests.post(NTFY_URL, data=message.encode('utf-8'), headers=headers, timeout=10)
        r.raise_for_status()
        logging.info(f"Notification pushed for {repo} ({n_type})")
    except Exception as e:
        logging.error(f"Ntfy delivery failed: {e}")


def main():
    if not GH_TOKEN or not NTFY_URL:
        logging.error("ENVIRONMENT ERROR: GH_TOKEN or NTFY_URL is missing.")
        return

    conn = init_db()
    cursor = conn.cursor()
    logging.info(f"GitHub Notification Engine active. Polling every {SYNC_INTERVAL}s.")

    while True:
        check_github_notifications(cursor, conn)
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    main()
