import sys
import requests
from rich import print
from collections import defaultdict

def summarize_events(events):
    summary = defaultdict(list)

    for e in events:
        etype = e["type"]

        if etype == "PushEvent":
            repo = e["repo"]["name"]
            commit_count = len(e["payload"].get("commits", []))
            summary[etype].append((repo, commit_count))

        elif etype == "IssueCommentEvent":
            issue = e["payload"]["issue"]["number"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, issue))

        elif etype == "IssuesEvent":
            issue = e["payload"]["issue"]["number"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, issue))

        elif etype == "PullRequestEvent":
            pr = e["payload"]["pull_request"]["number"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, pr))

        elif etype == "PullRequestReviewEvent":
            pr = e["payload"]["pull_request"]["number"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, pr))

        elif etype == "PullRequestReviewCommentEvent":
            pr = e["payload"]["pull_request"]["number"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, pr))

        elif etype == "WatchEvent":
            repo = e["repo"]["name"]
            summary[etype].append(repo)

        elif etype == "CreateEvent":
            ref_type = e["payload"]["ref_type"]
            ref = e["payload"]["ref"]
            repo = e["repo"]["name"]
            summary[etype].append((repo, ref_type, ref))

        else:
            summary["Other"].append(etype)

    return summary


def format_summary(summary):
    lines = []
    for etype, items in summary.items():
        if etype == "PushEvent":
            repo_commits = defaultdict(int)
            for repo, count in items:
                repo_commits[repo] += count
            for repo, total in repo_commits.items():
                lines.append(f"- pushed {total} commit(s) to [bold blue]{repo}[/bold blue]")

        elif etype == "IssueCommentEvent":
            lines.append(f"- commented on {len(items)} issue(s)")

        elif etype == "IssuesEvent":
            lines.append(f"- opened {len(items)} issue(s)")

        elif etype == "PullRequestEvent":
            lines.append(f"- opened {len(items)} pull request(s)")

        elif etype == "PullRequestReviewEvent":
            lines.append(f"- reviewed {len(items)} pull request(s)")

        elif etype == "PullRequestReviewCommentEvent":
            lines.append(f"- commented on {len(items)} pull request(s)")

        elif etype == "WatchEvent":
            repos = ", ".join(set(items))
            lines.append(f"- starred {len(items)} repo(s): {repos}")

        elif etype == "CreateEvent":
            for repo, ref_type, ref in items:
                lines.append(f"- created {ref_type} {ref} in [bold blue]{repo}[/bold blue]")

        elif etype == "Other":
            lines.append(f"- {len(items)} other event(s)")

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


def main():
    if len(sys.argv) < 2:
        print("Please provide a GitHub username as a command line argument.")
        return
    show_events(sys.argv[1])


if __name__ == "__main__":
    main()