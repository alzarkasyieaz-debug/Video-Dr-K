# Video MP — lessons from the first two episodes

## Environment
- Drive downloads need the **Video-Dr-K** cloud environment (Default refuses `drive.usercontent.google.com`). The Drive connector returns base64, which is useless for video; use curl.
- Node does not use the proxy by itself: prefix whisper model downloads with `NODE_USE_ENV_PROXY=1`, or the CLI fails with `ENOTFOUND huggingface.co`.
- whisper large-v3 (3.1 GB) runs at about real time ÷ 2 on 4 CPUs; a 17-minute file takes too long. Transcribe only the MP's parts. `ggml-small.bin` can be fetched with curl into `~/.cache/hyperframes/whisper/models/` for quick context passes.
- `npx hyperframes transcribe` always writes `assets/source/transcript.json` (or `assets/transcript.json`): copy it before the next run.
- Rendering with the WebGL grade is about 1.3–2 frames/s here: 60 s ≈ 13 min, 89 s ≈ 19 min. Run it in the background.
- `*.mp4` is git-ignored at the repo root: `git add -f` the delivered MP4 and the `seg-*.mp4` clips (each well under 100 MB).

## Transcription fixes seen so far (Malay parliament audio)

| Whisper wrote | Correct |
| --- | --- |
| Titik Gantung | Titi Gantung |
| Aida | IADA |
| Jalapang, jelapan | jelapang |
| Pengesunan, pengazonan | Pengezonan |
| pesawat | pesawah |
| Perkaitan | berkaitan |
| babau ini | baru-baru ini |
| pembinaan padi | pembenihan padi |
| Timbalani … Betul | Timbalan Yang di-Pertua |
| Dato' Endi Petua / Datuk Indi Petua | Dato' Yang di-Pertua |
| Ali yang menghormat | Ahli Yang Berhormat |
| pump | pam |
| telahpun | telah pun |
| `small` model: "26 bilion" | RM2.6 bilion (large-v3; the parts summed to 2.6) |

A slice re-transcribed with an `initial prompt` (whisper-cli `--prompt "Puan Timbalan Yang di-Pertua, Dewan Rakyat."`) settles a doubtful phrase.

## Craft
- Broadcast 4K from Parliament is often SD-soft. Punch-ins above ~1.8× smear; keep the hero close-ups at 1.6–1.8.
- Kamar Khas footage is dim: grade with exposure +0.1, shadows +0.14.
- One loudness pass is not enough. Measure the rendered file; picking dense clips raised it from −16 to −13 LUFS. Fix it with `speech_volume`, not a post-process, so re-renders match.
- Long uppercase Montserrat lines wrap sooner than character counts suggest. Keep `small` rows to about 40 characters at 31–34 px and check them in snapshots.
- `line_unread` on a card that builds word by word with the speech is expected; keep it and say so in REVIEW.md.
