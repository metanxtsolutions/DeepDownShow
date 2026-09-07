#!/usr/bin/env python3
"""Transcribe YouTube videos locally with Whisper (Apple Silicon, MLX).

Usage: ~/.venvs/dds-stt/bin/python scripts/transcribe.py VIDEO_ID [VIDEO_ID ...]
Env:   DDS_AUDIO_DIR (where audio is cached, default /tmp/dds-audio)
       DDS_WHISPER_MODEL (default mlx-community/whisper-large-v3-turbo)

Downloads audio with yt-dlp, transcribes in Bangla, writes transcripts/<id>.txt
(timestamped, ~30 s blocks) and transcripts/<id>.json. Use this when YouTube's
auto-captions are missing or in the wrong language.
"""
import json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcript import metadata, OUT

AUDIO = Path(os.environ.get('DDS_AUDIO_DIR', '/tmp/dds-audio'))
MODEL = os.environ.get('DDS_WHISPER_MODEL', 'mlx-community/whisper-large-v3-turbo')
YTDLP = os.environ.get('YTDLP', '/opt/homebrew/bin/yt-dlp')

def download(vid):
    AUDIO.mkdir(parents=True, exist_ok=True)
    existing = list(AUDIO.glob(f'{vid}.*'))
    if existing:
        return existing[0]
    subprocess.run([YTDLP, '-q', '--no-warnings', '-f', 'bestaudio[ext=m4a]/bestaudio', '-o', str(AUDIO / '%(id)s.%(ext)s'),
                    f'https://www.youtube.com/watch?v={vid}'], check=True)
    return list(AUDIO.glob(f'{vid}.*'))[0]

def transcribe(vid):
    import mlx_whisper
    audio = download(vid)
    t0 = time.time()
    res = mlx_whisper.transcribe(str(audio), path_or_hf_repo=MODEL, language='bn', task='transcribe',
                                 condition_on_previous_text=False, no_speech_threshold=0.5, verbose=False)
    lines, block, block_start = [], [], 0.0
    for s in res['segments']:
        text = s['text'].strip()
        if not text:
            continue
        if s['start'] - block_start >= 30 and block:
            lines.append(f'[{int(block_start)//60:02d}:{int(block_start)%60:02d}] ' + ' '.join(block))
            block, block_start = [], s['start']
        block.append(text)
    if block:
        lines.append(f'[{int(block_start)//60:02d}:{int(block_start)%60:02d}] ' + ' '.join(block))
    try:
        meta = metadata(vid)
    except Exception as e:
        meta = {'id': vid, 'metadata_error': str(e)}
    meta['captions'] = {'lang': 'bn', 'source': MODEL}
    meta['transcriptWords'] = sum(len(l.split()) for l in lines)
    OUT.mkdir(exist_ok=True)
    (OUT / f'{vid}.txt').write_text('\n'.join(lines), encoding='utf-8')
    (OUT / f'{vid}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    return f'{vid}: {meta["transcriptWords"]} words in {time.time()-t0:.0f}s — {(meta.get("title") or "")[:60]}'

if __name__ == '__main__':
    for vid in sys.argv[1:]:
        try:
            print(transcribe(vid), flush=True)
        except Exception as e:
            print(f'{vid}: ERROR {type(e).__name__}: {str(e)[:300]}', flush=True)
