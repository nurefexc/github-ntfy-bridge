# github-ntfy-bridge

[![Docker Hub](https://img.shields.io/docker/pulls/nurefexc/github-ntfy-bridge.svg)](https://hub.docker.com/r/nurefexc/github-ntfy-bridge)
[![Docker Image Size](https://img.shields.io/docker/image-size/nurefexc/github-ntfy-bridge/latest)](https://hub.docker.com/r/nurefexc/github-ntfy-bridge)

A lightweight Python script that polls GitHub for unread notifications and sends them to your [ntfy](https://ntfy.sh) topic in real-time. It uses a local SQLite database to track notifications and ensure you don't get duplicate alerts for the same event.

## Features

- **Duplicate Prevention:** Uses SQLite to track `thread_id` and `updated_at`.
- **Rich Notifications:** Includes emojis, tags, and priorities based on notification types (Pull Request, Issue, Release, Security, etc.).
- **Interactive Actions:** Direct "Open on GitHub" buttons in the notification (where supported by ntfy clients).
- **Customizable:** Configure sync interval, ntfy topic, and more via environment variables.
- **Docker Ready:** Easy deployment using Docker with official image.

## Prerequisites

1. **GitHub Token:** Create a Personal Access Token (PAT) with the `notifications` scope at [GitHub Settings](https://github.com/settings/tokens).
2. **ntfy Topic:** Decide on a topic name (e.g., `my_private_github_alerts`).

## Setup & Installation

### Option 1: Using Docker (Recommended)

The easiest way to run the bridge is using the official Docker image:

1. Pull the image from Docker Hub:
   ```bash
   docker pull nurefexc/github-ntfy-bridge:latest
   ```
2. Run the container:
   ```bash
   docker run -d \
     --name github-ntfy-bridge \
     --restart always \
     -v $(pwd)/data:/app/data \
     -e GH_TOKEN=your_github_pat \
     -e NTFY_URL=https://ntfy.sh/your_topic \
     nurefexc/github-ntfy-bridge:latest
   ```

### Option 2: Build Locally
If you want to build the image yourself:
1. Clone this repository.
2. Build the image:
   ```bash
   docker build -t nurefexc/github-ntfy-bridge:latest .
   ```
3. Run as shown above.

## CI/CD (Automation)

This repository includes a GitHub Action that automatically builds and pushes the Docker image to **Docker Hub** whenever you push to the `master` branch.

To make this work, you need to add the following **Secrets** to your GitHub repository (`Settings > Secrets and variables > Actions`):
- `DOCKERHUB_USERNAME`: Your Docker Hub username.
- `DOCKERHUB_TOKEN`: Your Docker Hub Personal Access Token (PAT).

### Option 3: Manual Installation (Native)

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
- 🔀 **Pull Requests** (Priority 4) - New or updated pull requests.
- 📌 **Issues** (Priority 3) - New issues or comments.
- 📦 **Releases** (Priority 5) - New releases or tags.
- 🚨 **Security** (Priority 5) - Repository vulnerability alerts.
- ❌ **Failures** (Priority 4) - Check suite or run failures.
- 💬 **Discussions** (Priority 3) - New discussions or comments.
- 💻 **Commits** (Priority 2) - New commits.

**Special Handling:**
- 📢 **Mentions** (Priority 5) - Automatically upgraded to Max priority.
- 👀 **Review Requests** (Priority 4) - Tagged for immediate attention.

## License

This project is available under the MIT license. See the [LICENSE](LICENSE) file for details.
