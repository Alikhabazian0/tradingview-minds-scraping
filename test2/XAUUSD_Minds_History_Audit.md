# XAUUSD Minds historical accessibility audit

Test date: 25 October 2026. Queried feed: `OANDA:XAUUSD`.

**This is a month-level accessibility and pagination audit, not proof of complete archive coverage.**

- Months tested: 47 (December 2022 through October 2026).
- Passing monthly checks: 47.
- Distinct posts in the monthly samples: 1880.
- HTTP requests: 194; status counts: {200: 194}.
- Disjoint page pairs: 47/47.
- Chronological page pairs: 47/47.
- Identical return-navigation results: 47/47.
- Samples containing post ID, publication timestamp and nonempty text: 47/47.

## Method

Located a page of 20 public posts in each calendar month using cursor positions. Followed the server-returned link to the adjacent older page, checked its 20 posts for duplicate IDs and date order, then followed its return link and compared IDs against the original page. The return request does not add 20 new posts. Requests were limited to one start every 1.2 seconds, with at most four active requests. No login, cookie, proxy rotation or paid credentials were supplied.

The earlier boundary test retrieved the oldest available batch on 19 December 2022 (earliest timestamp 13:38:28.763168 UTC). Its older-page link returned HTTP 200 with zero posts; forward pagination retrieved posts from 20 December 2022. Those boundary responses are included separately in this bundle.

## Interpretation and limits

Posts were reachable in every tested month. The tested links worked without duplicates or skipped items detectable by the return-navigation check. This supports implementing a historical collector across the available date range.

The audit intentionally jumped between monthly samples. It did not enumerate every intervening page or check every day, and it cannot rule out gaps between the samples. The endpoint exposes no authoritative archive total in the responses tested. Deleted, hidden, moderated or otherwise inaccessible posts cannot be accounted for by this method. Even a full crawl would establish the posts exposed by the endpoint, not all posts ever published.

The XAUUSD feed groups multiple gold providers/symbols, including TVC:GOLD. It is not evidence of exhaustive literal XAUUSD/#XAUUSD text-mention coverage.

Large jumps in internal cursor IDs were observed without corresponding gaps in publication dates. Following adjacent server-returned links across one such boundary retrieved later posts on the same day, 30 May 2026, and navigating back returned the original IDs. June, July and August 2026 were then checked successfully. Production collection should follow returned cursors rather than interpret ID gaps as missing posts or interpolate dates from IDs.

The unmodified mnwato/tradingview-scraper bulk method previously requested 50 posts and received HTTP 400 while reporting success with zero posts. This audit used 20-post pages and explicit HTTP validation. The original library is not verified as a reliable full-history collector.

A stronger follow-up would enumerate the feed continuously between fixed boundaries and repeat the traversal to compare IDs and counts. That has not been completed here.

## Monthly results

Dates below are publication dates in UTC; they identify samples, not month boundaries.

| Month | Check | Unique sample posts | Oldest sampled date | Newest sampled date |
| --- | --- | ---: | --- | --- |
| 2022-12 | pass | 40 | 2022-12-21 | 2022-12-23 |
| 2023-01 | pass | 40 | 2023-01-12 | 2023-01-13 |
| 2023-02 | pass | 40 | 2023-02-09 | 2023-02-11 |
| 2023-03 | pass | 40 | 2023-03-06 | 2023-03-07 |
| 2023-04 | pass | 40 | 2023-04-17 | 2023-04-18 |
| 2023-05 | pass | 40 | 2023-05-17 | 2023-05-17 |
| 2023-06 | pass | 40 | 2023-06-12 | 2023-06-13 |
| 2023-07 | pass | 40 | 2023-07-14 | 2023-07-14 |
| 2023-08 | pass | 40 | 2023-08-16 | 2023-08-17 |
| 2023-09 | pass | 40 | 2023-09-26 | 2023-09-26 |
| 2023-10 | pass | 40 | 2023-10-27 | 2023-10-28 |
| 2023-11 | pass | 40 | 2023-11-28 | 2023-11-28 |
| 2023-12 | pass | 40 | 2023-12-20 | 2023-12-20 |
| 2024-01 | pass | 40 | 2024-01-22 | 2024-01-22 |
| 2024-02 | pass | 40 | 2024-02-19 | 2024-02-20 |
| 2024-03 | pass | 40 | 2024-03-14 | 2024-03-14 |
| 2024-04 | pass | 40 | 2024-04-30 | 2024-04-30 |
| 2024-05 | pass | 40 | 2024-05-16 | 2024-05-16 |
| 2024-06 | pass | 40 | 2024-06-15 | 2024-06-16 |
| 2024-07 | pass | 40 | 2024-07-16 | 2024-07-16 |
| 2024-08 | pass | 40 | 2024-08-28 | 2024-08-28 |
| 2024-09 | pass | 40 | 2024-09-30 | 2024-09-30 |
| 2024-10 | pass | 40 | 2024-10-15 | 2024-10-15 |
| 2024-11 | pass | 40 | 2024-11-15 | 2024-11-15 |
| 2024-12 | pass | 40 | 2024-12-24 | 2024-12-24 |
| 2025-01 | pass | 40 | 2025-01-22 | 2025-01-22 |
| 2025-02 | pass | 40 | 2025-02-17 | 2025-02-17 |
| 2025-03 | pass | 40 | 2025-03-14 | 2025-03-14 |
| 2025-04 | pass | 40 | 2025-04-09 | 2025-04-09 |
| 2025-05 | pass | 40 | 2025-05-26 | 2025-05-26 |
| 2025-06 | pass | 40 | 2025-06-27 | 2025-06-27 |
| 2025-07 | pass | 40 | 2025-07-16 | 2025-07-16 |
| 2025-08 | pass | 40 | 2025-08-15 | 2025-08-15 |
| 2025-09 | pass | 40 | 2025-09-19 | 2025-09-19 |
| 2025-10 | pass | 40 | 2025-10-14 | 2025-10-14 |
| 2025-11 | pass | 40 | 2025-11-12 | 2025-11-12 |
| 2025-12 | pass | 40 | 2025-12-12 | 2025-12-12 |
| 2026-01 | pass | 40 | 2026-01-21 | 2026-01-21 |
| 2026-02 | pass | 40 | 2026-02-12 | 2026-02-12 |
| 2026-03 | pass | 40 | 2026-03-12 | 2026-03-12 |
| 2026-04 | pass | 40 | 2026-04-07 | 2026-04-07 |
| 2026-05 | pass | 40 | 2026-05-29 | 2026-05-30 |
| 2026-06 | pass | 40 | 2026-06-11 | 2026-06-11 |
| 2026-07 | pass | 40 | 2026-07-09 | 2026-07-09 |
| 2026-08 | pass | 40 | 2026-08-11 | 2026-08-11 |
| 2026-09 | pass | 40 | 2026-09-14 | 2026-09-14 |
| 2026-10 | pass | 40 | 2026-10-14 | 2026-10-14 |
