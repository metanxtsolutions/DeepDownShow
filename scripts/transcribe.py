#!/usr/bin/env python3
"""Transcribe YouTube videos locally with whisper.cpp (Metal on Apple Silicon).

Usage: python3 scripts/transcribe.py VIDEO_ID [VIDEO_ID ...]
Env:   DDS_WHISPER_MODEL  path to a ggml model (default ~/.cache/whisper-cpp/ggml-large-v3-q5_0.bin)
       DDS_VAD_MODEL      path to the Silero VAD ggml model (default ~/.cache/whisper-cpp/ggml-silero-v5.1.2.bin)
       DDS_AUDIO_DIR      audio cache (default /tmp/dds-audio)
       DDS_DENOISE=1      apply an ffmpeg high-pass/denoise/normalise chain first
Requires: brew install yt-dlp whisper-cpp ffmpeg

Downloads the audio with yt-dlp, converts to 16 kHz mono WAV, runs whisper-cli in
Bangla with greedy decoding, no context carry-over and VAD segmentation (which keeps
the model from looping on hard audio), and writes transcripts/<id>.txt (timestamped
~30 s blocks) and transcripts/<id>.json. Use this when YouTube has no usable Bangla
captions. Always run scripts/transcript_quality.py on the result before writing.
"""
import json, os, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcript import metadata, OUT

HOME = Path.home()
AUDIO = Path(os.environ.get('DDS_AUDIO_DIR', '/tmp/dds-audio'))
MODEL = os.environ.get('DDS_WHISPER_MODEL', str(HOME / '.cache/whisper-cpp/ggml-large-v3-q5_0.bin'))
VAD = os.environ.get('DDS_VAD_MODEL', str(HOME / '.cache/whisper-cpp/ggml-silero-v5.1.2.bin'))
YTDLP = os.environ.get('YTDLP', '/opt/homebrew/bin/yt-dlp')
WHISPER = os.environ.get('WHISPER_CLI', 'whisper-cli')
DENOISE = os.environ.get('DDS_DENOISE') == '1'

def download(vid):
    AUDIO.mkdir(parents=True, exist_ok=True)
    ex = list(AUDIO.glob(f'{vid}.m4a')) + [p for p in AUDIO.glob(f'{vid}.*') if p.suffix != '.wav']
    if not ex:
        subprocess.run([YTDLP, '-q', '--no-warnings', '-f', 'bestaudio[ext=m4a]/bestaudio', '-o', str(AUDIO / '%(id)s.%(ext)s'), f'https://www.youtube.com/watch?v={vid}'], check=True)
        ex = [p for p in AUDIO.glob(f'{vid}.*') if p.suffix != '.wav']
    wav = AUDIO / f'{vid}.wav'
    if not wav.exists():
        af = 'highpass=f=120,afftdn=nf=-28:nr=15:tn=1,dynaudnorm=f=150:g=15' if DENOISE else 'anull'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(ex[0]), '-ac', '1', '-ar', '16000', '-af', af, str(wav)], check=True)
    return wav

def run_whisper(wav):
    prefix = wav.with_suffix('')
    cmd = [WHISPER, '-m', MODEL, '-l', 'bn', '-t', '8', '-np', '-mc', '0', '-nf', '-bo', '1', '-bs', '1', '-et', '2.4',
           '--vad', '--vad-model', VAD, '-osrt', '-of', str(prefix), '-f', str(wav)]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    # whisper.cpp tokens are byte-level, so a multibyte character can straddle a segment: decode leniently.
    srt = prefix.with_suffix('.srt').read_bytes().decode('utf-8', 'replace').replace('\ufffd', '')
    segs = []
    for block in re.split(r'\n\s*\n', srt.strip()):
        lines = block.strip().split('\n')
        if len(lines) < 3: continue
        m = re.match(r'(\d+):(\d+):(\d+)[,.]\d+ -->', lines[1])
        if not m: continue
        t = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
        text = ' '.join(l.strip() for l in lines[2:]).strip()
        if text: segs.append((t, text))
    return segs

def collapse_repeats(text):
    """Collapse runs of the same word/phrase repeated 3+ times (a Whisper failure mode)."""
    text = re.sub(r'(\S+)(\s+\1){2,}', r'\1', text)
    text = re.sub(r'((?:\S+\s+){1,4}?)(\1){2,}', r'\1', text)
    return text

def transcribe(vid):
    t0 = time.time(); wav = download(vid); segs = run_whisper(wav)
    lines, block, block_start = [], [], 0
    for t, text in segs:
        if t - block_start >= 30 and block:
            lines.append(f'[{block_start//60:02d}:{block_start%60:02d}] ' + collapse_repeats(' '.join(block)))
            block, block_start = [], t
        block.append(text)
    if block:
        lines.append(f'[{block_start//60:02d}:{block_start%60:02d}] ' + collapse_repeats(' '.join(block)))
    try: meta = metadata(vid)
    except Exception as e: meta = {'id': vid, 'metadata_error': str(e)}
    meta['captions'] = {'lang': 'bn', 'source': f'whisper.cpp {Path(MODEL).name}' + (' +denoise' if DENOISE else '')}
    meta['transcriptWords'] = sum(len(l.split()) for l in lines)
    OUT.mkdir(exist_ok=True)
    (OUT / f'{vid}.txt').write_text('\n'.join(lines), encoding='utf-8')
    (OUT / f'{vid}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    return f'{vid}: {meta["transcriptWords"]} words in {time.time()-t0:.0f}s — {(meta.get("title") or "")[:60]}'

if __name__ == '__main__':
    for vid in sys.argv[1:]:
        try: print(transcribe(vid), flush=True)
        except Exception as e: print(f'{vid}: ERROR {type(e).__name__}: {str(e)[:300]}', flush=True)
