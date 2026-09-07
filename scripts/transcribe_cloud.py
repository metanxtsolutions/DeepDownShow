#!/usr/bin/env python3
"""Transcribe YouTube videos with a cloud speech-to-text API (strong Bangla support).

Usage:  python3 scripts/transcribe_cloud.py VIDEO_ID [VIDEO_ID ...]
Env:    DDS_STT=openai|gemini|elevenlabs   (default: whichever API key is set)
        OPENAI_API_KEY / GEMINI_API_KEY / ELEVENLABS_API_KEY
        DDS_AUDIO_DIR (audio cache, default /tmp/dds-audio)
Keys can also live in ~/.dds-stt.env (KEY=value lines); that file is never committed.

Audio is downloaded with yt-dlp, split into 10-minute mono MP3 chunks, sent to the
API, and re-assembled into transcripts/<id>.txt (timestamped ~30 s blocks) and
transcripts/<id>.json, the same format the other transcript scripts produce.
"""
import json, os, subprocess, sys, time, urllib.request, mimetypes, uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcript import metadata, OUT

envfile = Path.home() / '.dds-stt.env'
if envfile.exists():
    for line in envfile.read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            k, v = line.split('=', 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

AUDIO = Path(os.environ.get('DDS_AUDIO_DIR', '/tmp/dds-audio'))
YTDLP = os.environ.get('YTDLP', '/opt/homebrew/bin/yt-dlp')
CHUNK = 600  # seconds
PROVIDER = os.environ.get('DDS_STT') or ('openai' if os.environ.get('OPENAI_API_KEY') else 'gemini' if os.environ.get('GEMINI_API_KEY') else 'elevenlabs' if os.environ.get('ELEVENLABS_API_KEY') else None)
if not PROVIDER:
    sys.exit('No API key found. Set OPENAI_API_KEY, GEMINI_API_KEY or ELEVENLABS_API_KEY (or put it in ~/.dds-stt.env).')

def download(vid):
    AUDIO.mkdir(parents=True, exist_ok=True)
    ex = list(AUDIO.glob(f'{vid}.m4a')) + list(AUDIO.glob(f'{vid}.*'))
    if ex: return ex[0]
    subprocess.run([YTDLP, '-q', '--no-warnings', '-f', 'bestaudio[ext=m4a]/bestaudio', '-o', str(AUDIO / '%(id)s.%(ext)s'), f'https://www.youtube.com/watch?v={vid}'], check=True)
    return list(AUDIO.glob(f'{vid}.*'))[0]

def chunks(vid, src):
    d = AUDIO / f'{vid}_chunks'; d.mkdir(exist_ok=True)
    if not list(d.glob('*.mp3')):
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-ac', '1', '-ar', '16000', '-b:a', '64k', '-f', 'segment', '-segment_time', str(CHUNK), str(d / '%03d.mp3')], check=True)
    return sorted(d.glob('*.mp3'))

def multipart(fields, files):
    b = uuid.uuid4().hex; body = b''
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, (name, data, ctype) in files.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"; filename="{name}"\r\nContent-Type: {ctype}\r\n\r\n'.encode() + data + b'\r\n'
    body += f'--{b}--\r\n'.encode()
    return body, f'multipart/form-data; boundary={b}'

def post(url, body, headers, retries=4):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            return json.loads(urllib.request.urlopen(req, timeout=900).read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode('utf-8', 'replace')[:300]
            if e.code in (429, 500, 502, 503) and i < retries - 1:
                time.sleep(10 * (i + 1)); continue
            raise RuntimeError(f'HTTP {e.code}: {msg}')

# each provider returns a list of (start_seconds, text) for one chunk
def stt_openai(path):
    body, ctype = multipart({'model': os.environ.get('OPENAI_STT_MODEL', 'gpt-4o-transcribe'), 'language': 'bn', 'response_format': 'json',
                             'prompt': 'বাংলা পডকাস্ট। সঞ্চালক বরুণ অতিথির সঙ্গে কথা বলছেন। মাঝে মাঝে ইংরেজি শব্দ।'},
                            {'file': (path.name, path.read_bytes(), 'audio/mpeg')})
    r = post('https://api.openai.com/v1/audio/transcriptions', body, {'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}', 'Content-Type': ctype})
    return [(0.0, r.get('text', ''))]

def stt_elevenlabs(path):
    body, ctype = multipart({'model_id': 'scribe_v1', 'language_code': 'ben', 'diarize': 'true', 'tag_audio_events': 'false'},
                            {'file': (path.name, path.read_bytes(), 'audio/mpeg')})
    r = post('https://api.elevenlabs.io/v1/speech-to-text', body, {'xi-api-key': os.environ['ELEVENLABS_API_KEY'], 'Content-Type': ctype})
    out, cur, cur_start, cur_spk = [], [], 0.0, None
    for w in r.get('words', []):
        if w.get('type') == 'spacing': continue
        spk = w.get('speaker_id')
        if spk != cur_spk and cur:
            out.append((cur_start, (f'[{cur_spk}] ' if cur_spk else '') + ''.join(cur).strip())); cur, cur_start = [], w.get('start', 0.0)
        if not cur: cur_start = w.get('start', 0.0)
        cur_spk = spk; cur.append(w.get('text', '') + ' ')
    if cur: out.append((cur_start, (f'[{cur_spk}] ' if cur_spk else '') + ''.join(cur).strip()))
    return out or [(0.0, r.get('text', ''))]

def stt_gemini(path):
    key = os.environ['GEMINI_API_KEY']; model = os.environ.get('GEMINI_STT_MODEL', 'gemini-2.5-flash')
    data = path.read_bytes()
    up = urllib.request.Request(f'https://generativelanguage.googleapis.com/upload/v1beta/files?key={key}', data=data,
        headers={'X-Goog-Upload-Protocol': 'raw', 'X-Goog-Upload-Command': 'upload, finalize', 'Content-Type': 'audio/mpeg', 'X-Goog-File-Name': path.name})
    f = json.loads(urllib.request.urlopen(up, timeout=600).read())['file']
    while f.get('state') == 'PROCESSING':
        time.sleep(3); f = json.loads(urllib.request.urlopen(f'https://generativelanguage.googleapis.com/v1beta/{f["name"]}?key={key}').read())
    prompt = ('Transcribe this Bangla podcast audio verbatim, in Bengali script (keep English words in Latin script as spoken). '
              'Output plain text only, one paragraph per speaker turn, prefixed with the speaker label [Host] or [Guest]. Do not summarise, do not translate, do not add commentary.')
    body = json.dumps({'contents': [{'parts': [{'file_data': {'file_uri': f['uri'], 'mime_type': 'audio/mpeg'}}, {'text': prompt}]}],
                       'generationConfig': {'temperature': 0, 'maxOutputTokens': 65536}}).encode()
    r = post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}', body, {'Content-Type': 'application/json'})
    text = ''.join(p.get('text', '') for p in r['candidates'][0]['content']['parts'])
    return [(0.0, text)]

STT = {'openai': stt_openai, 'elevenlabs': stt_elevenlabs, 'gemini': stt_gemini}[PROVIDER]

def transcribe(vid):
    t0 = time.time(); src = download(vid); parts = chunks(vid, src); lines = []
    for i, p in enumerate(parts):
        offset = i * CHUNK
        for start, text in STT(p):
            for para in [x for x in text.split('\n') if x.strip()]:
                t = offset + start
                lines.append(f'[{int(t)//60:02d}:{int(t)%60:02d}] {para.strip()}')
        print(f'  chunk {i+1}/{len(parts)} done', flush=True)
    try: meta = metadata(vid)
    except Exception as e: meta = {'id': vid, 'metadata_error': str(e)}
    meta['captions'] = {'lang': 'bn', 'source': f'{PROVIDER} stt'}
    meta['transcriptWords'] = sum(len(l.split()) for l in lines)
    OUT.mkdir(exist_ok=True)
    (OUT / f'{vid}.txt').write_text('\n'.join(lines), encoding='utf-8')
    (OUT / f'{vid}.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding='utf-8')
    return f'{vid}: {meta["transcriptWords"]} words via {PROVIDER} in {time.time()-t0:.0f}s — {(meta.get("title") or "")[:60]}'

if __name__ == '__main__':
    for vid in sys.argv[1:]:
        try: print(transcribe(vid), flush=True)
        except Exception as e: print(f'{vid}: ERROR {type(e).__name__}: {str(e)[:300]}', flush=True)
