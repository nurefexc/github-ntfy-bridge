# github-ntfy-bridge

A lightweight Python script that polls GitHub for unread notifications and sends them to your [ntfy](https://ntfy.sh) topic. It uses a local SQLite database to track notifications and ensure you don't get duplicate alerts for the same event.

## Features

- **Duplicate Prevention:** Uses SQLite to track `thread_id` and `updated_at`.
- **Rich Notifications:** Includes emojis, tags, and priorities based on notification types (Pull Request, Issue, Release, Security, etc.).
- **Interactive Actions:** Direct "Open on GitHub" buttons in the notification (where supported by ntfy clients).
- **Customizable:** Configure sync interval, ntfy topic, and more via environment variables.
- **Docker Ready:** Easy deployment using Docker.

## Prerequisites

1. **GitHub Token:** Create a Personal Access Token (PAT) with the `notifications` scope at [GitHub Settings](https://github.com/settings/tokens).
2. **ntfy Topic:** Decide on a topic name (e.g., `my_private_github_alerts`).

## Setup & Installation

### Option 1: Using Docker

1. Clone this repository.
2. Build the Docker image (using `latest` tag):
   ```bash
   docker build -t your-dockerhub-username/github-ntfy-bridge:latest .
   ```
3. Run the container:
   ```bash
   docker run -d \
     --name github-ntfy-bridge \
     -e GH_TOKEN=your_token \
     -e NTFY_URL=https://ntfy.sh/your_topic \
     -v $(pwd)/data:/app/data \
     your-dockerhub-username/github-ntfy-bridge:latest
   ```

## CI/CD (Automation)

This repository includes a GitHub Action that automatically builds and pushes the Docker image to **Docker Hub** whenever you push to the `master` branch.

To make this work, you need to add the following **Secrets** to your GitHub repository (`Settings > Secrets and variables > Actions`):
- `DOCKERHUB_USERNAME`: Your Docker Hub username.
- `DOCKERHUB_TOKEN`: Your Docker Hub Personal Access Token (PAT).

### Option 2: Manual Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (see `.env.sample`).
3. Run the script:
   ```bash
   python main.py
   ```

## Configuration

The following environment variables are supported:

| Variable | Description | Default |
|----------|-------------|---------|
| `GH_TOKEN` | GitHub Personal Access Token (required) | - |
| `NTFY_URL` | Full ntfy topic URL (required) | - |
| `NTFY_TOKEN` | ntfy authentication token (optional) | - |
| `SYNC_INTERVAL` | Polling interval in seconds | `300` |
| `DB_PATH` | Path to the SQLite database file | `/app/data/notifications.db` |
| `TZ` | Timezone for logs (e.g., `Europe/Budapest`) | `Europe/Budapest` |

## Notification Types Supported

The bridge handles various GitHub notification types with custom icons and priorities:
- 🔀 **Pull Requests** (Priority 4)
- 📌 **Issues** (Priority 3)
- 📦 **Releases** (Priority 5)
- 🚨 **Security Vulnerabilities** (Priority 5)
- ❌ **Check Suites / Failures** (Priority 4)
- 💬 **Discussions** (Priority 3)
- 💻 **Commits** (Priority 2)

Special handling:
- **Mentions** are automatically upgraded to Priority 5 (Max) and tagged with a loudspeaker 📢.
- **Review Requests** are set to Priority 4 and tagged with eyes 👀.

## License

MIT
