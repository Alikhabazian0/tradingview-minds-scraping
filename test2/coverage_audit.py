"""Month-level accessibility audit; deliberately does not claim a full archive census."""
import base64
import calendar
import csv
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs

import requests

ROOT = Path(__file__).resolve().parent
API = 'https://www.tradingview.com/api/v1/minds/'
SYMBOL = 'OANDA:XAUUSD'
mutex = threading.Lock()
rate_mutex = threading.Lock()
last_start = 0.0
request_count = 0
requests_log = []
local = threading.local()
known = [(67, datetime.fromisoformat('2022-12-19T13:38:28+00:00').timestamp()),
         (250000, datetime.fromisoformat('2024-03-05T14:07:51+00:00').timestamp()),
         (1000000, datetime.fromisoformat('2025-04-17T04:19:55+00:00').timestamp()),
         (2000000, datetime.fromisoformat('2026-04-15T16:27:31+00:00').timestamp()),
         (3447693, datetime.fromisoformat('2026-10-25T18:44:27+00:00').timestamp())]


def fetch(url, params=None):
    global last_start, request_count
    if not hasattr(local, 'session'):
        local.session = requests.Session()
        local.session.headers['User-Agent'] = 'Dr-TradingView-History-Accessibility-Audit/1.0'
    for attempt in range(3):
        with rate_mutex:
            pause = 1.2 - (time.monotonic() - last_start)
            if pause > 0:
                time.sleep(pause)
            last_start = time.monotonic()
        began = time.monotonic()
        try:
            response = local.session.get(url, params=params, timeout=20)
            with mutex:
                request_count += 1
                requests_log.append({'url': response.url, 'http_status': response.status_code,
                                     'seconds': round(time.monotonic() - began, 3)})
            if response.status_code == 429:
                raise RuntimeError('HTTP 429: stop audit rather than continue requesting')
            if response.status_code >= 500 and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            response.raise_for_status()
            data = response.json()
            if not isinstance(data.get('results'), list):
                raise ValueError('No results list')
            return data
        except requests.Timeout:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def anchor_page(anchor):
    fragment = f'"o":"-id","v":[{anchor}]'
    cursor = base64.b64encode(fragment.encode()).decode().rstrip('=')
    return fetch(API, {'c': cursor, 'f': 'symbol', 'symbol': SYMBOL, 'new_count': 'False'})


def follow(path):
    url = urljoin(API, path)
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.netloc != 'www.tradingview.com' or parts.path != '/api/v1/minds/':
        raise ValueError('Unexpected pagination destination')
    return fetch(url)


def dates(rows):
    return [datetime.fromisoformat(row['created']).timestamp() for row in rows]


