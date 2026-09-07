#!/usr/bin/env python3
"""Fetch the full transcript and metadata of YouTube videos.

Usage: python3 scripts/transcript.py VIDEO_ID [VIDEO_ID ...]

Writes transcripts/<id>.txt  (timestamped text, one line per ~30 s block)
and    transcripts/<id>.json (title, description, publish date, duration, views, caption language).
Prefers Bangla captions, then English, then whatever exists. Requires:
    python3 -m pip install --user youtube-transcript-api
"""
import json, re, sys, urllib.request, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
from youtube_transcript_api import YouTubeTranscriptApi

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
OUT = Path(__file__).resolve().parent.parent / 'transcripts'

def metadata(vid):
    req = urllib.request.Request(f'https://www.youtube.com/watch?v={vid}', headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9', 'Cookie': 'CONSENT=YES+1'})
    page = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    m = re.search(r'ytInitialPlayerResponse\s*=\s*(\{.*?\});', page, re.S)
    pr = json.loads(m.group(1)) if m else {}
    d = pr.get('videoDetails', {})
    micro = pr.get('microformat', {}).get('playerMicroformatRenderer', {})
    return {'id': vid, 'title': d.get('title'), 'description': d.get('shortDescription'),
            'lengthSeconds': int(d.get('lengthSeconds', 0) or 0), 'viewCount': int(d.get('viewCount', 0) or 0),
            'publishDate': (micro.get('publishDate') or '')[:10], 'channel': d.get('author'), 'keywords': d.get('keywords', [])}

def fetch(vid):
    meta = metadata(vid)
    api = YouTubeTranscriptApi()
    tl = api.list(vid)
    try:
        tr = tl.find_transcript(['bn'])
    except Exception:
        try:
            tr = tl.find_transcript(['en'])
        except Exception:
            tr = next(iter(tl))
    segs = tr.fetch()
    lines, block, block_start = [], [], 0.0
    for s in segs:
        text = s.text.replace('\n', ' ').strip()
        if not text:
            continue
        if s.start - block_start >= 30 and block:
            lines.append(f'[{int(block_start)//60:02d}:{int(block_start)%60:02d}] ' + ' '.join(block))
            block, block_start = [], s.start
        block.append(text)
    if block:
        lines.append(f'[{int(block_start)//60:02d}:{int(block_start)%60:02d}] ' + ' '.join(block))
    meta['captions'] = {'lang': tr.language_code, 'generated': tr.is_generated}
    meta['transcriptWords'] = sum(len(l.split()) for l in lines)
    OUT.mkdir(exist_ok=True)
    (OUT / f'{vid}.txt').write_text('\n'.join(lines), encoding='utf-8')
    (OUT / f'{vid}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    return f'{vid}: {tr.language_code}{"/auto" if tr.is_generated else ""} {meta["transcriptWords"]} words, {meta["lengthSeconds"]//60} min — {(meta["title"] or "")[:60]}'

if __name__ == '__main__':
    for vid in sys.argv[1:]:
        try:
            print(fetch(vid), flush=True)
        except Exception as e:
            print(f'{vid}: ERROR {type(e).__name__}: {str(e)[:200]}', flush=True)
