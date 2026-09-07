# Writing an episode article

Every Deep Down Show episode gets one article at `articles/<slug>.md`. The article is
written **only after reading the complete transcript** of the episode. Nothing in the
article may come from the title, thumbnail or description alone, and nothing may be
invented. If the transcript does not support a claim, leave it out.

## Inputs
- `transcripts/<videoId>.txt` — the full spoken content, timestamped every ~30 s.
  It is machine-transcribed Bangla (YouTube auto-captions or Whisper), so names,
  numbers and English words are often misspelled. Use the episode title, description
  and context to correct obvious errors; when a detail stays unclear, omit it rather
  than guess. Do not quote transcription noise.
- `transcripts/<videoId>.json` — title, description, publish date, duration, views.
- The episode list in `docs/episodes.json` (slugs for internal links).

## Language and voice
- Write in clear English for a Bengali-speaking audience, with Bangla woven in
  naturally: the guest's most striking lines in Bangla with an English rendering,
  Bangla terms where the English is weaker, and Bangla keywords people actually
  search for (e.g. বাংলা পডকাস্ট, ব্যবসা, রামায়ণ). Never stuff keywords.
- Specific beats generic. Prefer the guest's own examples, numbers, place names,
  years and stories over summaries of the theme. No filler sentences about how
  "insightful" the conversation is.
- Report what the guest and host said; do not editorialise as if it were fact.
  Attribute opinions ("Basu argues…", "Barun asks…").
- Length: 1,500–3,000 words of body, scaled to how much ground the episode covers. Cut repetition, never real content.

## File format
JSON front matter between `---` lines, then Markdown body.

```
---
{
  "video_id": "upYFnCkCqxQ",
  "video_title": "exact YouTube title",
  "episode": 25,
  "slug": "karimul-haque-bike-ambulance-dada",
  "title": "SEO title, max 60 characters, guest name or key phrase first",
  "title_bn": "short Bangla title (optional but preferred)",
  "meta_description": "max 155 characters, specific, with the main keyword, ends with a hook",
  "lede": "one or two sentences shown under the headline (max ~240 characters)",
  "guest": "Karimul Haque",
  "guest_role": "Padma Shri, Bike Ambulance Dada of Jalpaiguri",
  "category": "society",            // business | society | culture | arts | science
  "published": "2026-09-05",        // the video's publish date
  "duration": "1:41:06",
  "keywords": ["8 to 15 English and Bangla keywords/phrases"],
  "takeaways": ["5 to 7 one-sentence takeaways, each a real point from the video"],
  "faq": [ {"q": "…", "a": "2–4 sentence answer grounded in the video"} ],   // 5 to 7
  "related": ["slug-a", "slug-b", "slug-c"],       // other articles, most relevant first
  "clips": [ {"id": "videoId", "title": "…"} ],     // shorts/clips cut from this episode, if any
  "parts": [ {"id": "videoId", "title": "Part 1 · …"} ]  // only for multi-part episodes
}
---
```

## Body structure (Markdown: `##`, `###`, paragraphs, `-` lists, `>` quotes, `**bold**`, links)
1. **Introduction** (2–3 paragraphs): who the guest is, what the conversation is really
   about, why it matters to the reader. Hook with a concrete moment from the episode.
2. **Sections with `##` headings** that follow the shape of the conversation, not the
   clock. Each section: the argument, the story behind it, the facts and figures the
   guest gives, and one quote where it earns its place. Use `> quote — Speaker` for
   quotes; for Bangla quotes write the Bangla, then the English in the next sentence.
3. **Who is <guest>** — a short factual section drawn from what the episode reveals.
4. **Why this conversation matters** — a closing section, specific to the episode.
5. Internal links inside the body: link at least two related articles by relative URL
   (`/episodes/<slug>/`), and the DDS Clips channel if clips exist
   (`https://www.youtube.com/@DDSClipsBangla`). Do not add an FAQ or video in the
   body — the build adds those from the front matter.

## Checks before finishing
- Every fact, number, name and quote traces to the transcript.
- Title ≤ 60 chars, meta description ≤ 155 chars, slug matches the file name.
- Valid JSON front matter (double quotes, no trailing commas, no comments).
- Run `python3 scripts/build_articles.py` — it fails loudly on missing fields.
