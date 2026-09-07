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
