---
name: video-mp
description: "Video MP" style — turn a Malaysian Parliament (Dewan Rakyat / Kamar Khas) speech recording into a 60–90 s vertical (1080x1920) documentary-style short with a navy information band, word-timed gold/yellow cards, Malay word-highlight captions, end card, SRTs and a Malay production pack. Use when the person asks for "Video MP", "style Video MP", a parliamentary speech short like the Parit videos, or gives a Dewan Rakyat recording (Drive link or file) to cut.
---

# Video MP

A house style built from two finished episodes in this repo: the root project (Parit, RMK13, Dewan Rakyat) and `pengezonan-padi/` (Kamar Khas, paddy zoning). The engine `engine/vmp.py` rebuilds `pengezonan-padi` near pixel-for-pixel from `examples/pengezonan-padi.episode.json`; start every new episode from that file.

Read `/hyperframes` first (render contract). Read `references/design.md` before changing anything visual, and `references/lessons.md` before downloading or transcribing.

## What every episode delivers

In `<episode>/deliverables/`:
1. `<id>.mp4`: 1080×1920, 30 fps, H.264/AAC, 60–90 s, −14 to −16 LUFS, true peak ≤ −1 dBTP.
2. `PAKEJ-PRODUKSI.md` (in Malay): analysis table, 5 titles, 3–5 points (Isu, Petikan asal, Ringkasan ≤15 words, Timestamp asal + video, On-screen text ≤7 words, Visual), SRT review table, storyboard by second, social caption with hashtags, music note.
3. `subtitles-video.srt` (video clock) and `subtitles-source.srt` (original-recording clock), both written by the engine.

Also `<episode>/REVIEW.md` (creative calls, what was measured vs. looked at, weakest shot). Use the two existing packs as the template.

## Integrity rules (non-negotiable)

- Only the speaker's real words. Every clip is a **complete sentence**; never cut mid-sentence. Reordering for narrative is allowed only if the meaning holds; list each clip's original timestamp in the storyboard.
- No invented statistics, reactions, applause or quotes. A number whose referent the speech doesn't state (e.g. "lebih 50%") is shown as a quote with the pill "Petikan ucapan", never as a stat card.
- Facts from someone else (e.g. the minister's reply) only on the end card, attributed in its box title, and re-checked with whisper large-v3.
- No date unless verified. No Parliament logo or crest. Credit the footage on the end card.
- Name: read it from the desk nameplate or the broadcast label, and tell the person to confirm the spelling.
- Place names: check them against the person's knowledge. Whisper writes "Titik Gantung" for **Titi Gantung**, "Aida" for **IADA**, "Jalapang" for **jelapang**, "pesawat" for **pesawah**. Add each new fix to `references/lessons.md`.

## Work loop

1. **Get the footage.** Drive folders: list them with the Google Drive connector, check `get_file_permissions` (anyone-with-link), then download with curl from `drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`. If the host is refused, the session needs the **Video-Dr-K** environment (it allows Drive, Hugging Face and HeyGen): move with `switch_environment`.
2. **Scaffold.**
   ```bash
   python3 .claude/skills/video-mp/engine/vmp.py init <episode>
   ```
   Then put the recording in `<episode>/assets/source/`.
3. **Map the recording.** Make a 1-frame-per-30 s contact sheet and run scene detection to find who speaks when (MP / minister / follow-up). Read the nameplate or label at full resolution.
4. **Transcribe the MP's parts only**, with whisper large-v3 in Malay. Use `NODE_USE_ENV_PROXY=1`. Cut a 16 kHz wav per part; 17 minutes of full large-v3 is too slow on this machine. Copy each result to `assets/source/<part>.json` straight away, because the CLI overwrites `transcript.json`. A fast `small` pass on the other speakers is fine for context, but **re-check any number** with large-v3.
5. **Choose 4–6 complete sentences** (60–90 s total) on this spine: **hook** (the strongest line, 6–10 s) → **issue/facts** → **problem** → **proposal** → **climax/target**. Then the end card (6.5 s). A short source (< 60 s) plays uncut after a hook that repeats its best line.
6. **Write `episode.json`** (schema below). Set `text` per segment to the corrected sentence. The word count must equal whisper's count for that time range; `a|b` splits one whisper word. Place the 3:4 crop over the speaker, excluding any burned-in label bar, and measure `face` (centre of eyes/nose) in the 1080×1440 plate.
7. **Build.**
   ```bash
   python3 .claude/skills/video-mp/engine/vmp.py segments <episode>
   ```
   ```bash
   python3 .claude/skills/video-mp/engine/vmp.py build <episode>
   ```
8. **Check and look.** Run `npx hyperframes check --json` from the episode folder (0 errors), then `npx hyperframes snapshot --at <every card>`. Fix wraps, faces under cards, and unread lines. Re-run `build` after every `episode.json` edit; never hand-edit the generated HTML.
9. **Preview, render and measure.** Run `npx hyperframes preview --background` and report its port. Then render with `npx hyperframes render --quality delivery --output renders/<id>.mp4` (about 13–20 min here). Run `npx hyperframes audio <mp4> --json` and adjust `speech_volume` until the result is −14 to −16 LUFS. Copy the file to `deliverables/` and `git add -f` it (`*.mp4` is git-ignored). Same for the `assets/seg-*.mp4` files, so the project can re-render.
10. **Music.** There is no licensed bed unless HeyGen is signed in (`npx hyperframes auth login`) or the person supplies a track. Say so plainly. `index.html` carries a commented `<audio id="music">` slot at volume 0.14.

## episode.json schema

Every time is **source seconds** (the whisper clock). The engine converts these to video and scene time.

| Key | Meaning |
| --- | --- |
| `source`, `crop [w,h,x,y]` (3:4), `face [x,y]` (in the 1080×1440 plate) | Footage and framing |
| `gain_db` (cut-time), `speech_volume` (render-time) | Loudness |
| `grade` | media-treatment payload (Natural Portrait; lift exposure/shadows for dim Kamar Khas footage) |
| `location`, `location_lt`, `mp {name, name_lines, seat}` | Labels |
| `transcripts [{file, offset}]` | Whisper JSONs; `offset` = where that wav starts in the recording |
| `keywords` | Words that stay yellow and pop in captions |
| `segments[]` | `id`, `src [a,b]`, `energy` (`high` = 3-word captions), `text`, `camera[]`, `sfx[]`, `cards[]` |
| `camera[]` | `{at, scale, fy?, to?, fy_to?, move?}`: a hard cut to a framing at `at`, optional linear push to `to`; `move` = eased 1 s reframe instead of a cut. Wide is 1.36; punch-ins 1.6–1.86 |
| `sfx[]` | `{file: impact-bass-1 \| impact-bass-2 \| whoosh-short, at, volume}`; the engine aligns the file's peak to `at`. Whooshes at seams and the end-card hit are automatic |
| `cards[]` | `{start, end, kicker, pill?, rows[]}` or `{type: "lowerthird", start, end}` |
| rows | `big {size, lines[[{t, at?, c?}]]}` mask-rise per word · `small {size, words[], italic?, quote?}` dim→lit per word · `stats {items[{num, at, unit, unit_at}]}` · `num {num, at, size, c, lead?, side[]}` · `list {items[], at, highlight, highlight_at}` · `chip {t, at}` · `foot {html, at}` |
| `end` | `{duration, quote? (html), box_title?, bullets[] (html), credit}` |

A word without `at` is on screen from its card's start. A card starting at video 0 is the thumbnail: fully drawn on frame 0.
