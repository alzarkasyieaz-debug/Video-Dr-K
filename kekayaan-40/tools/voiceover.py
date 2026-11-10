"""Generate the deep Malay voiceover with Meta's open MMS-TTS model (runs locally).

The narration is new editorial voiceover in a synthetic voice: it is NOT the voice of
@NakSeeHeart and does not imitate anyone. The text follows the infographic.

Each line is built from short phrases joined by deliberate pauses, then deepened:
pitch down ~4.7 semitones, slower delivery, warm low end, a little room, loudness to
-16 LUFS. Output: assets/voice/<id>.wav and assets/voice/meta.json (durations).

Run (needs torch, transformers, soundfile):  python tools/voiceover.py
"""
import json, pathlib, subprocess, sys

import numpy as np
import soundfile as sf
import torch
from transformers import AutoTokenizer, VitsModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "voice"
TMP = ROOT / ".voice-tmp"

MODEL = __import__("os").environ.get("MMS_MODEL_DIR", "facebook/mms-tts-zlm")  # Malay (local dir if set)
SEED = 40

# id: [(phrase, pause after in seconds)]
LINES = {
    "hook": [("selepas umur empat puluh tahun", 0.55), ("kekayaan sebenar", 0.35), ("adalah", 0.0)],
    # Ordinals are spoken inside the phrase: on their own the model slurs them.
    "p1": [("yang pertama kesihatan yang masih baik", 0.0)],
    "p2": [("yang kedua hati yang tenang", 0.0)],
    "p3": [("yang ketiga rezeki yang cukup", 0.3), ("dan berkat", 0.0)],
    "p4": [("yang keempat keluarga yang bahagia", 0.0)],
    "p5": [("yang kelima anak anak yang sihat", 0.0)],
    "p6": [("yang keenam sahabat yang ikhlass", 0.0)],  # spelt for a clear final "s"
    "p7": [("yang ketujuh hidup tanpa beban hutang", 0.0)],
    "p8": [("dan yang kelapan masa untuk mendekatkan diri kepada allah", 0.0)],
    "quote": [("bila usia semakin meningkat", 0.5), ("hidup yang sederhana", 0.3), ("tetapi tenang", 0.5),
              ("terasa jauh lebih berharga", 0.0)],
}

PITCH = 0.76    # resample factor: ~4.7 semitones down (deep)
TEMPO = 0.94    # overall a touch slower than the model's natural pace


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(exist_ok=True)
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = VitsModel.from_pretrained(MODEL)
    model.speaking_rate = 0.9
    model.noise_scale = 0.5
    sr = model.config.sampling_rate

    meta = {}
    for lid, phrases in LINES.items():
        parts, starts, pos = [], [], 0
        for k, (text, pause) in enumerate(phrases):
            torch.manual_seed(SEED + k)
            with torch.no_grad():
                wav = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
            # trim model silence at the edges
            idx = np.where(np.abs(wav) > 0.01)[0]
            if len(idx):
                wav = wav[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.08 * sr)]
            starts.append(round(pos / sr / TEMPO, 3))  # phrase start in output seconds
            parts.append(wav)
            parts.append(np.zeros(int(pause * sr), dtype=np.float32))
            pos += len(wav) + int(pause * sr)
        raw = TMP / f"{lid}.raw.wav"
        sf.write(raw, np.concatenate(parts), sr)

        out = OUT / f"{lid}.wav"
        # Deepen: lower pitch via asetrate, restore speed with atempo (net TEMPO),
        # warm low shelf, tame harshness, a small room, then loudness.
        chain = (
            f"asetrate={int(sr * PITCH)},aresample=44100,atempo={TEMPO / PITCH:.4f},"
            "highpass=f=60,equalizer=f=140:t=q:w=1.0:g=3.5,equalizer=f=3200:t=q:w=1.2:g=-2,"
            "aecho=0.8:0.5:38|61:0.12|0.08,"
            "acompressor=threshold=-20dB:ratio=3:attack=8:release=180,"
            "loudnorm=I=-16:TP=-1.5:LRA=7,apad=pad_dur=0.25"
        )
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", chain, "-ar", "44100", str(out)],
                       check=True)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                    "csv=p=0", str(out)], capture_output=True, text=True).stdout)
        meta[lid] = {"file": f"assets/voice/{lid}.wav", "duration": round(dur, 3), "starts": starts,
                     "text": " · ".join(p for p, _ in phrases)}
        print(lid, round(dur, 2), "s")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
