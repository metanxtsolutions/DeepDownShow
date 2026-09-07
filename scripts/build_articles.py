#!/usr/bin/env python3
"""Build episode article pages from articles/*.md.

Each article file starts with a JSON front matter block between `---` lines,
followed by the article body in Markdown. Output:
  episodes/<slug>/index.html   one page per article (Article + VideoObject + FAQ schema)
  episodes/index.html          the article index
  sitemap.xml, robots.txt
Run:  python3 scripts/build_articles.py
"""
import html, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
BASE = SITE['url'].rstrip('/')
ART = ROOT / 'articles'
OUT = ROOT / 'episodes'

CAT_LABEL = {'business': 'Business & Startups', 'society': 'Society & Health', 'culture': 'Culture & Mythology',
             'arts': 'Arts & Cinema', 'science': 'Science & Tech'}
REQUIRED = ['video_id', 'episode', 'slug', 'title', 'meta_description', 'guest', 'category', 'published', 'duration', 'keywords', 'faq']

# ---------------------------------------------------------------- markdown (small, dependency-free)
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', lambda m: f'<a href="{m.group(2)}"{" target=_blank rel=noopener" if m.group(2).startswith("http") else ""}>{m.group(1)}</a>', s)
    return s

def markdown(md):
    out, i, lines = [], 0, md.strip().split('\n')
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1; continue
        if line.startswith('### '):
            out.append(f'<h3 id="{slugify(line[4:])}">{inline(line[4:])}</h3>'); i += 1; continue
        if line.startswith('## '):
            out.append(f'<h2 id="{slugify(line[3:])}">{inline(line[3:])}</h2>'); i += 1; continue
        if line.strip() == '---':
            out.append('<hr>'); i += 1; continue
        if line.startswith('> '):
            block = []
            while i < len(lines) and lines[i].startswith('>'):
                block.append(lines[i][1:].strip()); i += 1
            text = ' '.join(b for b in block if b)
            cite = ''
            m = re.search(r'\s+[—–-]\s*([^—–]+)$', text)
            if m and len(m.group(1)) < 60:
                cite, text = m.group(1), text[:m.start()]
            out.append(f'<blockquote><p>{inline(text)}</p>{f"<cite>{inline(cite)}</cite>" if cite else ""}</blockquote>')
            continue
        if re.match(r'^(\-|\*) ', line):
            items = []
            while i < len(lines) and re.match(r'^(\-|\*) ', lines[i]):
                items.append(inline(lines[i][2:].strip())); i += 1
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'); continue
        if re.match(r'^\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(inline(re.sub(r'^\d+\. ', '', lines[i]).strip())); i += 1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'); continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{2,3} |> |\-|\* |\d+\. |---$)', lines[i]):
            para.append(lines[i].strip()); i += 1
        out.append(f'<p>{inline(" ".join(para))}</p>')
    return '\n'.join(out)

def slugify(s):
    s = re.sub(r'<[^>]+>', '', s).lower()
    s = re.sub(r'[^a-z0-9ঀ-৿]+', '-', s).strip('-')
    return s[:60] or 'section'

# ---------------------------------------------------------------- articles
def load(path):
    raw = path.read_text(encoding='utf-8')
    m = re.match(r'^---\s*\n(\{.*?\})\s*\n---\s*\n(.*)$', raw, re.S)
    if not m:
        sys.exit(f'{path.name}: missing JSON front matter between --- lines')
    meta = json.loads(m.group(1))
    missing = [k for k in REQUIRED if k not in meta]
    if missing:
        sys.exit(f'{path.name}: missing fields {missing}')
    meta['body_md'] = m.group(2).strip()
    meta['file'] = path.name
    if meta['slug'] != path.stem:
        sys.exit(f'{path.name}: slug "{meta["slug"]}" must match the file name')
    return meta

def iso_duration(d):
    parts = [int(x) for x in d.split(':')]
    while len(parts) < 3: parts.insert(0, 0)
    h, m, s = parts
    return f'PT{h}H{m}M{s}S'

def fmt_date(iso):
    return date.fromisoformat(iso).strftime('%-d %B %Y')

