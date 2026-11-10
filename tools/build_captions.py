"""Generate compositions/captions.html from the edit decision list.

Caption text follows the creator's own burned-in captions (checked frame by
frame); word times come from whisper (v1, v2) or the burned-in captions (v3).
Times below are SOURCE seconds; CLIPS maps them onto the output timeline.
"""
import json, html, pathlib

# id: (source file, media in, media out, output start)
CLIPS = {
    "c1": ("nasihat-2", 56.24, 64.14, 0.00),
    "c2": ("nasihat-2", 0.25, 3.40, 7.90),
    "c3": ("nasihat-2", 8.36, 13.14, 11.05),
    "c4": ("nasihat-2", 32.90, 42.62, 15.83),
    "c5": ("nasihat-1", 0.28, 16.55, 25.55),
    "c6": ("nasihat-1", 16.55, 35.70, 41.82),
    "c8": ("nasihat-1", 53.55, 69.05, 60.97),
    "c7": ("nasihat-3", 0.45, 9.10, 77.27),
    "c9": ("nasihat-3", 52.24, 68.45, 85.92),
}

# (clip, source start, source end, text, words to highlight in gold)
GROUPS = [
    # c1 is the hook: it uses its own kinetic type, not this track.
    ("c2", 0.35, 1.89, "Siapa dalam dunia ni", []),
    ("c2", 1.89, 3.36, "tak nak bahagia?", ["bahagia?"]),
    ("c3", 8.40, 10.07, "Tetapi ukuran bahagia", ["bahagia"]),
    ("c3", 10.07, 11.41, "bagi setiap orang", []),
    ("c3", 11.42, 13.12, "ini berbeza-beza.", ["berbeza-beza."]),
    ("c4", 32.97, 35.60, "Tetapi bahagia yang sebenar", ["bahagia", "sebenar"]),
    ("c4", 35.60, 38.42, "apabila kita dapat", []),
    ("c4", 38.42, 40.40, "buat satu perkara itu", []),
    ("c4", 40.40, 42.60, "untuk Allah suka pada kita.", ["Allah", "suka"]),
    ("c5", 0.40, 2.75, "Berkongsi kehidupan dengan insan", ["kehidupan"]),
    ("c5", 2.76, 5.44, "yang Allah Taala takdirkan kepada kita", ["takdirkan"]),
    ("c5", 5.44, 7.46, "adalah satu pengalaman", []),
    ("c5", 7.48, 8.75, "untuk mengajar kita", []),
    ("c5", 8.75, 10.94, "erti syukur yang sebenar.", ["syukur"]),
    ("c5", 10.96, 13.21, "Allah Taala nak membentuk diri kita", ["membentuk"]),
    ("c5", 13.21, 14.48, "untuk mengaplikasi", []),
    ("c5", 14.48, 16.53, "makna sabar yang sebenar.", ["sabar"]),
    ("c6", 16.58, 20.12, "Setiap ujian dalam rumah tangga", ["ujian"]),
    ("c6", 20.12, 21.93, "adalah salah satu fasa", []),
    ("c6", 21.93, 24.82, "untuk kita lebih mengenali pasangan kita,", ["mengenali"]),
    ("c6", 24.84, 27.65, "untuk kita lebih menghargai pasangan kita.", ["menghargai"]),
    ("c6", 27.65, 29.18, "Mana mungkin pelayaran", ["pelayaran"]),
    ("c6", 29.18, 30.90, "sebuah rumah tangga", []),
    ("c6", 30.90, 33.00, "tidak ada pasang surutnya,", ["pasang", "surutnya,"]),
    ("c6", 33.02, 35.66, "tidak ada hujan dan panasnya.", ["hujan", "panasnya."]),
    ("c8", 53.62, 56.17, "Maka jangan pernah sesekali letih", ["letih"]),
    ("c8", 56.17, 57.93, "untuk mempertahankan", []),
    ("c8", 57.93, 59.64, "ikatan perkahwinan.", ["ikatan", "perkahwinan."]),
    ("c8", 59.64, 61.24, "Jangan pernah letih", ["letih"]),
    ("c8", 61.24, 63.60, "untuk menjaga hubungan perkahwinan,", ["menjaga"]),
    ("c8", 63.62, 65.66, "agar dia terus menjadi saham", ["saham"]),
    ("c8", 65.68, 67.56, "untuk kita membina pahala", ["pahala"]),
    ("c8", 67.56, 69.04, "bekal di akhirat.", ["akhirat."]),
    ("c7", 0.50, 2.50, "Syukur Allah Taala", ["Syukur"]),
    ("c7", 2.50, 5.50, "hadiahkan kita seorang pasangan", ["pasangan"]),
    ("c7", 5.50, 6.50, "untuk melengkapkan", ["melengkapkan"]),
    ("c7", 6.50, 9.00, "kelemahan dan kekhilafan kita.", []),
    # c9 52.25-58.00 ("Andai ada kekurangan...") is set as a full typographic card.
    ("c9", 58.00, 59.50, "InsyaAllah kita mampu", []),
    ("c9", 59.50, 61.50, "mencipta bahagia dengan pasangan", ["bahagia"]),
    ("c9", 61.50, 64.75, "kiriman Tuhan yang Allah Taala takdirkan", ["takdirkan"]),
    ("c9", 64.75, 67.50, "bersama kita hingga akhir hayat kita.", ["akhir", "hayat"]),
    ("c9", 67.70, 68.40, "Percayalah.", ["Percayalah."]),
]


