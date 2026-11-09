---
name: ceramah-politik
description: "Ceramah Politik" style — turn a long political speech / ceramah recording into a 60–90 s vertical (9:16) premium political-documentary edit with HyperFrames: real quotes only, tracked digital camera, navy-and-gold broadcast cards, kinetic Malay captions, original or licensed score ducked under the voice, SRT + key points + headlines + caption deliverables. Use when the person asks for "style Ceramah Politik", a ceramah/ucapan/pidato political speech edit, or a video "macam video Dr K / Perpaduan UMNO-PAS".
---

# Ceramah Politik

A HyperFrames style for political speeches. One look, one story shape, one pipeline. The reference
edit is this repository's own video (`edit.json`, `deliverables/perpaduan-umno-pas-9x16.mp4`).
Read `/hyperframes` and `/media-use` first; this skill only adds the style and its pipeline.

## Non-negotiables (authenticity first)

1. **Real quotes only.** Every clip is a complete sentence cut on a measured pause. Never splice words into
   a new sentence, never reorder clauses inside a clip, never invent dialogue or crowd reactions.
2. **One out-of-order clip at most**: the hook. Everything after it runs in source order.
3. **A word the transcription passes disagree on is not shown.** Cut around it, or flag it in the
   delivery notes. Never guess a word into a caption.
4. **Numbers and claims on cards carry a source label**: "Angka seperti disebut penceramah (minit mm:ss). Belum disahkan secara bebas."
   Contested factual passages (audits, scandals, seat arithmetic) don't become cards unless the person verifies them.
5. **Speaker name only when the person confirms it.** `speaker.name` stays empty otherwise (the card hides it).
6. Cards and titles never cover the face. The camera puts the head at y≈940 px. Cards sit above it (y 178–700),
   captions below it (bottom edge at 1302 px), and all text stays inside 168–1330 px.

## The look

| Element | Spec |
|---|---|
| Canvas | 1080×1920, 30 fps, 60–90 s, H.264 MP4 |
| Palette | navy `#0a1630` / deep `#050b1a`, gold `#d9a93a` / bright `#f4c95d`, white, active caption word `#ffd84a` |
| Type | Anton (headlines, uppercase), Bebas Neue (kickers, labels, letter-spaced), Montserrat 600–800 (subs, captions). Fonts ship in `assets/fonts/` |
| Grade | `media-treatment`: `deep-contrast` 0.45, exposure +0.06, highlights −0.30, shadows +0.14, temperature −0.08, saturation −0.05, vignette 0.36, grain 0.12 |
| Shade | navy gradient top 520 px, black-navy bottom 900 px (legibility); per-card dim panel 0–860 px |
| Bug | top-left at y 178: gold bar + Bebas 34 px `EVENT · CERAMAH TOPIC`, on for the whole speech |
| Cuts | 3-frame dip to 45% black + diagonal gold light sweep (0.85 s) + whoosh (rotate whoosh-cinematic / whoosh-short / whoosh) |
| Captions | 3–4 words per group, Montserrat 800 70 px, 9 px black stroke, translucent navy box. Word in: opacity 0→1, scale .95→1 over .15 s. Active word yellow; keywords gold with pop 1→1.12→1 over .25 s |
| Camera | HOG speaker tracking, smoothed. Per clip: `push` (slow push / power curve) or `ease` (controlled zoom in/out), optional `punch` on a word. Max 1.8×, edges never show |
| End | navy radial fade, final quote card (Anton 112 px, gold keywords), name/role, gold dust, fade to black. `end_card` ≈ 3.8 s |

### Overlay types (`edit.json` → `scenes[].overlays[]`; see `references/edit-json.md`)

| type | Use for | Motion |
|---|---|---|
| `headline` | the hook, already on screen at frame 0 (thumbnail) | bold scale-in, masked slide-up, word reveal of a question, answer word with gold highlight sweep |
| `keypoint` | a POINT card (kicker + 2–3 lines, ≤ 6 words), held 2–5 s | dim, gold line draws, word-by-word blur→sharp stagger, blur exit |
| `versus` | two names / parties / sides joining | boxes slide in from each side with motion blur, `+` pops |
| `stat` | figures said in the speech, staged row by row, plus a total | rows land on their spoken number; total scale-in + highlight sweep; source label |
| `numbered` | 01 / 02 argument cards under one kicker | masked clip-path title reveal, sub slide-up, optional `{word}` highlight + pop |
| `slam` | the climax | lead line word-timed (Bebas), giant gold word slams in (1.45→1 + blur), gold glow, riser→impact |
| `words` | closing line, each word on its spoken time | per-word blur-in on the speech |
| `final` | end card quote + speaker | navy fade, staggered reveal, dust, fade to black |