def toc(body_html):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body_html)
    if len(heads) < 3: return ''
    items = ''.join(f'<li><a href="#{i}">{re.sub(r"<[^>]+>", "", t)}</a></li>' for i, t in heads)
    return f'<nav class="toc" aria-label="In this article"><p class="toc__label">In this article</p><ol>{items}</ol></nav>'

def card(a, small=False):
    return f'''<a class="epcard" href="/episodes/{a["slug"]}/">
      <span class="epcard__thumb"><img src="/thumbs/{a["video_id"]}.jpg" alt="" loading="lazy"><span class="epcard__dur">{a["duration"]}</span></span>
      <span class="epcard__body"><span class="epcard__kicker">DDS {a["episode"]} · {CAT_LABEL.get(a["category"], a["category"])}</span>
      <span class="epcard__title">{html.escape(a["title"])}</span><span class="epcard__guest">Ft. {html.escape(a["guest"])}</span></span></a>'''

def shell(title, description, canonical, body, extra_head='', og_image=None, og_type='website'):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{html.escape(SITE['name'])}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image or BASE + '/' + SITE['logo']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#090E22">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,300..800&family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=Instrument+Serif:ital@0;1&family=Tiro+Bangla:ital@0;1&family=Hind+Siliguri:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/css/style.css">
<link rel="stylesheet" href="/css/article.css">
<script>document.documentElement.classList.add('js');try{{var t=localStorage.getItem('dds-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
{extra_head}
</head>
<body class="article-page">
<div class="grain" aria-hidden="true"></div>
<header class="nav is-scrolled" id="nav">
  <div class="nav__inner">
    <a class="brand" href="/" aria-label="Deep Down Show Bangla, home">
      <img class="brand__mark" src="/assets/logo-mark-512.jpg" alt="" width="40" height="40">
      <span class="brand__word"><span class="brand__dds">DDS</span><span class="brand__sub">Deep Down Show</span></span>
      <span class="brand__bn">বাংলা</span>
    </a>
    <nav class="nav__links" aria-label="Primary">
      <a href="/#episodes">Episodes</a>
      <a href="/episodes/">Articles</a>
      <a href="/#guests">Guests</a>
      <a href="/#about">About</a>
      <a href="/#listen">Listen</a>
    </nav>
    <div class="nav__actions">
      <button class="theme-toggle" id="themeToggle" type="button" aria-label="Switch theme" title="Switch theme">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path class="sun" d="M12 4V2M12 22v-2M4 12H2M22 12h-2M5.6 5.6 4.2 4.2M19.8 19.8l-1.4-1.4M5.6 18.4l-1.4 1.4M19.8 4.2l-1.4 1.4M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path class="moon" d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5Z" fill="currentColor"/></svg>
      </button>
      <a class="btn btn--accent btn--sm" href="{SITE['channel']}?sub_confirmation=1" target="_blank" rel="noopener">Subscribe</a>
    </div>
  </div>
</header>
<main>
{body}
</main>
<footer class="footer">
  <div class="container footer__bottom">
    <p>© {date.today().year} {html.escape(SITE['publisher'])} · Deep Down Show. Kolkata, India.</p>
    <p><a href="/">Home</a> · <a href="/episodes/">All articles</a> · <a href="{SITE['channel']}" target="_blank" rel="noopener">YouTube</a></p>
  </div>
</footer>
<script src="/js/article.js" defer></script>
</body>
</html>
'''

def render_article(a, by_slug, all_articles):
    url = f'{BASE}/episodes/{a["slug"]}/'
    body_html = markdown(a['body_md'])
    related = [by_slug[s] for s in a.get('related', []) if s in by_slug and s != a['slug']][:3]
    if len(related) < 3:
        for o in all_articles:
            if o['slug'] != a['slug'] and o not in related and o['category'] == a['category']:
                related.append(o)
            if len(related) >= 3: break
    faq_html = ''.join(f'<details class="faq__item"><summary>{html.escape(q["q"])}</summary><div class="faq__a">{markdown(q["a"])}</div></details>' for q in a['faq'])
    clips = a.get('clips', [])
    clips_html = ''
    if clips:
        items = ''.join(f'<a class="clipchip" href="https://www.youtube.com/watch?v={c["id"]}" target="_blank" rel="noopener"><img src="/thumbs/{c["id"]}.jpg" alt="" loading="lazy" onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{c["id"]}/hqdefault.jpg\'"><span>{html.escape(c["title"])}</span></a>' for c in clips)
        clips_html = f'<section class="article__clips"><h2 id="clips-from-this-episode">Clips from this episode</h2><div class="clipchips">{items}</div></section>'
    takeaways = a.get('takeaways', [])
    takeaways_html = '<aside class="takeaways"><p class="takeaways__label">Key takeaways</p><ul>' + ''.join(f'<li>{inline(t)}</li>' for t in takeaways) + '</ul></aside>' if takeaways else ''
    kw = ', '.join(a['keywords'])
    parts = a.get('parts', [])
    parts_html = ''
    if parts:
        parts_html = '<p class="article__parts">This episode was published in parts: ' + ', '.join(f'<a href="https://www.youtube.com/watch?v={p["id"]}" target="_blank" rel="noopener">{html.escape(p["title"])}</a>' for p in parts) + '.</p>'

    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": a['title'], "description": a['meta_description'],
         "inLanguage": "en", "datePublished": a['published'], "dateModified": a.get('updated', a['published']),
         "author": {"@type": "Organization", "name": SITE['name'], "url": BASE},
         "publisher": {"@type": "Organization", "name": SITE['publisher'], "logo": {"@type": "ImageObject", "url": f'{BASE}/{SITE["logo"]}'}},
         "image": f'{BASE}/thumbs/{a["video_id"]}.jpg', "mainEntityOfPage": url, "keywords": kw,
         "about": {"@type": "Person", "name": a['guest']}},
        {"@context": "https://schema.org", "@type": "VideoObject", "name": a.get('video_title', a['title']), "description": a['meta_description'],
         "thumbnailUrl": [f'{BASE}/thumbs/{a["video_id"]}.jpg', f'https://i.ytimg.com/vi/{a["video_id"]}/maxresdefault.jpg'],
         "uploadDate": a['published'], "duration": iso_duration(a['duration']),
         "contentUrl": f'https://www.youtube.com/watch?v={a["video_id"]}', "embedUrl": f'https://www.youtube.com/embed/{a["video_id"]}',
         "publisher": {"@type": "Organization", "name": SITE['name'], "logo": {"@type": "ImageObject", "url": f'{BASE}/{SITE["logo"]}'}},
         "inLanguage": "bn", "isPartOf": {"@type": "PodcastSeries", "name": "Deep Down Show", "url": BASE}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q['q'], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'<[^>]+>', '', markdown(q['a']))}} for q in a['faq']]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + '/'},
            {"@type": "ListItem", "position": 2, "name": "Episodes", "item": BASE + '/episodes/'},
            {"@type": "ListItem", "position": 3, "name": a['title'], "item": url}]},
    ]
    extra_head = f'<meta name="keywords" content="{html.escape(kw)}">\n' + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in ld)

    body = f'''
<article class="article">
  <header class="article__head container">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/episodes/">Episodes</a><span>/</span><span>DDS {a["episode"]}</span></nav>
    <p class="eyebrow"><span class="ep-num">DDS {a["episode"]}</span> · {CAT_LABEL.get(a["category"], a["category"])}{f' · <span class="bn">{html.escape(a["title_bn"])}</span>' if a.get("title_bn") else ''}</p>
    <h1 class="article__title">{html.escape(a["title"])}</h1>
    <p class="article__lede">{html.escape(a.get("lede", a["meta_description"]))}</p>
    <dl class="article__meta">
      <div><dt>Guest</dt><dd>{html.escape(a["guest"])}{f'<span>{html.escape(a["guest_role"])}</span>' if a.get("guest_role") else ''}</dd></div>
      <div><dt>Host</dt><dd>{html.escape(SITE["host"])}</dd></div>
      <div><dt>Published</dt><dd><time datetime="{a["published"]}">{fmt_date(a["published"])}</time></dd></div>
      <div><dt>Runtime</dt><dd>{a["duration"]}</dd></div>
    </dl>
  </header>

  <div class="container article__video">
    <div class="video" data-id="{a["video_id"]}">
      <iframe src="https://www.youtube-nocookie.com/embed/{a["video_id"]}?rel=0" title="{html.escape(a.get("video_title", a["title"]))}" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
    </div>
    <p class="video__links"><a href="https://www.youtube.com/watch?v={a["video_id"]}" target="_blank" rel="noopener">Watch on YouTube ↗</a>{parts_html}</p>
  </div>

  <div class="container article__grid">
    <div class="article__body prose">
      {takeaways_html}
      {toc(body_html)}
      {body_html}
      <section class="faq"><h2 id="faq">Frequently asked questions</h2>{faq_html}</section>
      {clips_html}
      <p class="article__tags">{''.join(f'<span>{html.escape(k)}</span>' for k in a["keywords"])}</p>
    </div>
    <aside class="article__side">
      <div class="sidecard">
        <p class="sidecard__label">Listen everywhere</p>
        <a href="{SITE['channel']}" target="_blank" rel="noopener">YouTube · full episodes</a>
        <a href="https://podcasters.spotify.com/pod/show/startupians-u09acu09beu0982u09b2u09be" target="_blank" rel="noopener">Spotify · audio</a>
        <a href="{SITE['clips_channel']}" target="_blank" rel="noopener">DDS Clips · short cuts</a>
      </div>
      <div class="sidecard">
        <p class="sidecard__label">Related episodes</p>
        {''.join(f'<a href="/episodes/{r["slug"]}/">DDS {r["episode"]} · {html.escape(r["title"])}</a>' for r in related)}
      </div>
    </aside>
  </div>

  <section class="container article__related">
    <h2>Keep going deep</h2>
    <div class="epgrid">{''.join(card(r) for r in related)}</div>
    <p class="article__all"><a class="btn btn--ghost" href="/episodes/">All episode articles →</a></p>
  </section>
</article>
'''
    return shell(a['title'], a['meta_description'], url, body, extra_head, og_image=f'{BASE}/thumbs/{a["video_id"]}.jpg', og_type='article')

def render_index(articles):
    url = BASE + '/episodes/'
    cats = {}
    for a in articles:
        cats.setdefault(a['category'], []).append(a)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Deep Down Show episodes", "url": url,
          "hasPart": [{"@type": "Article", "headline": a['title'], "url": f'{BASE}/episodes/{a["slug"]}/'} for a in articles]}
    body = f'''
<section class="container index">
  <header class="section__head">
    <p class="eyebrow"><span class="bn">সব পর্বের লেখা</span> · Episode articles</p>
    <h1 class="h2">Every episode, <em class="serif">written up in full.</em></h1>
    <p class="section__lede">Each article is built from the complete conversation: the arguments, the stories, the numbers and the quotes, with the episode embedded so you can watch as you read.</p>
  </header>
  <div class="epgrid epgrid--index">{''.join(card(a) for a in articles)}</div>
</section>
'''
    return shell('Episode articles · Deep Down Show বাংলা', 'Full written articles for every Deep Down Show episode: business, society, health, mythology, cinema and science, from the first Bangla talk-show podcast.',
                 url, body, f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')

def main():
    files = sorted(ART.glob('*.md'))
    articles = sorted((load(p) for p in files), key=lambda a: -int(a['episode']))
    by_slug = {a['slug']: a for a in articles}
    OUT.mkdir(exist_ok=True)
    for a in articles:
        d = OUT / a['slug']; d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(render_article(a, by_slug, articles), encoding='utf-8')
    (OUT / 'index.html').write_text(render_index(articles), encoding='utf-8')
    today = date.today().isoformat()
    urls = [(BASE + '/', today, '1.0'), (BASE + '/episodes/', today, '0.8')] + [(f'{BASE}/episodes/{a["slug"]}/', a.get('updated', a['published']), '0.7') for a in articles]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{u}</loc><lastmod>{m}</lastmod><priority>{p}</priority></url>\n' for u, m, p in urls) + '</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n', encoding='utf-8')
    # slug map for the home page
    (ROOT / 'js' / 'episode-links.js').write_text('window.DDS_ARTICLES=' + json.dumps({a['video_id']: a['slug'] for a in articles}) + ';\n', encoding='utf-8')
    print(f'built {len(articles)} articles → episodes/, sitemap.xml, robots.txt')

if __name__ == '__main__':
    main()