def out_time(clip, t):
    _, m_in, _, start = CLIPS[clip]
    return round(start + (t - m_in), 3)


def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    groups = []
    for i, (clip, s, e, text, hi) in enumerate(GROUPS):
        a, b = out_time(clip, s), out_time(clip, e)
        words = text.split()
        n = len(words)
        # Type reveal: a quick left-to-right ripple so the whole line reads early.
        span = min(0.6, (b - a) * 0.35)
        groups.append({
            "id": f"cap{i}",
            "start": a,
            "end": b,
            "words": [{"t": w, "hi": w in hi, "at": round(a + span * k / n, 3)} for k, w in enumerate(words)],
        })

    markup = []
    for g in groups:
        spans = " ".join(
            f'<span class="w{" hi" if w["hi"] else ""}">{html.escape(w["t"])}</span>' for w in g["words"]
        )
        markup.append(f'    <div class="cap" id="{g["id"]}"><div class="cap-line">{spans}</div></div>')

    end = max(g["end"] for g in groups)
    timing = json.dumps([{"id": g["id"], "start": g["start"], "end": g["end"], "at": [w["at"] for w in g["words"]]} for g in groups])

    doc = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    #root .cap {{
      position: absolute; left: 0; right: 0; top: 1130px;
      padding: 0 130px; text-align: center; opacity: 0; overflow: visible;
    }}
    #root .cap-line {{
      font-family: "Montserrat", sans-serif; font-weight: 700; font-size: 54px;
      line-height: 1.22; color: #fbf6ec; letter-spacing: 0.005em;
      text-shadow: 0 2px 18px rgba(6, 12, 24, 0.85), 0 0 2px rgba(6, 12, 24, 0.9);
    }}
    #root .w {{ display: inline-block; opacity: 0; }}
    #root .w.hi {{ color: #f0cd84; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(markup)}
  </div>
  <script>
    (function () {{
      const G = {timing};
      const tl = gsap.timeline({{ paused: true }});
      G.forEach((g) => {{
        const el = "#" + g.id;
        const words = document.querySelectorAll(el + " .w");
        tl.set(el, {{ opacity: 1, visibility: "visible" }}, g.start - 0.05);
        words.forEach((w, k) => {{
          tl.fromTo(w, {{ opacity: 0, y: 14, scale: 0.96 }},
            {{ opacity: 1, y: 0, scale: 1, duration: 0.32, ease: "power2.out" }}, g.at[k] - 0.05);
        }});
        tl.to(el, {{ opacity: 0, duration: 0.14, ease: "power2.in" }}, g.end - 0.14);
        tl.set(el, {{ opacity: 0, visibility: "hidden" }}, g.end);
      }});
      tl.set({{}}, {{}}, {end:.2f});
      window.__timelines["captions"] = tl;
    }})();
  </script>
</template>
"""
    (root / "compositions" / "captions.html").write_text(doc)
    print("groups", len(groups), "last end", end)


if __name__ == "__main__":
    main()