def audit_month(year, month):
    label = f'{year:04}-{month:02}'
    day = 24 if label == '2022-12' else 15
    target = datetime(year, month, day, 12, tzinfo=timezone.utc).timestamp()
    result = {'month': label, 'status': 'unresolved', 'search_requests': 0}
    for iteration in range(10):
        with mutex:
            points = sorted(known)
        lower = max((p for p in points if p[1] <= target), default=points[0], key=lambda p: (p[1], p[0]))
        upper = min((p for p in points if p[1] >= target), default=points[-1], key=lambda p: (p[1], p[0]))
        if upper[0] <= lower[0] or upper[1] <= lower[1]:
            raise ValueError(f'Invalid search bracket for {label}')
        proportion = min(.9, max(.1, (target - lower[1]) / (upper[1] - lower[1])))
        anchor = int(lower[0] + (upper[0] - lower[0]) * proportion)
        page = anchor_page(anchor)
        rows = page['results']
        result['search_requests'] += 1
        if not rows:
            raise ValueError(f'Unexpected empty anchor page for {label}')
        ts = dates(rows)
        newest = max(ts)
        with mutex:
            known.append((anchor, newest))
        observed = datetime.fromtimestamp(newest, timezone.utc).strftime('%Y-%m')
        if observed == label:
            break
    else:
        result['status'] = 'search_limit_reached'
        return result
    next_url = page.get('next')
    if not next_url:
        raise ValueError(f'Unexpected missing older link for {label}')
    older = follow(next_url)
    older_rows = older['results']
    if not older_rows:
        raise ValueError(f'Unexpected empty older page for {label}')
    back = follow(older['prev']) if older.get('prev') else None
    ids = [x['uid'] for x in rows]
    older_ids = [x['uid'] for x in older_rows]
    overlap = set(ids).intersection(older_ids)
    chronological = max(dates(older_rows)) <= min(ts)
    roundtrip = bool(back) and [x['uid'] for x in back['results']] == ids
    combined = rows + older_rows
    result.update(status='pass' if not overlap and chronological and roundtrip else 'pagination_mismatch',
                  anchor_id=anchor, posts_checked=len(combined),
                  unique_posts=len({x['uid'] for x in combined}),
                  oldest_utc=min(x['created'] for x in combined),
                  newest_utc=max(x['created'] for x in combined),
                  pages_disjoint=not overlap, chronological=chronological,
                  roundtrip_identical=roundtrip,
                  required_fields_present=all(x.get('uid') and x.get('created') and x.get('text') for x in combined),
                  post_ids=[x['uid'] for x in combined])
    (ROOT / 'month_evidence').mkdir(exist_ok=True)
    (ROOT / 'month_evidence' / f'{label}.json').write_text(
        json.dumps({'summary': result, 'page': page, 'older_page': older,
                    'roundtrip_post_ids': [x['uid'] for x in back['results']] if back else []},
                   ensure_ascii=False), encoding='utf-8')
    return result


def main():
    global request_count, requests_log
    months = [(y, m) for y in range(2022, 2027) for m in range(1, 13)
              if (2022, 12) <= (y, m) <= (2026, 10)]
    results = []
    checkpoint = ROOT / 'monthly_audit.json'
    if checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        results = [row for row in previous['results'] if row['status'] == 'pass']
        request_count = previous['http_requests']
        requests_log = json.loads((ROOT / 'monthly_http_log.json').read_text())
        for row in results:
            known.append((row['anchor_id'], datetime.fromisoformat(row['newest_utc']).timestamp()))
    # The server's next/prev cursor IDs can jump sharply while publication time
    # barely changes. Seed the checked boundary and prefer the most advanced ID
    # among equal timestamps so interpolation cannot repeatedly probe one point.
    boundary = ROOT / 'gap_next_available.json'
    if boundary.exists():
        data = json.loads(boundary.read_text())['payload']
        c = parse_qs(urlsplit(data['prev']).query)['c'][0]
        cursor = json.loads('{' + base64.b64decode(c + '===').decode() + '}')
        known.append((cursor['v'][0], max(dates(data['results']))))
    completed = {row['month'] for row in results}
    pending = [(y, m) for y, m in months if f'{y:04}-{m:02}' not in completed]
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(audit_month, y, m): (y, m) for y, m in pending}
        for future in as_completed(futures):
            y, m = futures[future]
            try:
                result = future.result()
            except Exception as error:
                result = {'month': f'{y:04}-{m:02}', 'status': 'error', 'error': str(error)}
            results.append(result)
            with mutex:
                summary = {'method': 'monthly accessibility and two-page roundtrip audit, not an exhaustive census',
                           'symbol': SYMBOL, 'months_planned': len(months), 'months_finished': len(results),
                           'http_requests': request_count, 'results': sorted(results, key=lambda r: r['month'])}
                (ROOT / 'monthly_audit.json').write_text(json.dumps(summary, indent=2))
                (ROOT / 'monthly_http_log.json').write_text(json.dumps(requests_log, indent=2))
            print(json.dumps({k: v for k, v in result.items() if k != 'post_ids'}), flush=True)
    print('FINISHED', len(results), 'months;', request_count, 'HTTP requests', flush=True)


if __name__ == '__main__':
    main()
