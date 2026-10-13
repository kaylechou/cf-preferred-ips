# cf-preferred-ips

Aggregated Cloudflare preferred IPs, auto-updated daily by GitHub Action.

## Files

- `custom-ips.txt` — curated list (tested for China Telecom), takes priority in merge.
- `aggregated-ips.txt` — merged output: custom + upstream best-cf-ips (collected + top100), deduped by IP:port. Use this in the preferred-IP tool's API URL field.
- `aggregate.py` — merge script run by the Action.

## API URL for the tool

```
https://raw.githubusercontent.com/kaylechou/cf-preferred-ips/main/aggregated-ips.txt
```

## Upstream sources

- https://github.com/LancelotRar/best-cf-ips (collected + scanned top100)