## Story shape (adapt to what the speech really contains)

| Beat | Time | Content | Overlay |
|---|---|---|---|
| Hook | 0–6 s | the most quotable self-contained line (question → answer is ideal) | `headline` |
| Issue | 6–20 s | what the speech is about | `keypoint` (+ `versus`) |
| Evidence | 15–35 s | figures or facts the speaker states | `stat` with source label |
| Argument | 35–60 s | the 2 reasons / the precedent | `numbered` |
| Climax | 60–70 s | the most passionate sentence | `slam`, close-up push + punch, riser→impact |
| Close | 70–85 s | the speaker's real closing message | `words` + `final` |

Pick 3–5 key points; one card per 6–8 s; never two cards at once.

## Pipeline

Scripts live in `.claude/skills/ceramah-politik/scripts/` and all read `<project>/edit.json`.
Python deps (one venv): `torch transformers soundfile numpy scipy "opencv-python-headless<5"`.
Network: Hugging Face (`huggingface.co`, `us.aws.cdn.hf.co`, `cas-bridge.xethub.hf.co`, `cdn-lfs.hf.co`) for models.
A Drive source needs `drive.usercontent.google.com`. Node fetches need `NODE_USE_ENV_PROXY=1` behind the proxy.

0. **New project**: `npx hyperframes init <dir> --skip-skills --skill=hyperframes`, then copy
   `.claude/skills/ceramah-politik/assets/fonts/*.woff2` into `<dir>/assets/fonts/` (Anton and Bebas Neue, SIL OFL).
1. **Get the source** into a folder outside the project. For a Google Drive share link:
   `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t" -o src.mp4`.
2. **Transcribe the whole speech** (Malay is not English: never `.en`):
   `npx hyperframes transcribe speech16k.wav --engine whisper --model medium --language ms --json`.
   Download the ggml model first with curl into `~/.cache/hyperframes/whisper/models/` if the CLI can't reach Hugging Face.
   Also map loudness (`astats`) to find the energetic passages.
3. **Choose the clips** (story shape above). Re-transcribe each candidate window with `--model large-v3` and
   compare it with the medium pass. Where they disagree, run a third pass on a tight window; still unclear → cut around it.
   Set `in`/`out` on measured silences (50 ms RMS frames below about −40 dB), about 0.15 s before the first word.
4. **Write `edit.json`**: clips with their exact display text, `spoken` forms for numbers/honorifics,
   keywords, scenes and overlays anchored to spoken words, SFX, music cues. Start from `references/edit-json.md`
   or this repo's `edit.json`.
5. `python prep.py .` cuts `assets/footage/clip-*.mp4` and cleans the voice (−15 LUFS).
6. `python align.py .` force-aligns the text and writes `data/words.json` on the output timeline.
7. `python track.py .` tracks the speaker and writes `data/camera.json`.
8. **Music**: HeyGen catalog first (`/media-use`, `npx hyperframes auth status`; the device login is
   `NODE_USE_ENV_PROXY=1 npx hyperframes auth login --device`). Otherwise, with the person's OK, run
   `python music.py . --generate` for original MusicGen cues (4 cues: dark → building → climax → resolution, about 17 min each on CPU;
   the weights are CC-BY-NC). Then `python music.py .` assembles `assets/audio/score.m4a` plus the ducking lane.
   SFX: copy `impact-bass-1 whoosh-cinematic whoosh whoosh-short riser` from `/media-use` `audio/assets/sfx/` into `assets/sfx/`.
9. `python3 build.py .` writes `index.html` and `compositions/`. Then apply the grade:
   `npx hyperframes media-treatment --selector video --grading '<Grade JSON from the table above>' --apply`.
10. `npm run check`: 0 errors. `composition_file_too_large` on captions.html is expected.
    Snapshot the hook, every card and the end card; read them. Fix any card touching the face by changing `head_y` or the card text, never by shrinking type.
11. Open the Studio preview (`npx hyperframes preview --background`), then render:
    `npx hyperframes render --quality delivery --output renders/<slug>.mp4`.
    Measure with `npx hyperframes audio <mp4> --json` (target −14 to −15 LUFS, true peak ≤ −1 dBTP).
12. **Deliverables**: `python srt.py .`, then `deliverables/RINGKASAN.md` with 3–5 key points (title ≤ 6 words,
    summary ≤ 15 words, supporting quote, source timestamp, animation), 5 headlines, a social caption, the editing timeline,
    the QC table and the words needing human review; plus `REVIEW.md`. Copy the MP4 to `deliverables/`.

Re-running `build.py` overwrites `index.html` and `compositions/`. Hand edits made in Studio belong in
`edit.json` (or the engine) if they should survive a rebuild.
