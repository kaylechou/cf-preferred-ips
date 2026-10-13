#!/usr/bin/env python3
"""Merge custom preferred IPs with upstream best-cf-ips lists.

Sources:
  - https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-collected.txt
  - https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-scanned-top100.txt
  - custom-ips.txt (local, curated; oldest, goes last)
Output: aggregated-ips.txt (one IP:port#name per line, deduped by IP:port).
Order: newest first. Upstream sources are ordered by the timestamp in
their own header line (e.g. "# 74 best ips collected at 2026-10-13 20:13"),
newest first; custom-ips.txt has no timestamp and is treated as oldest,
so it always goes last. Within each source the original order is kept.
On duplicate IP:port the newer source's line wins (first occurrence wins).
"""
import re
import urllib.request

UPSTREAM = [
    "https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-collected.txt",
    "https://raw.githubusercontent.com/LancelotRar/best-cf-ips/main/best-cf-ip-scanned-top100.txt",
]

TS_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")

def parse_lines(text):
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line)
    return out

def header_timestamp(text):
    # 上游文件头含更新时间，如 "# 74 best ips collected at 2026-10-13 20:13"。
    # 找不到则当作最旧（空串在排序中垫底）。
    for raw in text.splitlines()[:5]:
        m = TS_RE.search(raw)
        if m:
            return m.group(0)
    return ""

def key_of(line):
    # dedupe key: the IP:port part before '#'
    return line.split("#", 1)[0].strip()

def main():
    seen = set()
    merged = []
    with open("custom-ips.txt", encoding="utf-8") as f:
        custom = parse_lines(f.read())
    # 先拉上游，按各自头里的时间戳新到旧排；custom 无时间戳、当最旧放最后。
    fetched = []
    for url in UPSTREAM:
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                text = r.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"WARN: fetch failed {url}: {e}")
            continue
        fetched.append((header_timestamp(text), url, parse_lines(text)))
    fetched.sort(key=lambda t: t[0], reverse=True)
    for ts, url, lines in fetched:
        n_new = 0
        for line in lines:
            k = key_of(line)
            if k not in seen:
                seen.add(k)
                merged.append(line)
                n_new += 1
        print(f"{url} (updated {ts or 'unknown'}): +{n_new} new")
    n_upstream = len(merged)
    n_custom = 0
    for line in custom:
        k = key_of(line)
        if k not in seen:
            seen.add(k)
            merged.append(line)
            n_custom += 1
    # 不写 # 注释头：订阅接口解析器不跳过 # 行，会把注释当成一条 IP，
    # 空 IP + 默认端口拼成 ":443# ..." 这种脏数据。更新时间看 git 提交记录。
    with open("aggregated-ips.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(merged) + "\n")
    print(f"upstream={n_upstream} custom={n_custom} total={len(merged)}")

if __name__ == "__main__":
    main()
