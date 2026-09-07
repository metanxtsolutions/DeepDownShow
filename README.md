# Deep Down Show বাংলা — website

A static, dependency-free website for **Deep Down Show – বাংলা**, the first Bangla
talk-show podcast (Startupians, Kolkata), hosted by Barun.

## Run locally

```bash
python3 -m http.server 4173
```

Then open http://localhost:4173. Any static host works for deployment
(Netlify, Vercel, GitHub Pages, Cloudflare Pages): upload the folder as-is.

## Deploy to Vercel

The site is plain static files, so no framework preset or build command is needed.

1. Push this folder to a Git repository (GitHub, GitLab or Bitbucket).
2. In Vercel, **Add New → Project**, import the repository, leave the framework as
   **Other**, leave build command and output directory empty, and deploy.

Or deploy straight from this folder with the CLI:

```bash
npx vercel --prod
```

`vercel.json` sets long cache headers for `assets/`, `thumbs/`, `css/` and `js/`
and a few security headers. `.vercelignore` keeps `dist/` and the build script out
of the deployment.

## Thumbnails

`thumbs/` holds one `<videoId>.jpg` per video (720px wide) and `<videoId>_v.jpg`
for vertical shorts. The page loads these locally; if a file is missing it falls
back to YouTube's CDN. To add a new episode, drop its thumbnail here:

```bash
curl -sL "https://i.ytimg.com/vi/<videoId>/maxresdefault.jpg" -o thumbs/<videoId>.jpg
```

## Episode articles

Every episode has a full SEO article at `/episodes/<slug>/`, written from the complete
transcript of the video (never from the title or description alone). Sources live in
`articles/<slug>.md` (JSON front matter + Markdown body); the pages, the index at
`/episodes/`, `sitemap.xml` and `robots.txt` are generated:

```bash
python3 scripts/build_articles.py
```

Set the production domain once in `site.json` (`url`); canonical URLs, Open Graph
tags, schema and the sitemap all use it.

### Adding a new episode (the workflow)

1. `python3 scripts/new_episode.py <videoId> --slug <clean-slug>` downloads the
   thumbnail, fetches the complete transcript (Bangla auto-captions, or a local Whisper
   transcription via `scripts/transcribe.py` when captions are missing or in the wrong
   language) and scaffolds `articles/<slug>.md`.
2. Read `docs/article-guide.md`, then read the whole transcript, then write the article
   (SEO title, meta description, lede, keywords in English and Bangla, takeaways, FAQ,
   related links, clips) into the scaffold.
3. Add the episode to `EPISODES` in `js/main.js` and to `docs/episodes.json`.
4. `python3 scripts/build_articles.py && python3 build.py`, then commit and push.

In Claude Code the whole sequence is one command: `/article <videoId or URL>`
(see `.claude/commands/article.md`).

One-time setup for transcripts:

```bash
python3 -m pip install --user youtube-transcript-api
brew install yt-dlp whisper-cpp ffmpeg
```

YouTube's own Bangla auto-captions are used when they exist (episodes from 2024 on).
Older recordings are mislabelled by YouTube as English or Hindi, and vanilla Whisper
loops and garbles their Bangla, so `scripts/transcribe.py` runs whisper.cpp with a
Bangla fine-tune converted to ggml. The IISc Vaani model (spontaneous Indian speech)
gave the most coherent output; Mozilla's `whisper-large-v3-turbo-bn` is a good second.
To build the model file once:

```bash
python3.12 -m venv ~/.venvs/dds-stt && ~/.venvs/dds-stt/bin/pip install torch transformers openai-whisper huggingface_hub
curl -sL -o ~/.cache/whisper-cpp/convert-h5-to-ggml.py https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/models/convert-h5-to-ggml.py
~/.venvs/dds-stt/bin/python -c "from huggingface_hub import snapshot_download; snapshot_download('ARTPARK-IISc/whisper-medium-vaani-bengali', local_dir='$HOME/.cache/whisper-cpp/hf-vaani')"
SITE=$(~/.venvs/dds-stt/bin/python -c 'import whisper,os;print(os.path.dirname(os.path.dirname(whisper.__file__)))')
mkdir -p ~/.cache/whisper-cpp/out-vaani && ~/.venvs/dds-stt/bin/python ~/.cache/whisper-cpp/convert-h5-to-ggml.py ~/.cache/whisper-cpp/hf-vaani "$SITE" ~/.cache/whisper-cpp/out-vaani
curl -sL -o ~/.cache/whisper-cpp/ggml-silero-v5.1.2.bin https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v5.1.2.bin
export DDS_WHISPER_MODEL=~/.cache/whisper-cpp/out-vaani/ggml-model.bin
```

Always run `python3 scripts/transcript_quality.py <id>` afterwards: only GOOD or WEAK
transcripts may be turned into articles, and WEAK ones get shorter, more conservative
articles. `scripts/transcribe_cloud.py` is an optional alternative if an API key for
OpenAI, Gemini or ElevenLabs is ever available.

`transcripts/` is git-ignored (regenerate with the scripts above).

## Build the single-file version

```bash
python3 build.py
```

Writes `dist/deep-down-show.html`: CSS and JS inlined, every thumbnail and brand
image embedded as a data URI, and playback switched to open on YouTube (for hosts
that block iframes, such as the Claude artifact viewer).

## Structure

| Path | What it is |
| --- | --- |
| `index.html` | Page markup: nav, hero, stats, episodes, running threads, shorts, DDS Clips band, guests, about, platforms, collab CTA, footer, modal player |
| `css/style.css` | Design tokens (dark-first, light theme via `prefers-color-scheme` or `data-theme`), components, responsive rules, reduced-motion rules |
| `js/main.js` | Content data and behaviour: episode grid + filters, shorts and guest rails, clips stack, modal YouTube player, theme toggle, reveal animations, count-up stats |
| `build.py` | Bundles everything into `dist/deep-down-show.html` |
| `articles/`, `episodes/` | Article sources and the generated article pages |
| `scripts/` | `transcript.py`, `transcribe.py`, `new_episode.py`, `build_articles.py` |
| `docs/` | `article-guide.md` (writing rules) and `episodes.json` (slug registry) |
| `thumbs/` | Episode, short and clip thumbnails served by the site |
| `vercel.json` | Vercel headers and URL settings |
| `assets/` | Channel logo mark, show banner, favicon |

## Updating content

All content lives at the top of `js/main.js`:

- `EPISODES` — every full episode: YouTube id, episode number, category
  (`business`, `society`, `culture`, `arts`, `science`), duration, date, views, guest,
  title. `feature: true` marks the large card; `parts: 2` notes multi-part episodes.
- `SHORTS` — vertical shorts.
- `CLIPS` — the three clips shown in the DDS Clips band.
- `GUESTS` — guest cards with role and a pull quote.

The featured hero episode is set with `data-id` and `data-title` on `#featuredPlayer`
in `index.html`.

## Design notes

- Palette from the channel's identity: deep navy ground, mustard accent, the brand red
  reserved for the wordmark and live marks, sky blue for the বাংলা plate, paper for text.
- Type: Bricolage Grotesque (display), Instrument Serif italic (accents),
  Instrument Sans (body), Tiro Bangla / Hind Siliguri (Bengali). Loaded from Google Fonts.
- The hero wordmark is an inline SVG whose DDS letters are filled with a drifting field
  of Bengali glyphs, echoing the channel logo. Every animation respects
  `prefers-reduced-motion`.
