# XAUUSD TradingView Minds feasibility test

Test date: 25 October 2026. Source: https://github.com/mnwato/tradingview-scraper

Inspected commit: `68ea546a7a4b78b49da2b7417824b8ee44d237d5`.
Repository setup.py declares version 0.4.22. Imported the checked-out Minds
module directly, using Python 3.12, requests 2.34.2 and pandas 3.1.0.
The full package dependency set was not installed; the repository pins requests
2.32.4. This was a targeted Minds module and endpoint test.

## Actual results

| Test | Result |
| --- | --- |
| Unmodified `Minds().get_minds('OANDA:XAUUSD', limit=5)` | Success, 5 posts, nonempty text |
| Unmodified `get_all_minds(..., max_results=60)` | Returned success with 0 posts |
| Underlying first bulk HTTP request (`limit=50`) | HTTP 400, code `bad_pagination_request` |
| Requests using limit=10 and limit=20 | Both HTTP 200 with requested counts |
| Following server-returned next URL | Success, distinct older posts |
| Included workaround script, 3 pages of 20 | HTTP 200 for every page; 60 unique posts |

The final sample runs from 2026-10-24 08:00:51.849712 UTC to
2026-10-25 18:24:51.183336 UTC. All 60 timestamps are in descending order,
all texts are nonempty, and CSV has 60 data rows. No login, cookie, or paid
API credentials were supplied. No scheduled collection was configured.

## Download again

```bash
python -m pip install requests
python test_xauusd_minds.py --symbol OANDA:XAUUSD --max-pages 3 --output sample
```

The included script uses the same public web endpoint as the repository:
`https://www.tradingview.com/api/v1/minds/`. It uses 20-post pages and follows
the returned next URLs rather than the repository's failing 50-post default.
It checks HTTP failures, validates required fields, deduplicates by uid,
and preserves the original timestamp offset and complete raw page responses.
The observed failure does not prove 20 is the endpoint's maximum page size.

Files:

- `sample/xauusd_minds.csv`: flattened sample for inspection.
- `sample/xauusd_minds_raw.json`: complete raw pages, request metadata and unique posts.
- `test_xauusd_minds.py`: bounded repeatable download test.
- `verification.json`: checks of sample count, dates and fields.
- `single_result.json`, `pagination_result.json`, `http_events.json`: library test evidence.

## Fit for Dr-TradingView

- Available fields include post ID, text, URL, publication time, username,
  profile URL, symbol mentions, likes, comment count, modified and hidden fields.
- This test did not expose follower counts, a separate boosts field, full
  comments, or historical engagement snapshots. Market price bars and computed
  indicators require separate data collection.
- OANDA:XAUUSD returned posts tagged with multiple gold providers, including
  FOREXCOM:XAUUSD, FX:XAUUSD and TVC:GOLD. Preserve these tags; do not assume
  the feed is exclusive to one broker. Symbol-feed membership does not establish
  coverage of every literal XAUUSD or #XAUUSD mention across TradingView.
- Bare XAUUSD is rejected by the library's validation; include a provider prefix.
- The library strips the timezone and subsecond precision from its parsed
  `created` value. Preserve the original raw timestamps for feature alignment.
- The library's bulk method silently breaks on non-200 responses and returns
  success, potentially with zero or incomplete data. Reproduced both live and
  with a controlled HTTP 400 response.
- The repository has no date-range arguments or persisted resume checkpoint in
  its Minds methods. Five-minute polling and historical date-to-date collection
  need a wrapper with saved cursors, overlap, ID-based upserts, retries/backoff,
  explicit incomplete-run status, and UTC timestamps.
- This is a feasibility sample, not proof of complete historical coverage,
  stable access, a supported official public API, or five-minute reliability.
  The script intentionally lacks production scheduling and durable resume.
