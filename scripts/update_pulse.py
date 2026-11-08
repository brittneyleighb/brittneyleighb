#!/usr/bin/env python3
"""Create a self-hosted, 90-day GitHub contribution signal (no dependencies)."""
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
import json
import math
import os
import sys
import urllib.error
import urllib.request

DAYS = 90
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "contribution-pulse.svg"
QUERY = """query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}"""


def get_days(username: str, token: str, today: date) -> list[tuple[date, int]]:
    start = today - timedelta(days=DAYS - 1)
    variables = {
        "login": username,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": f"{today.isoformat()}T23:59:59Z",
    }
    body = json.dumps({"query": QUERY, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "User-Agent": "brittneyleighb-profile-pulse",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        result = json.load(response)
    if result.get("errors"):
        raise RuntimeError("GitHub GraphQL error: " + str(result["errors"]))
    try:
        weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except (KeyError, TypeError) as error:
        raise RuntimeError("Unexpected GitHub contributionCalendar response") from error
    reported = {}
    for week in weeks:
        for day in week["contributionDays"]:
            d = date.fromisoformat(day["date"])
            count = int(day["contributionCount"])
            if count < 0:
                raise ValueError("Negative GitHub contribution count")
            reported[d] = count
    return [(d, reported.get(d, 0)) for d in (start + timedelta(days=i) for i in range(DAYS))]


def render(days: list[tuple[date, int]], updated: date) -> str:
    if len(days) != DAYS or any(days[i][0] >= days[i + 1][0] for i in range(DAYS - 1)):
        raise ValueError("Expected 90 increasing daily observations")
    counts = [count for _, count in days]
    if any(count < 0 for count in counts):
        raise ValueError("Counts must be nonnegative")
    total = sum(counts)
    maximum = max(counts) or 1
    bars = []
    for i, count in enumerate(counts):
        x = 65 + i * 12
        height = int(105 * math.sqrt(count / maximum)) if count else 0
        y = 185 - height
        if count:
            opacity = min(.95, .35 + count / maximum * .65)
            bars.append(f'<line x1="{x}" y1="185" x2="{x}" y2="{y}" stroke="#7eeba8" stroke-width="3.5" stroke-linecap="round" opacity="{opacity:.2f}"/>')
            bars.append(f'<circle cx="{x}" cy="{y}" r="2.3" fill="#d6ffcb"/>')
        else:
            bars.append(f'<line x1="{x}" y1="185" x2="{x}" y2="183" stroke="#315b48" stroke-width="2"/>')
    def label(d):
        return escape(d.strftime("%b %d").upper())
    subtitle = f"{total:,} PUBLIC CONTRIBUTIONS  /  LAST {DAYS} DAYS"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="258" viewBox="0 0 1200 258" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution signal, last 90 days</title>
<desc id="desc">{total} public GitHub contributions between {days[0][0].isoformat()} and {days[-1][0].isoformat()}. Each vertical bar represents one day; height scales with the square root of its count.</desc>
<defs><linearGradient id="background" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#080f10"/><stop offset="1" stop-color="#10251b"/></linearGradient></defs>
<rect width="1200" height="258" rx="8" fill="url(#background)"/>
<rect x="1" y="1" width="1198" height="256" rx="8" fill="none" stroke="#526c60" opacity=".65"/>
<g font-family="Consolas,Menlo,Monaco,monospace">
  <text x="63" y="43" fill="#d8f4df" font-size="20" letter-spacing="2">CONTRIBUTION SIGNAL</text>
  <text x="1135" y="41" fill="#9cc3a9" font-size="12" text-anchor="end">GITHUB / PUBLIC ACTIVITY</text>
  <text x="64" y="66" fill="#8fbba2" font-size="12" letter-spacing="1.4">{escape(subtitle)}</text>
  <path d="M65 185H1135" stroke="#527c62" stroke-width="1" opacity=".65"/>
  {''.join(bars)}
  <text x="65" y="217" fill="#8fbba2" font-size="13">{label(days[0][0])}</text>
  <text x="599" y="217" fill="#8fbba2" font-size="13" text-anchor="middle">{label(days[DAYS // 2][0])}</text>
  <text x="1135" y="217" fill="#8fbba2" font-size="13" text-anchor="end">{label(days[-1][0])}</text>
  <text x="65" y="243" fill="#759c89" font-size="11">COMMITS · ISSUES · PULL REQUESTS · REVIEWS · OTHER CONTRIBUTIONS</text>
  <text x="1135" y="243" fill="#759c89" font-size="11" text-anchor="end">UPDATED {updated.isoformat()} UTC</text>
</g>
</svg>
'''


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required; refusing to fabricate activity data")
    username = os.environ.get("GITHUB_USERNAME", "brittneyleighb")
    today = datetime.now(timezone.utc).date()
    try:
        days = get_days(username, token, today)
    except (urllib.error.URLError, RuntimeError, ValueError) as error:
        sys.exit(f"Could not update contribution signal: {error}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(days, today), encoding="utf-8")
    print(f"Updated {OUTPUT} from GitHub contributionCalendar")


if __name__ == "__main__":
    main()
