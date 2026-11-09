#!/usr/bin/env python3
"""Write the graphics scene files. Shared CSS and helpers live here so every scene matches.

Times in each scene are LOCAL to that scene; comments give the spoken word they land on.
Edit copy or timing here and re-run:  python3 scripts/build_scenes.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CSS = """
    @font-face {
      font-family: "Anton";
      src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2");
      font-weight: 400;
    }
    #root { position: absolute; inset: 0; background: transparent; font-family: "Montserrat", sans-serif; color: #fff; }
    .blk { position: absolute; left: 72px; top: 196px; width: 936px; height: 300px; }
    .kicker { font-weight: 700; font-size: 28px; letter-spacing: 0.14em; color: #d6ac52; text-transform: uppercase;
      display: flex; align-items: center; gap: 16px; white-space: nowrap; }
    .kicker i { display: block; width: 64px; height: 4px; background: #d6ac52; transform-origin: 0 50%; }
    .pill { margin-left: auto; font-weight: 600; font-size: 28px; letter-spacing: 0.04em; color: #fff;
      border: 2px solid rgba(214, 172, 82, 0.8); border-radius: 6px; padding: 2px 10px; }
    .big { margin-top: 12px; font-family: "Anton", sans-serif; font-size: 100px; line-height: 1;
      text-transform: uppercase; text-shadow: 0 6px 28px rgba(0, 0, 0, 0.6); }
    .line { display: block; overflow: hidden; padding-top: 4px; }
    .w { display: inline-block; }
    .small { margin-top: 14px; font-weight: 800; font-size: 38px; text-transform: uppercase; letter-spacing: 0.01em; }
    .small .w { opacity: 0.25; }
    .gold { color: #d6ac52; }
    .yel { color: #ffd447; }
"""

JS_HEAD = """    const tl = gsap.timeline({ paused: true });
    const reveal = (sel, t) => tl.fromTo(sel, { yPercent: 105 }, { yPercent: 0, duration: 0.45, ease: "power4.out" }, t);
    const kick = (rule, t) => tl.fromTo(rule, { scaleX: 0 }, { scaleX: 1, duration: 0.6, ease: "expo.out" }, t);
    const light = (sel, t) => tl.to(sel, { opacity: 1, duration: 0.1, ease: "none" }, t);
    const blurIn = (sel, t) => tl.fromTo(sel, { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, t);
    const out = (sel, t) => tl.to(sel, { opacity: 0, filter: "blur(8px)", duration: 0.2, ease: "power2.in" }, t);
"""


def scene(cid, extra_css, markup, js, root_attrs=""):
    return f"""<template>
  <style>{CSS}{extra_css}  </style>
  <div id="root" data-composition-id="{cid}" data-width="1080" data-height="1920"{root_attrs}>
{markup}
  </div>
  <script>
{JS_HEAD}{js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


def write(name, text):
    with open(os.path.join(ROOT, "compositions", name), "w") as f:
        f.write(text)


# ── A · hook (0–8.28) ────────────────────────────────────────────────────────────
write("hook.html", scene("hook", """
    #h-title { margin-top: 16px; font-size: 96px; line-height: 1.02; }
    #lt-name { font-family: "Anton", sans-serif; font-size: 66px; line-height: 1.12; text-transform: uppercase; }
    #lt-seat { font-weight: 600; font-size: 36px; color: #e8e8e8; }
    #lt-bar { position: absolute; left: 0; top: 0; width: 8px; height: 196px; background: #d6ac52; transform-origin: 50% 0; }
    #lt-text { position: absolute; left: 34px; top: 0; width: 900px; }
""", """    <div id="h-blk" class="blk clip" data-start="0" data-duration="4.3" data-track-index="0">
      <div class="kicker"><i id="h-rule"></i><span>Kamar Khas &nbsp;|&nbsp; Dewan Rakyat</span></div>
      <h1 id="h-title" class="big">
        <span class="line" data-layout-allow-overflow><span class="w">Pengezonan jelapang</span></span>
        <span class="line" data-layout-allow-overflow><span class="w">padi</span> <span class="w yel">Perak Tengah</span></span>
      </h1>
    </div>
    <div id="lt" class="blk clip" data-start="4.35" data-duration="3.85" data-track-index="1">
      <div id="lt-bar"></div>
      <div id="lt-text">
        <div class="line" data-layout-allow-overflow><span id="lt-loc" class="w kicker">Kamar Khas &nbsp;|&nbsp; Parlimen Malaysia</span></div>
        <div class="line" data-layout-allow-overflow><span id="lt-name" class="w" data-var-text="mp-name">Hj. Muhammad Ismi bin Mat Taib</span></div>
        <div class="line" data-layout-allow-overflow><span id="lt-seat" class="w" data-var-text="mp-seat">Ahli Parlimen Parit, Perak</span></div>
      </div>
    </div>""", """
    // Frame 0 is the thumbnail: headline already on screen; only the rule draws.
    tl.fromTo("#h-rule", { scaleX: 0.2 }, { scaleX: 1, duration: 0.7, ease: "expo.out" }, 0);
    out("#h-blk", 4.05);
    tl.fromTo("#lt-bar", { scaleY: 0 }, { scaleY: 1, duration: 0.5, ease: "expo.out" }, 4.35);
    tl.fromTo(["#lt-loc", "#lt-name", "#lt-seat"], { yPercent: 110 }, { yPercent: 0, duration: 0.6, stagger: 0.12, ease: "power4.out" }, 4.45);
    out("#lt", 7.95);""", root_attrs=""" data-composition-variables='[{"id":"mp-name","type":"string","label":"Nama Ahli Parlimen","default":"Hj. Muhammad Ismi bin Mat Taib"},{"id":"mp-seat","type":"string","label":"Jawatan / kawasan","default":"Ahli Parlimen Parit, Perak"}]'"""))

# ── B · facts (local = video − 8.28 = source − 23.97 + … ) ───────────────────────
write("facts.html", scene("facts", """
    .stats { margin-top: 14px; display: flex; gap: 56px; align-items: flex-end; }
    .num { font-family: "Anton", sans-serif; font-size: 118px; line-height: 1; color: #d6ac52;
      text-shadow: 0 0 30px rgba(214, 172, 82, 0.35), 0 6px 24px rgba(0, 0, 0, 0.6); }
    .unit { margin-top: 4px; font-weight: 800; font-size: 30px; letter-spacing: 0.06em; text-transform: uppercase; }
    #f-foot { white-space: nowrap; margin-top: 16px; font-weight: 700; font-size: 30px; color: #e8e8e8; }
    #f-foot b { color: #ffd447; font-weight: 800; }
    #z-l1 { font-size: 104px; }
    .swap { position: relative; height: 56px; margin-top: 16px; }
    .swap > div { position: absolute; left: 0; top: 0; width: 936px; white-space: nowrap;
      font-weight: 800; font-size: 36px; text-transform: uppercase; }
    .swap .w { opacity: 0.25; }
""", """    <div id="f-blk" class="blk clip" data-start="1.4" data-duration="11.65" data-track-index="0">
      <div class="kicker"><i id="f-rule"></i><span>Fakta daripada ucapan</span><span class="pill">Petikan ucapan</span></div>
      <div class="stats">
        <div><div id="f-n1" class="num">15,392.8</div><div id="f-u1" class="unit">hektar tanah sawah</div></div>
        <div><div id="f-n2" class="num">9,650</div><div id="f-u2" class="unit">lot</div></div>
      </div>
      <div id="f-foot">Kawasan strategik &nbsp;·&nbsp; seliaan <b>IADA Seberang Perak</b></div>
    </div>
    <div id="z-blk" class="blk clip" data-start="13.0" data-duration="11.17" data-track-index="1">
      <div class="kicker"><i id="z-rule"></i><span id="z-kick">Sudah tiba masanya</span></div>
      <div id="z-l1" class="big">
        <span class="line" data-layout-allow-overflow><span id="z-w1" class="w">Zon padi</span> <span id="z-w2" class="w gold">Bota Kiri</span></span>
      </div>
      <div class="swap">
        <div id="z-s1"><span id="z-a1" class="w">Dimasukkan</span> <span id="z-a2" class="w">kategori</span> <span id="z-a3" class="w yel">jelapang padi</span></div>
        <div id="z-s2"><span class="w" id="z-b0" style="opacity:1;color:#d6ac52">Seperti</span> <span id="z-b1" class="w">Krian</span> · <span id="z-b2" class="w">Sungai Manik</span> · <span id="z-b3" class="w">Seberang Perak</span></div>
      </div>
    </div>""", """
    // Stats: numbers land on the spoken figures.
    kick("#f-rule", 1.4);
    tl.fromTo("#f-n1", { opacity: 0, scale: 1.25, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", transformOrigin: "0% 100%" }, 1.52); // 15,392.8
    blurIn("#f-u1", 3.72); // hektar
    tl.fromTo("#f-n2", { opacity: 0, scale: 1.25, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", transformOrigin: "0% 100%" }, 6.6); // 9,650
    blurIn("#f-u2", 8.19); // lot
    blurIn("#f-foot", 9.25); // kawasan strategik
    out("#f-blk", 12.8);

    // Bota Kiri demand.
    kick("#z-rule", 13.03); // sudah tiba masanya
    blurIn("#z-kick", 13.05);
    reveal("#z-w1", 14.55); // zon padi
    reveal("#z-w2", 15.14); // Bota Kiri
    tl.set("#z-s2", { opacity: 0 }, 0);
    light("#z-a1", 16.26); // dimasukkan
    light("#z-a2", 17.52); // kategori
    light("#z-a3", 18.73); // jelapang padi
    tl.to("#z-s1", { opacity: 0, duration: 0.15, ease: "power2.in" }, 19.8);
    tl.fromTo("#z-s2", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "power2.out" }, 19.93); // seperti
    light("#z-b1", 21.18); // Krian
    light("#z-b2", 21.75); // Sungai Manik
    light("#z-b3", 22.96); // Seberang Perak
    out("#z-blk", 23.95);"""))

# ── C · problems (local = video − 32.45) ────────────────────────────────────────
write("problems.html", scene("problems", """
    #p-title { font-size: 92px; }
    #p-loc { margin-top: 14px; font-size: 32px; white-space: nowrap; }
    #q-big { margin-top: 6px; display: flex; align-items: flex-end; gap: 22px; }
    #q-lebih { font-family: "Anton", sans-serif; font-size: 64px; line-height: 1.2; text-transform: uppercase; }
    #q-num { font-family: "Anton", sans-serif; font-size: 170px; line-height: 0.95; color: #ffd447;
      text-shadow: 0 0 34px rgba(255, 212, 71, 0.35), 0 6px 24px rgba(0, 0, 0, 0.6); }
    #q-quote { margin-top: 10px; font-weight: 700; font-style: italic; font-size: 36px; color: #f2f2f2; }
    #q-quote .w { opacity: 0.25; }
    #r-title { font-size: 104px; }
""", """    <div id="p-blk" class="blk clip" data-start="0.1" data-duration="11.15" data-track-index="0">
      <div class="kicker"><i id="p-rule"></i><span>Masalah pesawah &nbsp;·&nbsp; soalan susulan</span></div>
      <div id="p-title" class="big">
        <span class="line" data-layout-allow-overflow><span id="p-w1" class="w">Benih padi</span></span>
        <span class="line" data-layout-allow-overflow><span id="p-w2" class="w yel">punca</span> <span id="p-w3" class="w yel">penyakit</span></span>
      </div>
      <div id="p-loc" class="small"><span id="p-l1" class="w">Titi Gantung</span> · <span id="p-l2" class="w">Parit</span> · <span id="p-l3" class="w">seluruh Perak Tengah</span></div>
    </div>
    <div id="q-blk" class="blk clip" data-start="11.35" data-duration="7.55" data-track-index="1">
      <div class="kicker"><i id="q-rule"></i><span>Hasil padi</span><span class="pill">Petikan ucapan</span></div>
      <div id="q-big"><span id="q-lebih">Lebih</span><span id="q-num">50%</span></div>
      <div id="q-quote">“…<span id="q-w1" class="w">hasil padi</span> <span id="q-w2" class="w">yang amat</span> <span id="q-w3" class="w">mengecewakan</span>”</div>
    </div>
    <div id="r-blk" class="blk clip" data-start="19.0" data-duration="4.6" data-track-index="2">
      <div class="kicker"><i id="r-rule"></i><span>Antara puncanya</span></div>
      <div id="r-title" class="big">
        <span class="line" data-layout-allow-overflow><span id="r-w1" class="w gold">Saliran</span></span>
        <span class="line" data-layout-allow-overflow><span id="r-w2" class="w">&amp; benih padi</span></span>
      </div>
    </div>""", """
    kick("#p-rule", 0.1);
    reveal("#p-w1", 0.1); // benih padi
    reveal("#p-w2", 2.06); // punca
    reveal("#p-w3", 3.4); // penyakit
    light("#p-l1", 6.57); // Titi Gantung
    light("#p-l2", 7.9); // Parit
    light("#p-l3", 9.15); // seluruh Perak Tengah
    out("#p-blk", 11.05);

    kick("#q-rule", 11.35);
    blurIn("#q-lebih", 11.42); // lebih
    tl.fromTo("#q-num", { opacity: 0, scale: 1.3, filter: "blur(10px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.4, ease: "expo.out", transformOrigin: "0% 100%" }, 12.38); // 50%
    light("#q-w1", 14.3); // hasil padi
    light("#q-w2", 15.86); // yang amat
    light("#q-w3", 17.16); // mengecewakan
    out("#q-blk", 18.7);

    kick("#r-rule", 19.0); // antara puncanya
    reveal("#r-w1", 20.88); // saliran
    reveal("#r-w2", 22.18); // keduanya … benih padi
    out("#r-blk", 23.38);"""))

# ── D · proposals (local = video − 56.09) ───────────────────────────────────────
write("proposals.html", scene("proposals", """
    .row { position: absolute; left: 0; width: 936px; height: 44px; display: flex; align-items: center;
      background: rgba(8, 26, 50, 0.72); border-left: 4px solid #d6ac52; }
    .row .n { width: 64px; text-align: center; font-family: "Anton", sans-serif; font-size: 32px; color: #d6ac52; }
    .row .t { font-weight: 800; font-size: 30px; text-transform: uppercase; white-space: nowrap; }
    #l-r1 { top: 56px; } #l-r2 { top: 106px; } #l-r3 { top: 156px; } #l-r4 { top: 206px; } #l-r5 { top: 256px; }
    #h-big { font-size: 100px; }
    #h-done { margin-top: 18px; display: inline-block; font-weight: 800; font-size: 30px; text-transform: uppercase;
      color: #081a32; background: #ffd447; border-radius: 6px; padding: 6px 14px; }
""", """    <div id="l-blk" class="blk clip" data-start="0.1" data-duration="6.95" data-track-index="0">
      <div class="kicker"><i id="l-rule"></i><span>Cadangan Ahli Parlimen</span><span class="pill">Petikan ucapan</span></div>
      <div id="l-r1" class="row"><div class="n">01</div><div class="t">Insentif khas untuk petani</div></div>
      <div id="l-r2" class="row"><div class="n">02</div><div class="t">Pusat pembenihan padi Titi Gantung</div></div>
      <div id="l-r3" class="row"><div class="n">03</div><div class="t">Infrastruktur pengairan</div></div>
      <div id="l-r4" class="row"><div class="n">04</div><div class="t">Teknologi pertanian pintar</div></div>
      <div id="l-r5" class="row"><div class="n">05</div><div class="t">Minat golongan muda</div></div>
    </div>
    <div id="h-blk" class="blk clip" data-start="7.05" data-duration="7.5" data-track-index="1">
      <div class="kicker"><i id="h-rule"></i><span>Cadangan 01 &nbsp;·&nbsp; insentif khas</span></div>
      <div id="h-big" class="big">
        <span class="line" data-layout-allow-overflow><span id="h-w1" class="w">Harga lantai</span> <span id="h-w2" class="w yel">stabil</span></span>
      </div>
      <div class="small"><span id="h-s1" class="w">Pulangan adil</span> <span id="h-s2" class="w">&amp; lumayan</span></div>
      <div id="h-done">✓ Telah pun dilaksanakan baru-baru ini</div>
    </div>""", """
    kick("#l-rule", 0.1);
    tl.fromTo(["#l-r1", "#l-r2", "#l-r3", "#l-r4", "#l-r5"],
      { opacity: 0, x: -36, clipPath: "inset(0% 100% 0% 0%)" },
      { opacity: 1, x: 0, clipPath: "inset(0% 0% 0% 0%)", duration: 0.5, stagger: 0.07, ease: "power4.out" }, 0.25); // saya mencadangkan
    tl.to(["#l-r2", "#l-r3", "#l-r4", "#l-r5"], { opacity: 0.5, duration: 0.2, ease: "power2.out" }, 1.1); // pertama
    tl.fromTo("#l-r1", { backgroundColor: "rgba(8, 26, 50, 0.72)" }, { backgroundColor: "rgba(214, 172, 82, 0.35)", duration: 0.2, ease: "power2.out" }, 1.1);
    out("#l-blk", 6.85);

    kick("#h-rule", 7.05); // menetapkan
    reveal("#h-w1", 8.3); // harga lantai
    reveal("#h-w2", 9.2); // stabil
    light("#h-s1", 10.78); // pulangan adil
    light("#h-s2", 11.77); // lumayan
    tl.fromTo("#h-done", { opacity: 0, scale: 0.85 }, { opacity: 1, scale: 1, duration: 0.3, ease: "back.out(1.6)", transformOrigin: "0% 50%" }, 12.28); // telah pun dilaksanakan
    out("#h-blk", 14.35);"""))

# ── E · climax (local = video − 70.71) ──────────────────────────────────────────
write("climax.html", scene("climax", """
    #k-big { font-size: 96px; }
    #s-row { margin-top: 2px; display: flex; align-items: flex-end; gap: 26px; }
    #s-num { font-family: "Anton", sans-serif; font-size: 190px; line-height: 0.95; color: #d6ac52;
      text-shadow: 0 0 40px rgba(214, 172, 82, 0.45), 0 6px 28px rgba(0, 0, 0, 0.6); }
    #s-lbl { padding-bottom: 18px; font-weight: 800; font-size: 34px; line-height: 1.2; text-transform: uppercase; }
    #s-lbl .w { opacity: 0.25; }
""", """    <div id="k-blk" class="blk clip" data-start="0.1" data-duration="6.55" data-track-index="0">
      <div class="kicker"><i id="k-rule"></i><span>Harapan</span></div>
      <div class="small" style="margin-top:10px;font-size:31px;white-space:nowrap"><span id="k-s1" class="w">Cadangan ini</span> <span id="k-s2" class="w">diberi perhatian</span> <span id="k-s3" class="w">kementerian</span></div>
      <div id="k-big" class="big">
        <span class="line" data-layout-allow-overflow><span id="k-w1" class="w">Pertanian negara</span></span>
        <span class="line" data-layout-allow-overflow><span id="k-w2" class="w gold">lebih berdaya maju</span></span>
      </div>
    </div>
    <div id="s-blk" class="blk clip" data-start="6.75" data-duration="5.05" data-track-index="1">
      <div class="kicker"><i id="s-rule"></i><span>Sasaran</span></div>
      <div id="s-row">
        <div id="s-num">70%</div>
        <div id="s-lbl"><span id="s-l1" class="w">Tahap sara diri</span><br /><span id="s-l2" class="w">(SSR)</span> <span id="s-l3" class="w">beras negara</span></div>
      </div>
    </div>""", """
    kick("#k-rule", 0.1);
    light("#k-s1", 0.63); // cadangan ini
    light("#k-s2", 1.27); // diberikan perhatian
    light("#k-s3", 2.16); // kementerian
    reveal("#k-w1", 3.44); // pertanian negara
    reveal("#k-w2", 4.44); // lebih berdaya maju
    out("#k-blk", 6.45);

    kick("#s-rule", 6.9); // sasaran
    tl.fromTo("#s-num", { opacity: 0, scale: 1.35, filter: "blur(12px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out", transformOrigin: "0% 100%" }, 7.5); // 70%
    light("#s-l1", 8.09); // tahap sara diri
    light("#s-l2", 9.26); // SSR
    light("#s-l3", 10.8); // beras negara"""))

# ── F · final (local = video − 82.4) ────────────────────────────────────────────
write("final.html", scene("final", """
    #fin-scrim { position: absolute; inset: 0; background: linear-gradient(180deg, rgba(8, 26, 50, 0.92) 0%, rgba(8, 11, 19, 0.88) 100%); }
    #fin-card { position: absolute; left: 72px; top: 330px; width: 936px; height: 990px; }
    #fin-name { margin-top: 24px; font-family: "Anton", sans-serif; font-size: 88px; line-height: 1.04; text-transform: uppercase; }
    #fin-seat { margin-top: 10px; font-weight: 600; font-size: 38px; color: #ffd447; }
    #fin-ans { margin-top: 46px; padding: 26px 28px; background: rgba(8, 26, 50, 0.85); border-left: 5px solid #d6ac52; }
    #fin-ans ul { margin-top: 14px; padding-left: 0; list-style: none; }
    #fin-ans li { position: relative; padding-left: 30px; margin-top: 12px; font-weight: 600; font-size: 32px; line-height: 1.32; color: #f2f2f2; }
    #fin-ans li::before { content: ""; position: absolute; left: 0; top: 16px; width: 12px; height: 12px; background: #d6ac52; }
    #fin-ans b { color: #ffd447; font-weight: 800; }
    #fin-credit { margin-top: 30px; font-weight: 600; font-size: 28px; color: #b9c0cc; }
""", """    <div id="fin-scrim" class="clip" data-start="0" data-duration="6.6" data-track-index="0"></div>
    <div id="fin-card" class="clip" data-start="0.4" data-duration="6.2" data-track-index="1">
      <div class="kicker"><i id="fin-rule"></i><span>Kamar Khas &nbsp;|&nbsp; Dewan Rakyat</span></div>
      <div id="fin-name">
        <span class="line" data-layout-allow-overflow><span id="fin-n1" class="w">Hj. Muhammad Ismi</span></span>
        <span class="line" data-layout-allow-overflow><span id="fin-n2" class="w">bin Mat Taib</span></span>
      </div>
      <div id="fin-seat">Ahli Parlimen Parit, Perak</div>
      <div id="fin-ans">
        <div class="kicker">Jawapan kementerian di Kamar Khas</div>
        <ul>
          <li><b>3 projek pengairan</b> luar jelapang di Perak Tengah dipohon dalam <b>RMK13</b></li>
          <li>Harga lantai padi diselaraskan <b>RM1,300 → RM1,500</b> setiap tan metrik (mulai 16 Feb 2025)</li>
        </ul>
      </div>
      <div id="fin-credit">Petikan ucapan asal &nbsp;·&nbsp; Rakaman Kamar Khas, Dewan Rakyat</div>
    </div>""", """
    tl.fromTo("#fin-scrim", { opacity: 0 }, { opacity: 1, duration: 0.9, ease: "power2.inOut" }, 0);
    kick("#fin-rule", 0.45);
    tl.fromTo(["#fin-n1", "#fin-n2"], { yPercent: 105 }, { yPercent: 0, duration: 0.55, stagger: 0.12, ease: "power4.out" }, 0.8);
    blurIn("#fin-seat", 1.25);
    blurIn("#fin-ans", 1.7);
    tl.fromTo("#fin-credit", { opacity: 0 }, { opacity: 1, duration: 0.3, ease: "power2.out" }, 2.1);
    tl.to(["#fin-card", "#fin-scrim"], { opacity: 0, duration: 0.9, ease: "power2.in" }, 5.7);"""))

print("scenes written")
