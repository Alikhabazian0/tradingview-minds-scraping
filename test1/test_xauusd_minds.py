"""Bounded public XAUUSD Minds download; not a production history collector.

Install: python -m pip install requests
Run: python test_xauusd_minds.py --output sample
Uses the endpoint found in mnwato/tradingview-scraper. Follows returned next
URLs with 20-post pages rather than the library's failing 50-post default.
"""
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

BASE = 'https://www.tradingview.com'
ENDPOINT = BASE + '/api/v1/minds/'


def download(symbol='OANDA:XAUUSD', max_pages=3, page_size=20, delay=1.2):
    if not 1 <= page_size <= 20 or max_pages < 1 or delay < 0:
        raise ValueError('Use page_size 1..20, max_pages >= 1, delay >= 0')
    if ':' not in symbol:
        raise ValueError('Include a provider prefix, e.g. OANDA:XAUUSD')
    url = ENDPOINT
    params = {'symbol': symbol, 'limit': page_size, 'sort': 'recent'}
    pages, posts, seen, visited = [], [], set(), set()
    with requests.Session() as session:
        session.headers['User-Agent'] = 'Dr-TradingView-Minds-Feasibility-Test/1.0'
        for page in range(max_pages):
            response = session.get(url, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
            items = payload.get('results')
            if not isinstance(items, list):
                raise ValueError('Unexpected response: results is not a list')
            pages.append({'url': response.url, 'http_status': response.status_code,
                          'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                          'response': payload})
            for item in items:
                uid = item.get('uid')
                if not uid or not item.get('text') or not item.get('created'):
                    raise ValueError('Missing required post ID, text, or timestamp')
                if uid not in seen:
                    seen.add(uid)
                    posts.append(item)
            print(f'Page {page + 1}: {len(items)} posts; {len(posts)} unique total', flush=True)
            next_url = payload.get('next')
            if not items or not next_url or page + 1 == max_pages:
                break
            url = urljoin(BASE, next_url)
            target = urlsplit(url)
            if (target.scheme != 'https' or target.netloc != 'www.tradingview.com'
                    or target.path != '/api/v1/minds/'):
                raise ValueError('Unexpected pagination destination')
            if url in visited:
                raise ValueError('Repeated pagination URL')
            visited.add(url)
            params = None
            time.sleep(delay)
    return {'symbol': symbol, 'pages': pages, 'posts': posts}


def save(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'xauusd_minds_raw.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    columns = ['uid', 'created', 'username', 'profile_url', 'text', 'url',
               'symbols', 'total_likes', 'total_comments', 'modified', 'hidden']
    with (output / 'xauusd_minds.csv').open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for item in result['posts']:
            author = item.get('author', {})
            row = {key: item.get(key) for key in columns}
            row.update(username=author.get('username'),
                       profile_url=urljoin(BASE, author.get('uri', '')),
                       symbols=json.dumps(item.get('symbols', {}), ensure_ascii=False))
            writer.writerow(row)
    print(f'Saved {len(result["posts"])} unique posts to {output.resolve()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--symbol', default='OANDA:XAUUSD')
    parser.add_argument('--max-pages', type=int, default=3)
    parser.add_argument('--page-size', type=int, default=20)
    parser.add_argument('--delay', type=float, default=1.2)
    parser.add_argument('--output', default='sample')
    args = parser.parse_args()
    save(download(args.symbol, args.max_pages, args.page_size, args.delay), args.output)
