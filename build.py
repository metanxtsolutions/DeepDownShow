#!/usr/bin/env python3
"""Bundle the site into one self-contained HTML file (dist/deep-down-show.html).

Inlines CSS and JS, embeds every thumbnail and brand image as a data URI, and
switches video playback to open on YouTube (for hosts that block iframes).
"""
import base64, json, mimetypes, os, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
THUMBS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'thumbs'
OUT = ROOT / 'dist' / 'deep-down-show.html'

def data_uri(p: Path) -> str:
    mime = mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'css' / 'style.css').read_text(encoding='utf-8')
js = (ROOT / 'js' / 'main.js').read_text(encoding='utf-8')

body = html.split('<!--BODY-START-->')[1].split('<!--BODY-END-->')[0]
body = re.sub(r'src="(assets/[^"]+)"', lambda m: f'src="{data_uri(ROOT / m.group(1))}"', body)

SITE_URL = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))['url'].rstrip('/')
body = body.replace('href="episodes/', f'target="_blank" rel="noopener" href="{SITE_URL}/episodes/')
js = js.replace('const href = `episodes/${c.slug}/`;', f'const href = `{SITE_URL}/episodes/${{c.slug}}/`;')
thumbs = {p.stem: data_uri(p) for p in sorted(THUMBS.glob('*.jpg'))} if THUMBS.exists() else {}
body = re.sub(r'src="thumbs/([^"]+)\.jpg"', lambda m: f'src="{thumbs.get(m.group(1), m.group(0)[5:-1])}"', body)
fonts = re.search(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]+>', html).group(0)

out = f"""<title>Deep Down Show বাংলা</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<style>
{css}
</style>
<script>document.documentElement.classList.add('js');</script>
{body}
<script>window.DDS_EMBED=false;window.DDS_THUMBS={json.dumps(thumbs)};</script>
<script>
{js}
</script>
"""
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(out, encoding='utf-8')
print(f"wrote {OUT} ({OUT.stat().st_size/1e6:.2f} MB, {len(thumbs)} thumbnails)")
