# edit.json — Ceramah Politik project file

One file describes the whole edit. The scripts read it from the project root.

```jsonc
{
  "style": "ceramah-politik",
  "title": "…",                      // <title> of index.html
  "source": "/abs/path/speech.mp4",  // the full recording (kept out of the repo)
  "lang": "ms",
  "end_card": 3.8,                   // seconds of end card after the last word
  "bug": "PRN MELAKA · CERAMAH PERPADUAN",   // "·" renders gold
  "speaker": { "name": "", "role": "…" },     // name stays empty until confirmed
  "spoken": { "3.6": "tiga perpuluhan enam", "SAW": "sallallahu alaihi wasallam" },  // alignment only
  "keywords": ["rakyat", "perpaduan"],        // caption words that pop gold (lowercase)

  "clips": [                         // play back to back, in this order
    { "id": "a", "in": 960.66, "out": 967.00,         // seconds in the source
      "head_y": 900,                                   // optional, default 940
      "zoom": { "type": "push", "from": 1.58, "to": 1.78, "pow": 1.2,
                "punch": { "at": { "word": "tuntutan" }, "add": 0.08 } },   // punch optional
      "text": "Exact words as displayed, one token per spoken word." }
  ],

  "scenes": [ { "id": "hook", "overlays": [ … ] } ],  // one composition file per scene
  "sfx": [ { "file": "impact-bass-1", "at": { "word": "rakyat", "offset": 0.03 }, "volume": 0.32 } ],
  "music": { "cues": [ { "file": "assets/audio/cues/cue1.wav", "at": 0, "length": 24,
                         "seconds": 30, "seed": 11, "prompt": "…" } ],
             "climax_scene": "climax" }
}
```

## Time anchors (`at`, `until`, `end`, …)

| Form | Meaning |
|---|---|
| `12.5` | absolute output seconds |
| `{ "word": "perpaduan", "after": 6.3, "offset": -0.2 }` | start of the first caption word matching (case-insensitive, punctuation ignored) at or after `after` s, plus `offset` |
| `{ "cut": 2, "offset": 0.03 }` | the 2nd cut (start of the 3rd clip) |
| `{ "speech_end": true, "offset": -0.95 }` | end of the last clip |

Prefer word anchors: when clips are re-cut, cards follow the speech.

## Overlays

```jsonc
{ "type": "headline", "lines": [ { "text": "POLITIK" }, { "text": "PERSEPSI", "gold": true } ],
  "question": { "text": "YANG RUGI SIAPA?", "at": {…}, "stagger": 0.24 },
  "answer": { "lead": "YANG RUGI:", "word": "RAKYAT.", "at": {…} }, "end": 6.98 }

{ "type": "keypoint", "kicker": "POINT 01 · ISU UTAMA", "at": {…}, "hold": 4.35,
  "lines": [ { "text": "PERPADUAN", "size": 120, "gold": true }, { "text": "DUA PARTI TERBESAR" } ] }

{ "type": "versus", "left": "UMNO", "right": "PAS", "join": "+", "left_at": {…}, "right_at": {…}, "hold": 1.8 }

{ "type": "stat", "kicker": "POINT 02 · …", "start": 21.3, "end": 36.55,
  "rows": [ { "label": "UMNO", "value": "3.6", "unit": "JUTA", "at": {…} } ],
  "divider_at": {…}, "total": { "label": "GABUNGAN", "value": "4.6", "unit": "JUTA", "at": {…} },
  "source": "Angka seperti disebut penceramah (minit 02:23–02:38). Belum disahkan secara bebas." }

{ "type": "numbered", "kicker": "POINT 03 · …", "start": 36.7, "end": 59.95,
  "cards": [ { "num": "01", "title": "MEMBINA MASJID", "sub": "Asas {kekuatan} negara", "sub_big": true,
               "highlight_at": {…}, "at": {…}, "until": {…} } ] }      // last card runs to "end"

{ "type": "slam", "kicker": "POINT 04 · KEMUNCAK", "lead_clip": "e", "lead_words": 6,
  "big": "TUNTUTAN", "big_at": {…}, "second": "ALLAH SWT", "second_at": {…},
  "lines": [ { "text": "MENYATUKAN DUA KELOMPOK", "at": {…}, "stagger": 0.3 } ], "end": 70.3 }

{ "type": "words", "kicker": "POINT 05 · MESEJ PENUTUP", "end": { "speech_end": true, "offset": -0.95 },
  "lines": [ { "size": 124, "gold": true, "words": [ { "text": "PERPADUAN", "at": {…} } ] } ] }

{ "type": "final", "kicker": "MESEJ PENUTUP", "lines": [ "“INI BUKAN *PERPADUAN*", "UNTUK POLITIK", "*SEMATA-MATA.”*" ] }
```

`*word*` in `final` lines renders gold. Card copy is UPPERCASE and at most 6 words a line.
Type sizes are fixed by the style: change words, not sizes.

## SFX files and peaks

`build.py` lands each SFX's peak on its `at` time. Known peaks: impact-bass-1 0.073 s, whoosh / whoosh-short 0.162 s,
whoosh-cinematic 2.503 s, riser 3.472 s. Volumes in the reference edit: whooshes 0.20–0.30,
impacts 0.28–0.55, riser 0.18. Use one impact per card at most, and one riser→impact for the whole film.
