#!/usr/bin/env python3
"""Prepare everything for a new episode article.

Usage: python3 scripts/new_episode.py VIDEO_ID [--slug my-slug]

1. Downloads the thumbnail into thumbs/.
2. Fetches the full transcript (Bangla auto-captions; falls back to local Whisper
   via scripts/transcribe.py when captions are missing or in the wrong language).
3. Scaffolds articles/<slug>.md with the front matter pre-filled from the video.
Then write the article per docs/article-guide.md, add the episode to js/main.js,
run scripts/build_articles.py and commit.
"""
import json, os, re, subprocess, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
vid = sys.argv[1]
slug = sys.argv[sys.argv.index('--slug') + 1] if '--slug' in sys.argv else None

# 1. thumbnail
t = ROOT / 'thumbs' / f'{vid}.jpg'
if not t.exists():
    for kind in ('maxresdefault', 'sddefault', 'hqdefault'):
        data = urllib.request.urlopen(f'https://i.ytimg.com/vi/{vid}/{kind}.jpg').read()
        if len(data) > 5000:
            t.write_bytes(data); break
    subprocess.run(['sips', '-Z', '720', '-s', 'format', 'jpeg', '-s', 'formatOptions', '68', str(t), '--out', str(t)], capture_output=True)
    print(f'thumbnail → {t}')

# 2. transcript
from transcript import fetch
meta_path = ROOT / 'transcripts' / f'{vid}.json'
try:
    print(fetch(vid))
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    ok = meta['captions']['lang'] == 'bn' and meta['transcriptWords'] > meta['lengthSeconds'] / 60 * 60
except Exception as e:
    print('caption fetch failed:', e); ok = False
if not ok:
    print('No usable Bangla captions — transcribing locally with Whisper (this takes a few minutes per hour of audio)…')
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'transcribe.py'), vid], check=True)
    subprocess.run([sys.executable, str(ROOT / 'scripts' / 'transcript_quality.py'), vid])
meta = json.loads(meta_path.read_text(encoding='utf-8'))

# 3. scaffold
title = meta.get('title') or vid
m = re.search(r'(?:DDS|Deep Down Show|Ep(?:isode)?)[\s\-:]*(\d+)', title, re.I)
ep = int(m.group(1)) if m else 0
if not slug:
    slug = re.sub(r'[^a-z0-9]+', '-', title.split('|')[0].lower()).strip('-')[:60]
h, rem = divmod(meta.get('lengthSeconds', 0), 3600); mnt, sec = divmod(rem, 60)
dur = f'{h}:{mnt:02d}:{sec:02d}' if h else f'{mnt}:{sec:02d}'
front = {"video_id": vid, "video_title": title, "episode": ep, "slug": slug, "title": "", "title_bn": "", "meta_description": "", "lede": "",
         "guest": "", "guest_role": "", "category": "business", "published": meta.get('publishDate', ''), "duration": dur,
         "keywords": [], "takeaways": [], "faq": [], "related": [], "clips": []}
out = ROOT / 'articles' / f'{slug}.md'
if out.exists():
    print(f'{out} already exists — not overwriting')
else:
    out.write_text('---\n' + json.dumps(front, ensure_ascii=False, indent=2) + '\n---\n\n<!-- Write the article here after reading transcripts/' + vid + '.txt in full. See docs/article-guide.md -->\n', encoding='utf-8')
    print(f'scaffold → {out}')
print(f'\nNext: read transcripts/{vid}.txt completely, write the article, add the episode to EPISODES in js/main.js, then run python3 scripts/build_articles.py')
