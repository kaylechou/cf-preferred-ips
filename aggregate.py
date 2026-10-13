#!/usr/bin/env python3
"""Merge custom preferred IPs with upstream best-cf-ips lists.

Sources:
  - custom-ips.txt (local, curated; takes priority)
  - https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-collected.txt
  - https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-scanned-top100.txt
Output: aggregated-ips.txt (one IP:port#name per line, deduped by IP:port).
"""
import datetime
import urllib.request

UPSTREAM = [
    "https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-collected.txt",
    "https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-scanned-top100.txt",
]

def parse_lines(text):
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out

def key_of(line):
    # dedupe key: the IP:port part before '#'
    return line.split("#", 1)[0].strip()

def main():
    seen = set()
    merged = []
    with open("custom-ips.txt", encoding="utf-8") as f:
        custom = parse_lines(f.read())
    for line in custom:
        k = key_of(line)
        if k not in seen:
            seen.add(k)
            merged.append(line)
    n_custom = len(merged)
    for url in UPSTREAM:
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                text = r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"WARN: fetch failed {url}: {e}")
            continue
        n_new = 0
        for line in parse_lines(text):
            k = key_of(line)
            if k not in seen:
                seen.add(k)
                merged.append(line)
                n_new += 1
        print(f"{url}: +{n_new} new")
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = [f"# Aggregated Cloudflare preferred IPs updated {now}",
              f"# Sources: custom-ips.txt ({n_custom}) + upstream best-cf-ips (collected + top100)"]
    with open("aggregated-ips.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(header + merged) + "\n")
    print(f"custom={n_custom} total={len(merged)}")

if __name__ == "__main__":
    main()
