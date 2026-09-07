#!/usr/bin/env python3
"""Score transcript quality so articles are only written from usable transcripts.

Usage: python3 scripts/transcript_quality.py [VIDEO_ID ...]   (default: all transcripts)

Reports, per transcript: words per minute of audio, share of Bangla-script tokens,
share of repeated trigrams (looping), and a verdict:
  GOOD   usable as the basis of an article
  WEAK   usable with care (shorter, conservative article; omit unclear details)
  BAD    do not write an article from this transcript
"""
import json, re, sys
from collections import Counter
from pathlib import Path

T = Path(__file__).resolve().parent.parent / 'transcripts'
BN = re.compile(r'[ঀ-৿]')

def score(vid):
    txt = (T / f'{vid}.txt').read_text(encoding='utf-8') if (T / f'{vid}.txt').exists() else ''
    meta = json.loads((T / f'{vid}.json').read_text(encoding='utf-8')) if (T / f'{vid}.json').exists() else {}
    words = [w for line in txt.splitlines() for w in re.sub(r'^\[\d+:\d+\]\s*', '', line).split()]
    minutes = max(1, meta.get('lengthSeconds', 0) / 60)
    wpm = len(words) / minutes
    bn_share = sum(1 for w in words if BN.search(w)) / max(1, len(words))
    tri = Counter(tuple(words[i:i+3]) for i in range(len(words) - 2))
    rep = sum(c - 1 for c in tri.values() if c > 1) / max(1, len(words))
    lang = (meta.get('captions') or {}).get('lang')
    if lang and lang != 'bn': verdict = 'BAD'
    elif wpm >= 70 and bn_share >= 0.75 and rep <= 0.12: verdict = 'GOOD'
    elif wpm >= 45 and bn_share >= 0.6 and rep <= 0.25: verdict = 'WEAK'
    else: verdict = 'BAD'
    return dict(id=vid, verdict=verdict, wpm=round(wpm), bn=round(bn_share, 2), rep=round(rep, 2), lang=lang,
                source=(meta.get('captions') or {}).get('source', 'youtube'), title=(meta.get('title') or '')[:50])

if __name__ == '__main__':
    ids = sys.argv[1:] or sorted(p.stem for p in T.glob('*.txt'))
    for vid in ids:
        s = score(vid)
        print(f"{s['verdict']:<5} {s['id']} wpm={s['wpm']:<4} bn={s['bn']:<5} rep={s['rep']:<5} {s['lang'] or '-':<3} {s['source'][:24]:<24} {s['title']}")
