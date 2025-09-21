import sys
import requests
from rich import print
from collections import defaultdict
from datetime import datetime, timezone


# Emojis for event types like idk commit, issue, pr, review, star, fork, release etc.
EVENT_ICONS = {
    "PushEvent": "🔧",
    "IssueCommentEvent": "💬",
    "IssuesEvent": "🐛",
    "PullRequestEvent": "🚀",
    "PullRequestReviewEvent": "👀",
    "PullRequestReviewCommentEvent": "💭",
    "WatchEvent": "⭐",
    "CreateEvent": "📦",
    "ForkEvent": "🍴",
    "ReleaseEvent": "🏷️",
    "Other": "❓",
}


def relative_time(timestr: str) -> str:
    """Convert GitHub timestamp to 'Xh ago' style."""
    dt = datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    diff = datetime.now(timezone.utc) - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)}h ago"
    else:
        return f"{int(seconds // 86400)}d ago"


# Group events by repo, collecting type + extra info like commit count, issue/pr number, etc.
def summarize_events(events):
    """Group events by repo, collecting type + extra info."""
    summary = defaultdict(list)

    for e in events:
        etype = e["type"]
        repo = e["repo"]["name"]
        time = relative_time(e["created_at"])

        if etype == "PushEvent":
            commit_count = len(e["payload"].get("commits", []))
            summary[repo].append((etype, f"pushed {commit_count} commit(s)", time))

        elif etype == "IssueCommentEvent":
            issue = e["payload"]["issue"]["number"]
            summary[repo].append((etype, f"commented on issue #{issue}", time))

        elif etype == "IssuesEvent":
            issue = e["payload"]["issue"]["number"]
            summary[repo].append((etype, f"opened issue #{issue}", time))

        elif etype == "PullRequestEvent":
            pr = e["payload"]["pull_request"]["number"]
            summary[repo].append((etype, f"opened pull request #{pr}", time))

        elif etype == "PullRequestReviewEvent":
            pr = e["payload"]["pull_request"]["number"]
            summary[repo].append((etype, f"reviewed pull request #{pr}", time))

        elif etype == "PullRequestReviewCommentEvent":
            pr = e["payload"]["pull_request"]["number"]
            summary[repo].append((etype, f"commented on pull request #{pr}", time))

        elif etype == "WatchEvent":
            summary[repo].append((etype, "starred the repo", time))

        elif etype == "CreateEvent":
            ref_type = e["payload"]["ref_type"]
            ref = e["payload"]["ref"]
            summary[repo].append((etype, f"created {ref_type} {ref}", time))

        elif etype == "ForkEvent":
            summary[repo].append((etype, "forked the repo", time))

        elif etype == "ReleaseEvent":
            release = e["payload"]["release"]["tag_name"]
            summary[repo].append((etype, f"published release {release}", time))

        else:
            summary[repo].append(("Other", f"{etype}", time))

    return summary

# Format the summary for pretty terminal output
def format_summary(summary):
    """Pretty print grouped events with emojis + times."""
    lines = []
    for repo, events in summary.items():
        lines.append(f"\n[bold blue]{repo}[/bold blue] ({len(events)} event(s))")
        for etype, desc, time in events:
            icon = EVENT_ICONS.get(etype, "❓")
            lines.append(f"  {icon} {desc} [{time}]")
    return lines


def show_events(user):
    res = requests.get(f"https://api.github.com/users/{user}/events", timeout=10)
    if res.status_code != 200:
        print(f"Error fetching events for {user}: {res.status_code}")
        return
    events = res.json()
    if not events:
        print(f"No latest events for [bold yellow]{user}[/bold yellow].")
        return

    print(f"Latest events for [bold green]{user}[/bold green]:")
    summary = summarize_events(events)
    lines = format_summary(summary)
    for line in lines:
        print(line)

# Entry point
def main():
    if len(sys.argv) < 2:
        print("Please provide a GitHub username as a command line argument.")
        return
    show_events(sys.argv[1])


if __name__ == "__main__":
    main()