import sys
import requests
from rich import print

EVENT_MAP = {
    "IssueCommentEvent": lambda e: f"- commented on issue {e['payload']['issue']['number']}",
    "PushEvent": lambda e: f"- pushed to {e['repo']['name']}",
    "IssuesEvent": lambda e: f"- created issue {e['payload']['issue']['number']}",
    "WatchEvent": lambda e: f"- starred {e['repo']['name']}",
    "PullRequestEvent": lambda e: f"- created pull request {e['payload']['pull_request']['number']}",
    "PullRequestReviewEvent": lambda e: f"- reviewed pull request {e['payload']['pull_request']['number']}",
    "PullRequestReviewCommentEvent": lambda e: f"- commented on pull request {e['payload']['pull_request']['number']}",
    "CreateEvent": lambda e: f"- created {e['payload']['ref_type']} {e['payload']['ref']}",
}

def show_events(user):
    res = requests.get(f"https://api.github.com/users/{user}/events", timeout=10)
    if res.status_code != 200:
        print(f"Error fetching events for {user}: {res.status_code}")
        return
    print(f"Latest events for [bold green]{user}[/bold green]:")
    for e in res.json():
        msg = EVENT_MAP.get(e["type"], lambda ev: f"- {ev['type']}")(e)
        print(msg)

def main():
    if len(sys.argv) < 2:
        print("Please provide a GitHub username as a command line argument.")
        return
    show_events(sys.argv[1])

if __name__ == "__main__":
    main()