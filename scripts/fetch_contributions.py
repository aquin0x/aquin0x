"""Scrape the public contribution calendar (no token) -> data/contributions.json."""

import json
import os
import re
from collections import OrderedDict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "aquin0x")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    r = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "profile-readme-bot"},
        timeout=30,
    )
    r.raise_for_status()
    return r.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(strip=True) for t in soup.select("tool-tip[for]")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        m = re.match(r"([\d,]+) contributions?", tips.get(td.get("id"), ""))
        days.append({
            "date": td["data-date"],
            "count": int(m.group(1).replace(",", "")) if m else 0,
            "level": int(td.get("data-level", 0)),
        })
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells found - GitHub markup may have changed")
    return days


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    # current streak: today may still be empty, so start from yesterday in that case
    current, tail = 0, days[:-1] if days[-1]["count"] == 0 else days
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return current, longest


def main() -> None:
    days = parse_days(fetch_html(USERNAME))
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    months: "OrderedDict[str, int]" = OrderedDict()
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    data = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total": sum(d["count"] for d in days),
        "active_days": sum(1 for d in days if d["count"]),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "months": months,
        "days": days,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1)
    print(f"{USERNAME}: {data['total']} contributions over {len(days)} days "
          f"(streak {current}, longest {longest}, best {best['date']}={best['count']})")


if __name__ == "__main__":
    main()
