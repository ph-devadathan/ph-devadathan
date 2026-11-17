
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

API_KEY = os.environ["MONKEYTYPE_API_KEY"]
README_FILE = "README.md"

DURATIONS = [15, 30, 60, 120]


def fetch_personal_best(duration):
    params = urllib.parse.urlencode({
        "mode": "time",
        "mode2": duration
    })

    url = f"https://api.monkeytype.com/users/personalBests?{params}"

    request = urllib.request.Request(
        url,
        headers={"Authorization": f"ApeKey {API_KEY}"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "data" not in result:
        raise RuntimeError(f"Unexpected API response: {result}")

    return result["data"]


def main():
    results = []

    for duration in DURATIONS:
        pb = fetch_personal_best(duration)

        if pb and pb.get("wpm") is not None:
            results.append({
                "duration": duration,
                "wpm": float(pb["wpm"]),
                "accuracy": float(pb.get("acc", 0)),
                "consistency": float(pb.get("consistency", 0)),
                "timestamp": pb.get("timestamp", 0)
            })

    if not results:
        raise RuntimeError("No Monkeytype personal bests were returned.")

    best = max(results, key=lambda item: item["wpm"])

    rows = [
        "| Test duration | Personal best | Accuracy | Consistency |",
        "|---|---:|---:|---:|"
    ]

    for item in results:
        rows.append(
            f"| {item['duration']} seconds "
            f"| {item['wpm']:.2f} WPM "
            f"| {item['accuracy']:.2f}% "
            f"| {item['consistency']:.2f}% |"
        )

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    section = "\n".join([
        "### ⌨️ Monkeytype Personal Bests",
        "",
        f"**Highest WPM:** {best['wpm']:.2f} WPM",
        "",
        f"**Best test duration:** {best['duration']} seconds",
        "",
        *rows,
        "",
        f"*Last updated: {updated}*",
        "",
        "[View Monkeytype](https://monkeytype.com/profile/devnn)",
    ])

    with open(README_FILE, "r", encoding="utf-8") as file:
        readme = file.read()

    start = "<!-- MONKEYTYPE-START -->"
    end = "<!-- MONKEYTYPE-END -->"

    if start not in readme or end not in readme:
        raise RuntimeError("Monkeytype README markers are missing.")

    before, remaining = readme.split(start, 1)
    _, after = remaining.split(end, 1)

    new_readme = (
        before + start + "\n" + section + "\n" + end + after
    )

    with open(README_FILE, "w", encoding="utf-8") as file:
        file.write(new_readme)

    print(f"Updated highest WPM: {best['wpm']:.2f}")


if __name__ == "__main__":
    main()
