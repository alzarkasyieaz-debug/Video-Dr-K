#!/usr/bin/env python3
"""Per-issue videos (Parit local issues only) from the 5 speeches in Drive folder
1vLCNBKHN1Lozh-yUDs1qx7tfTNKpN0B4.

  d1 = "1-Isu Sekolah.mp4"   committee stage, Ministry of Education (Kepala B63)
  d2 = "2-Kamar Khas.mp4"    Kamar Khas
  d3 = "Ucapan 2.mp4"        budget debate
  d4 = "Ucapan 3.mp4"        debate on the royal address
  d5 = "Ucapan 4.mp4"        Budget 2024 debate ("Kerajaan Persekutuan telah membentangkan Belanjawan 2024")

Segments: (file, src_in, src_out) in output order; the first is the hook.
Card times are SOURCE times (file, t) — hfkit maps them to output time.
    python3 tools/ep4_specs.py [video-id ...]
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hfkit

OUT = os.path.join(hfkit.ROOT, "ep4-parit")
CROPS = {"d1": 488, "d3": 460, "d4": 335, "d5": 370, "d2": 408, "d2dm": 538, "d2hm": 400}
hfkit.FACE_Y.update({"d1": 245, "d3": 210, "d4": 170, "d5": 190, "d2": 240, "d2dm": 210, "d2hm": 190})

S_D1 = "JAWATANKUASA · KEMENTERIAN PENDIDIKAN"
S_D3 = "PERBAHASAN BAJET"
S_D4 = "PERBAHASAN TITAH DIRAJA"
S_D5 = "PERBAHASAN BAJET 2024"
S_KK = "KAMAR KHAS · UCAPAN YB PARIT"
S_DM = "JAWAPAN TIMBALAN MENTERI DALAM NEGERI"
S_HM = "JAWAPAN MENTERI KESIHATAN"

KEYS = r"^(sekolah|murid|mendadak|bangunan|tambahan|universiti|sesi|SKM|pembaziran|guru|kuarters|terbiar|kosong|jalan|teruk|kemalangan|kematian|parit|B40|" \
       r"miskin|perumahan|pelancongan|homestay|telekomunikasi|internet|digital|lambor|pengairan|air|padi|akuakultur|sangkar|hakisan|pasir|" \
       r"MRSM|tahfiz|masjid|uzur|hospital|katil|pakar|rehabilitasi|dataran|seluang|hektar|dewan|komuniti|teknologi|kilang|segera|disegerakan)$"

SPECS = [
    # ------------------------------------------------------------------ 01 sekolah sesak
    dict(id="01-sekolah-sesak", title="Sekolah Sesak di Seri Iskandar", topic="ISU · SEKOLAH SESAK, SERI ISKANDAR",
         outro="SEKOLAH SESAK<br />SERI ISKANDAR",
         segments=[("d1", 88.75, 92.45), ("d1", 80.15, 139.55), ("d5", 756.45, 769.65)],
         hook=dict(kick="SERI ISKANDAR · DEWAN RAKYAT", lines=["“MENGAKIBATKAN BILANGAN MURID"], big="NAIK MENDADAK”", t_big=91.4, t_lines=[88.8]),
         cards=[
             dict(at=("d1", 92.5), type="pills", kicker="SEKOLAH TERKESAN LIMPAHAN MURID", src=S_D1, items=[
                 ("SK SERI ISKANDAR", ("d1", 95.8), "gold"), ("SK ISKANDAR PERDANA", ("d1", 97.3), "gold"),
                 ("SK SERI TRONOH · PARLIMEN BERHAMPIRAN", ("d1", 101.9), ""), ("TERKESAN SANGAT TERUK", ("d1", 104.0), "red")]),
             dict(at=("d1", 107.1), type="big", kicker="MOHON DISEGERAKAN", big="BANGUNAN TAMBAHAN", t=("d1", 110.2),
                  subs=[("bagi sekolah-sekolah ini", ("d1", 111.6))]),
             dict(at=("d1", 112.9), type="pills", kicker="BANDAR UNIVERSITI, SERI ISKANDAR", items=[
                 ("SEKOLAH BARU", ("d1", 115.2), "gold"), ("LOT TANAH SUDAH DIPERUNTUKKAN", ("d1", 118.8), ""),
                 ("MASIH BELUM DIBINA", ("d1", 122.9), "red"), ("PERUMAHAN MELEPASI 3,000 BUAH RUMAH", ("d1", 126.2), "")]),
             dict(at=("d1", 129.3), type="big", mode="full", kicker="DI PARLIMEN PARIT", big="DUA SESI", t=("d1", 135.9), tag="",
                  subs=[("beberapa sekolah terpaksa mengadakan dua sesi", ("d1", 134.7))]),
             dict(at=("d5", 756.5), type="pills", kicker="BANDAR UNIVERSITI", src=S_D5, items=[
                 ("SMK BANDAR UNIVERSITI AKAN DIBINA ✓", ("d5", 761.7), "gold"), ("MOHON SEKOLAH RENDAH JUGA", ("d5", 764.4), ""),
                 ("KEPADATAN PENDUDUK", ("d5", 766.6), "red")]),
         ],
         fix={}, subs=[(r"\b33\b\x00ribu", "3,000\x00"), (r"\bTrono\b", "Tronoh"), (r"\bredah\b", "rendah")]),

    # ------------------------------------------------------------------ 02 sekolah kurang murid
    dict(id="02-sekolah-kurang-murid", title="26 Sekolah Kurang Murid di Parit", topic="ISU · SEKOLAH KURANG MURID (SKM)",
         outro="SEKOLAH KURANG MURID<br />PARLIMEN PARIT",
         segments=[("d1", 186.95, 190.95), ("d1", 162.25, 206.95)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“SEDANGKAN GURU ADA 10 ORANG."], big="INI PEMBAZIRAN.”", t_big=190.2, t_lines=[187.0]),
         cards=[
             dict(at=("d1", 164.3), type="stats", kicker="SEKOLAH KURANG MURID (SKM)", src=S_D1, items=[
                 dict(label="SKM DI PARLIMEN PARIT", value="26 BUAH", t=("d1", 165.3), note="sekolah kurang murid", size=104)]),
             dict(at=("d1", 170.4), type="stats", kicker="CONTOH: SJKC CHUNG HUA, PARIT", items=[
                 dict(label="PELAJAR", value="26", t=("d1", 176.8), note="5 Cina · 21 Melayu &amp; India", t_note=("d1", 182.0), size=96),
                 dict(label="GURU", value="10", t=("d1", 189.0), note="9 Cina · 1 Melayu", t_note=("d1", 194.3), red=True, size=96)]),
             dict(at=("d1", 197.6), type="big", mode="full", kicker="TUNTUTAN", big="ATASI PEMBAZIRAN", t=("d1", 200.4), tag="",
                  subs=[("26 sekolah kurang murid di Parlimen Parit", ("d1", 202.0))]),
         ],
         subs=[(r"Chung\x00Hua", "Chung\x00Hua,")]),

    # ------------------------------------------------------------------ 03 kuarters guru
    dict(id="03-kuarters-guru", title="Kuarters Guru Terbiar di Parit", topic="ISU · KUARTERS GURU TERBIAR",
         outro="KUARTERS GURU<br />TERBIAR",
         segments=[("d1", 212.45, 217.3), ("d1", 206.85, 242.45)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“KUARTERS GURU … YANG"], big="TERBIAR KOSONG”", t_big=216.6, t_lines=[212.5]),
         cards=[
             dict(at=("d1", 211.9), type="pills", kicker="KUARTERS GURU DI PARIT", src=S_D1, items=[
                 ("KAMPUNG SADANG", ("d1", 213.2), "gold"), ("SUNGAI RANGGAM", ("d1", 214.5), "gold"), ("PULAU TIGA KIRI", ("d1", 215.6), "gold"),
                 ("TERBIAR KOSONG", ("d1", 216.6), "red")]),
             dict(at=("d1", 217.3), type="q", label="MOHON KEMENTERIAN", lines=[
                 ("Fikirkan cara supaya <b>jangan berlaku pembaziran</b>.", ("d1", 218.2))]),
             dict(at=("d1", 231.5), type="tiles", kicker="CADANGAN MEMANFAATKAN KUARTERS", items=[
                 ("Beri kepada asnaf", ("d1", 232.6)), ("Sewa dengan harga rendah", ("d1", 233.7)), ("Sewa kepada maahad tahfiz", ("d1", 235.8))]),
         ],
         subs=[(r"Mak\x00Tafis", "maahad\x00tahfiz")]),

    # ------------------------------------------------------------------ 04 jalan raya
    dict(id="04-jalan-raya", title="Jalan Raya di Parit", topic="ISU · JALAN RAYA PARLIMEN PARIT",
         outro="JALAN RAYA<br />PARLIMEN PARIT",
         segments=[("d4", 554.05, 556.7), ("d3", 191.75, 219.75), ("d4", 544.65, 557.6), ("d5", 681.05, 687.3)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“INI AKAN MENGAKIBATKAN"], big="KEMALANGAN, KEMATIAN”", size=96, t_big=554.8, t_lines=[554.1]),
         cards=[
             dict(at=("d3", 192.5), type="pills", kicker="JALAN PERSEKUTUAN DI PARLIMEN PARIT", src=S_D3, items=[
                 ("KEBANYAKANNYA TERUK", ("d3", 196.3), "red"), ("TIDAK DIBAIKI SEPENUHNYA", ("d3", 197.1), ""),
                 ("ALASAN: KEKURANGAN PERUNTUKAN", ("d3", 200.3), "")]),
             dict(at=("d3", 203.5), type="big", kicker="JALAN-JALAN INI", big="NADI PERHUBUNGAN RAKYAT", size=74, t=("d3", 205.9),
                  subs=[("kebanyakannya golongan B40 — untuk mencari rezeki", ("d3", 209.2))]),
             dict(at=("d3", 215.6), type="q", label="MOHON", lines=[("<b>Kementerian Kerja Raya</b> memberi maklum balas berkaitan isu ini.", ("d3", 216.4))]),
             dict(at=("d4", 545.4), type="pills", kicker="INFRASTRUKTUR JALAN", src=S_D4, items=[
                 ("PERLU DITURAP", ("d4", 549.8), "gold"), ("PERLU DISELENGGARA DENGAN BAIK", ("d4", 551.0), "gold"),
                 ("KEMALANGAN", ("d4", 554.8), "red"), ("KEMATIAN", ("d4", 555.6), "red")]),
             dict(at=("d5", 681.1), type="big", kicker="MOHON TINDAKAN SEGERA", src=S_D5, big="LEBARKAN JALAN", t=("d5", 682.3),
                  subs=[("Bota Kanan → Pekan Parit", ("d5", 685.3))]),
         ],
         subs=[(r"maklum\x00malas", "maklum\x00balas"), (r"kepekan", "ke pekan"), (r"Kepekan", "ke pekan")]),

    # ------------------------------------------------------------------ 05 perumahan
    dict(id="05-perumahan-miskin", title="Perumahan untuk Golongan Miskin di Parit", topic="ISU · PERUMAHAN DI PARIT",
         outro="PERUMAHAN<br />GOLONGAN MISKIN",
         segments=[("d3", 250.05, 255.15), ("d3", 220.65, 260.95)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“KELUARGA MISKIN TERPAKSA MENUNGGU LAMA DAN"], big="DINAFIKAN HAK”", t_big=253.7, t_lines=[250.1]),
         cards=[
             dict(at=("d3", 221.4), type="pills", kicker="PRASARANA PERUMAHAN TERSUSUN", src=S_D3, items=[
                 ("PERUMAHAN TERSUSUN DI PARIT", ("d3", 222.9), "gold"), ("PERLU PERHATIAN SERIUS", ("d3", 225.7), "red")]),
             dict(at=("d3", 228.9), type="tiles", kicker="PERANCANGAN INI PERLU", items=[
                 ("Pembangunan secara sistematik", ("d3", 233.7)), ("Memudahkan fasa seterusnya", ("d3", 236.4)), ("Tanpa mengganggu ekologi", ("d3", 239.4))]),
             dict(at=("d3", 242.1), type="stats", kicker="RUMAH GOLONGAN MISKIN, PARIT", items=[
                 dict(label="PERUNTUKAN &amp; KELULUSAN", value="AMAT SEDIKIT", t=("d3", 248.7), red=True, size=80,
                      note="ramai keluarga miskin terpaksa menunggu lama", t_note=("d3", 250.6))]),
             dict(at=("d3", 256.6), type="q", label="MOHON", lines=[("<b>Kementerian Pembangunan Kerajaan Tempatan</b> memberi penjelasan.", ("d3", 257.0))]),
         ],
         subs=[(r"memakitkan", "membangkitkan"), (r"penyedaan", "penyediaan"), (r"faksa", "fasa")]),

    # ------------------------------------------------------------------ 06 agro-pelancongan
    dict(id="06-agro-pelancongan", title="Agro-Pelancongan Parit", topic="ISU · AGRO-PELANCONGAN PARIT",
         outro="AGRO-PELANCONGAN<br />PARIT",
         segments=[("d3", 284.95, 288.95), ("d3", 262.45, 315.75), ("d5", 769.65, 776.85)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“PARLIMEN PARIT MEMPUNYAI BEBERAPA"], big="KAWASAN TARIKAN”", t_big=287.3, t_lines=[285.0]),
         cards=[
             dict(at=("d3", 274.1), type="tiles", kicker="AKTIVITI AGRO-PELANCONGAN", src=S_D3, items=[
                 ("Lawatan dusun buah-buahan", ("d3", 276.8)), ("Ladang ternakan", ("d3", 279.3)),
                 ("Industri kecil produk setempat", ("d3", 280.8)), ("Homestay", ("d3", 283.3))]),
             dict(at=("d3", 295.1), type="pills", kicker="TARIKAN DI PARLIMEN PARIT", items=[
                 ("PADANG KOBA", ("d3", 296.7), "gold"), ("TELUK BAKUNG", ("d3", 297.5), "gold"),
                 ("TEBING SUNGAI PERAK · PEKAN PARIT → EKOR LAMBAT", ("d3", 298.3), ""), ("TAMAN CEMPAKA SARI", ("d3", 301.8), "gold")]),
             dict(at=("d3", 303.8), type="q", lines=[("Apakah kementerian berhasrat <b>menggiatkan agro-pelancongan</b> di Parlimen Parit?", ("d3", 309.8))]),
             dict(at=("d5", 769.7), type="big", kicker="MOHON NAIK TARAF", src=S_D5, big="DATARAN TUNTUNG", t=("d5", 771.6),
                  subs=[("Bota Kanan — tarikan pelancongan daerah Perak Tengah", ("d5", 773.1))]),
         ],
         subs=[(r"\btuluk\b", "Teluk"), (r"\bbakung\b", "Bakung"), (r"\bkoba\b", "Koba"), (r"\bpadang\b", "Padang"), (r"mengiatkan", "menggiatkan"),
               (r"\bbuta\b", "Bota"), (r"\bkanan\b", "Kanan"), (r"\btuntung\b", "Tuntung"), (r"\bperak\b", "Perak"), (r"\bcempaka\b", "Cempaka"), (r"\bsari\b", "Sari"), (r"\bekor\x00lambat", "Ekor\x00Lambat")]),

    # ------------------------------------------------------------------ 07 telekomunikasi
    dict(id="07-liputan-internet", title="Liputan Telekomunikasi & Jalur Lebar di Parit", topic="ISU · LIPUTAN INTERNET LUAR BANDAR",
         outro="LIPUTAN INTERNET<br />LUAR BANDAR",
         segments=[("d3", 342.35, 347.5), ("d3", 317.05, 355.1)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“JIKA CAPAIAN RANGKAIAN TIDAK MEMUASKAN,"], big="MERENCATKAN URUSAN”", size=96, t_big=345.6, t_lines=[342.4]),
         cards=[
             dict(at=("d3", 318.0), type="big", kicker="MOHON NAIK TARAF", src=S_D3, big="TELEKOMUNIKASI<br />&amp; JALUR LEBAR", size=72, t=("d3", 320.6)),
             dict(at=("d3", 325.9), type="pills", kicker="MOHON KERAJAAN MEMASTIKAN LIPUTAN", items=[
                 ("DIPERLUAS", ("d3", 330.4), "gold"), ("KUALITI DITINGKATKAN", ("d3", 331.6), "gold"),
                 ("TERMASUK LUAR BANDAR SEPERTI PARIT", ("d3", 333.5), "")]),
             dict(at=("d3", 336.6), type="pills", kicker="KEPERLUAN UTAMA", items=[("URUSAN HARIAN RAKYAT KINI DIGITAL", ("d3", 338.5), "gold")]),
             dict(at=("d3", 348.4), type="tiles", kicker="INTERNET TIDAK STABIL MENYUKARKAN", items=[
                 ("Peniaga atas talian", ("d3", 349.1)), ("Pelajar pengajian dalam talian", ("d3", 350.8))]),
         ],
         subs=[(r"merencahkan", "merencatkan")]),

    # ------------------------------------------------------------------ 08 pertanian & akuakultur
    dict(id="08-pertanian-akuakultur", title="Pertanian, Pengairan & Akuakultur Parit", topic="ISU · PERTANIAN &amp; BEKALAN MAKANAN",
         outro="PERTANIAN &amp;<br />AKUAKULTUR PARIT",
         segments=[("d3", 389.15, 393.95), ("d3", 356.15, 394.0), ("d5", 776.75, 807.05)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“PERTANIAN SAWAH PADI MERUPAKAN"], big="SUMBER UTAMA EKONOMI”", size=92, t_big=391.2, t_lines=[389.2]),
         cards=[
             dict(at=("d3", 356.6), type="big", kicker="JAMINAN BEKALAN MAKANAN", src=S_D3, big="MUKIM LAMBOR", t=("d3", 362.2),
                  subs=[("dinaik taraf sebagai kawasan pertanian bersepadu", ("d3", 364.1))]),
             dict(at=("d3", 373.6), type="pills", kicker="RUMAH PAM PENGAIRAN DI PARIT", items=[
                 ("MOHON NAIK TARAF", ("d3", 374.2), "gold"), ("KEKURANGAN BEKALAN AIR", ("d3", 383.9), "red"),
                 ("KETIKA MUSIM DIPERLUKAN PETANI", ("d3", 386.3), "")]),
             dict(at=("d5", 776.9), type="big", kicker="DAERAH PERAK TENGAH", src=S_D5, big="AKUAKULTUR", t=("d5", 787.1),
                  subs=[("program pembangunan integrasi di sepanjang Sungai Perak", ("d5", 787.9))]),
             dict(at=("d5", 789.8), type="pills", kicker="KAWASAN BERPOTENSI", items=[
                 ("BOTA KANAN · BOTA KIRI", ("d5", 790.1), "gold"), ("LAYANG KANAN · LAYANG KIRI", ("d5", 791.7), "gold"),
                 ("CHOPPING KANAN · CHOPPING KIRI", ("d5", 792.9), "gold"), ("BELANJA KANAN · BELANJA KIRI", ("d5", 794.8), "gold"),
                 ("IKAN SANGKAR", ("d5", 799.6), ""), ("KEBANYAKANNYA DIHANTAR KE TEMERLOH", ("d5", 802.0), "red")]),
         ],
         subs=[(r"\blambor\b", "Lambor"), (r"\bsangka\b", "sangkar"), (r"\btemerlu\b", "Temerloh"), (r"\b[Cc]oping\b", "Chopping"), (r"\blayang\b", "Layang"),
               (r"\bbelanja\b", "Belanja"), (r"\bbota\b", "Bota"), (r"\bkanan\b", "Kanan"), (r"\bkiri\b", "Kiri")]),

    # ------------------------------------------------------------------ 09 hakisan sungai perak
    dict(id="09-hakisan-sungai-perak", title="Hakisan Tebing Sungai Perak", topic="ISU · HAKISAN TEBING SUNGAI PERAK",
         outro="HAKISAN TEBING<br />SUNGAI PERAK",
         segments=[("d3", 411.85, 414.05), ("d3", 394.55, 414.05)],
         hook=dict(kick="SUNGAI PERAK · DEWAN RAKYAT", lines=["“REBAKAN DAN HAKISAN INI"], big="SANGAT MEMBAHAYAKAN”", size=96, t_big=412.5, t_lines=[411.9]),
         cards=[
             dict(at=("d3", 394.6), type="pills", kicker="PENGUATKUASAAN DIPERLUKAN", src=S_D3, items=[
                 ("PELOMBONG PASIR DI SUNGAI", ("d3", 396.5), "gold"), ("GAGAL MENGIKUT SYARAT", ("d3", 399.3), "red")]),
             dict(at=("d3", 402.9), type="big", kicker="PUNCA UTAMA", big="HAKISAN TEBING", t=("d3", 405.7),
                  subs=[("di sepanjang jajaran Sungai Perak", ("d3", 407.8))]),
         ]),

    # ------------------------------------------------------------------ 10 MRSM tahfiz
    dict(id="10-mrsm-parit-tahfiz", title="MRSM Parit sebagai Tahfiz Ulul Albab", topic="CADANGAN · MRSM PARIT",
         outro="MRSM PARIT<br />TAHFIZ ULUL ALBAB",
         segments=[("d4", 199.65, 215.2)],
         hook=None,
         cards=[
             dict(at=("d4", 203.1), type="big", kicker="CADANGAN", src=S_D4, big="MRSM PARIT", t=("d4", 204.1),
                  subs=[("dijadikan Tahfiz Ulul Albab", ("d4", 205.8)), ("melahirkan lebih ramai huffaz di Parit", ("d4", 211.4))]),
         ],
         subs=[(r"TAHFIS", "Tahfiz"), (r"ulul\x00al-bab", "Ulul\x00Albab"), (r"hufaz", "huffaz")]),

    # ------------------------------------------------------------------ 11 masjid
    dict(id="11-masjid-uzur", title="Dua Masjid Uzur di Parit", topic="ISU · MASJID UZUR DI PARIT",
         outro="MASJID UFRANIAH &amp;<br />MASJID LATIFAH",
         segments=[("d5", 821.15, 824.45), ("d4", 216.75, 242.0), ("d5", 807.45, 836.4)],
         hook=dict(kick="PARLIMEN PARIT · DEWAN RAKYAT", lines=["“KERANA TELAH PUN TERLALU UZUR,"], big="PEMBINAAN SEMULA”", t_big=822.9, t_lines=[821.2]),
         cards=[
             dict(at=("d4", 216.8), type="pills", kicker="MOHON KERAJAAN", src=S_D4, items=[("MASJID LEBIH SELESA &amp; MESRA PENGGUNA", ("d4", 222.6), "gold")]),
             dict(at=("d4", 228.0), type="tiles", kicker="UZUR &amp; USANG · MOHON DIBINA BARU", items=[
                 ("Masjid Ufraniah, Titi Gantung", ("d4", 238.1)), ("Masjid Latifah, Sungai Korok", ("d4", 240.1))]),
             dict(at=("d5", 807.5), type="tiles", kicker="MOHON DIBINA DENGAN SEGERA", src=S_D5, items=[
                 ("Masjid Ufraniah", ("d5", 810.3)), ("Masjid Latifah, Sungai Korok", ("d5", 813.4))]),
             dict(at=("d5", 825.3), type="stats", kicker="KUTIPAN AJK MASJID", items=[
                 dict(label="SUDAH DISEDIAKAN", value="&gt; 10%", t=("d5", 831.9), size=104, note="daripada nilai projek, seperti yang dimahukan kementerian", t_note=("d5", 832.8))]),
         ],
         subs=[(r"Titik\x00Gantung", "Titi\x00Gantung"), (r"Ufrania\b", "Ufraniah"), (r"\buzu\b", "uzur"), (r"Memakili", "Mewakili")]),

    # ------------------------------------------------------------------ 12 hospital
    dict(id="12-hospital-seri-iskandar", title="Hospital Seri Iskandar", topic="ISU · HOSPITAL SERI ISKANDAR",
         outro="HOSPITAL<br />SERI ISKANDAR",
         segments=[("d4", 522.15, 528.1), ("d4", 519.05, 544.5), ("d5", 163.55, 182.65), ("d5", 731.45, 753.6)],
         hook=dict(kick="SERI ISKANDAR · DEWAN RAKYAT", lines=["“76 KATIL, SEDANGKAN RAKYAT ADA 61,000."], big="TIDAK MENCUKUPI”", t_big=527.5, t_lines=[522.2]),
         cards=[
             dict(at=("d4", 519.1), type="stats", kicker="HOSPITAL SERI ISKANDAR (DIBINA)", src=S_D4, items=[
                 dict(label="KAPASITI", value="76 KATIL", t=("d4", 522.9), size=72),
                 dict(label="PENDUDUK", value="61,000", t=("d4", 525.1), size=72, red=True)]),
             dict(at=("d4", 529.2), type="pills", kicker="MOHON", items=[
                 ("TAMBAH KAPASITI", ("d4", 531.7), "gold"), ("PERKHIDMATAN PAKAR", ("d4", 539.4), "gold"),
                 ("RAKYAT TIDAK PERLU PERGI JAUH", ("d4", 541.1), "")]),
             dict(at=("d5", 163.6), type="stats", kicker="PERUNTUKAN DISEBUT DALAM UCAPAN", src=S_D5, items=[
                 dict(label="HOSPITAL SERI ISKANDAR", value="RM140 JUTA", t=("d5", 168.1), size=60),
                 dict(label="NAIK TARAF PARKIR · HOSPITAL PULAI", value="RM500 JUTA", t=("d5", 175.4), size=60, red=True,
                      note="“tidak wajar, tidak adil”", t_note=("d5", 181.0))]),
             dict(at=("d5", 731.5), type="big", kicker="SELEPAS HOSPITAL BARU SIAP", big="HOSPITAL<br />CHANGKAT MELINTANG", size=70, t=("d5", 737.9),
                  subs=[("→ pusat rehabilitasi, atau pusat rawatan komuniti", ("d5", 740.0))]),
         ],
         subs=[(r"RM61,000", "61,000"), (r"mencukup\b", "mencukupi"), (r"Cangkap\x00Lintang", "Changkat\x00Melintang"),
               (r"Pemberdahan", "pembedahan"), (r"Randa", "Perdana"), (r"pelarai", "pilihan raya"), (r"pulai", "Pulai")]),

    # ------------------------------------------------------------------ 13 dataran sungai seluang
    dict(id="13-dataran-sungai-seluang", title="Taman Awam Dataran Sungai Seluang", topic="ISU · DATARAN SUNGAI SELUANG",
         outro="DATARAN<br />SUNGAI SELUANG",
         segments=[("d5", 711.45, 714.95), ("d4", 567.75, 575.3), ("d5", 705.05, 717.5)],
         hook=dict(kick="SERI ISKANDAR · DEWAN RAKYAT", lines=["“KELUASAN 19 HEKTAR,"], big="LOKASI BERIADAH”", t_big=713.4, t_lines=[711.5]),
         cards=[
             dict(at=("d4", 567.8), type="stats", kicker="TAMAN REKREASI UNTUK RAKYAT PARIT", src=S_D4, items=[
                 dict(label="DATARAN SUNGAI SELUANG", value="19 HEKTAR", t=("d4", 571.6), size=96, note="peluang anak muda beriadah", t_note=("d4", 573.7))]),
             dict(at=("d5", 705.1), type="big", kicker="MOHON DIBINA", src=S_D5, big="TAMAN AWAM", t=("d5", 707.2),
                  subs=[("di Dataran Sungai Seluang", ("d5", 708.2)), ("taman rekreasi ini sangat penting", ("d5", 715.9))]),
         ]),

    # ------------------------------------------------------------------ 14 kemudahan komuniti
    dict(id="14-dewan-kompleks-komuniti", title="Dewan Serba Guna & Kompleks Komuniti", topic="ISU · KEMUDAHAN KOMUNITI",
         outro="DEWAN &amp; KOMPLEKS<br />KOMUNITI",
         segments=[("d5", 700.45, 705.05), ("d5", 687.25, 705.05), ("d5", 719.45, 731.45)],
         hook=dict(kick="SERI ISKANDAR · DEWAN RAKYAT", lines=["“MENGALAMI PERTAMBAHAN PENDUDUK"], big="SANGAT KETARA”", t_big=704.5, t_lines=[702.5]),
         cards=[
             dict(at=("d5", 687.3), type="tiles", kicker="MOHON DIBINA DEWAN SERBA GUNA", src=S_D5, items=[
                 ("Dataran Jagung, Titi Gantung", ("d5", 690.2)), ("Perkarangan masjid, Bandar Universiti Seri Iskandar", ("d5", 692.6))]),
             dict(at=("d5", 695.8), type="pills", kicker="UNTUK", items=[("AKTIVITI MASYARAKAT SETEMPAT", ("d5", 698.7), "gold")]),
             dict(at=("d5", 719.5), type="big", kicker="MOHON DIBINA", big="KOMPLEKS KOMUNITI", size=80, t=("d5", 722.1),
                  subs=[("dilengkapi fasiliti untuk kegunaan awam", ("d5", 723.6)), ("tapak sedia ada di Seri Iskandar", ("d5", 728.9))]),
         ],
         subs=[(r"titik\x00gantung", "Titi\x00Gantung"), (r"jagung", "Jagung"), (r"perkerangan", "perkarangan"), (r"kompleksukan", "kompleks")]),

    # ------------------------------------------------------------------ 15 taman teknologi
    dict(id="15-taman-teknologi", title="Taman Teknologi Seri Iskandar", topic="ISU · TAMAN TEKNOLOGI SERI ISKANDAR",
         outro="TAMAN TEKNOLOGI<br />SERI ISKANDAR",
         segments=[("d5", 853.65, 857.0), ("d5", 838.65, 864.0)],
         hook=dict(kick="SERI ISKANDAR · DEWAN RAKYAT", lines=["“HANYA TERDAPAT"], big="DUA KILANG SAHAJA”", t_big=855.1, t_lines=[853.7]),
         cards=[
             dict(at=("d5", 839.2), type="big", kicker="MOHON DIAKTIFKAN", src=S_D5, big="TAMAN TEKNOLOGI", size=84, t=("d5", 840.6),
                  subs=[("Seri Iskandar", ("d5", 841.5))]),
             dict(at=("d5", 843.8), type="pills", kicker="ISUNYA", items=[
                 ("BANYAK TANAH INDUSTRI DISEDIAKAN", ("d5", 843.8), "gold"), ("KURANG MINAT PELABUR ASING &amp; TEMPATAN", ("d5", 847.5), "red"),
                 ("HANYA 2 KILANG BEROPERASI", ("d5", 855.1), "red")]),
             dict(at=("d5", 858.5), type="q", label="MOHON", lines=[("Pihak berkenaan mengambil tindakan sewajarnya <b>memanfaatkan kawasan yang telah disediakan</b>.", ("d5", 859.5))]),
         ],
         subs=[(r"Skandal", "Iskandar")]),

    # ------------------------------------------------------------------ 16 kaunter imigresen (Kamar Khas)
    dict(id="16-kaunter-imigresen", title="Kaunter Imigresen untuk Parit (Kamar Khas)", topic="KAMAR KHAS · KAUNTER IMIGRESEN PARIT",
         outro="KAUNTER IMIGRESEN<br />UNTUK PARIT",
         segments=[("d2", 446.35, 451.4), ("d2", 9.6, 21.6), ("d2", 32.25, 46.0), ("d2dm", 227.2, 250.0),
                   ("d2", 397.9, 407.8), ("d2", 423.4, 441.8), ("d2dm", 513.7, 532.4)],
         hook=dict(kick="PARLIMEN PARIT · KAMAR KHAS", lines=["“ADA RAKYAT SAYA YANG MENGADU TERPAKSA"], big="TIDUR HOTEL”", t_big=449.2, t_lines=[446.4]),
         cards=[
             dict(at=("d2", 13.2), type="big", kicker="USUL KAMAR KHAS", src=S_KK, big="KAUNTER IMIGRESEN", size=80, t=("d2", 16.6),
                  subs=[("untuk komuniti setempat di Parlimen Parit", ("d2", 19.0))]),
             dict(at=("d2", 32.3), type="stats", kicker="PEJABAT IMIGRESEN TERDEKAT", items=[
                 dict(label="LUMUT", value="40 KM", t=("d2", 36.9), size=80),
                 dict(label="IPOH", value="30 KM", t=("d2", 39.9), size=80, note="40–50 minit perjalanan", t_note=("d2", 44.2))]),
             dict(at=("d2dm", 227.3), type="q", label=S_DM, mode="full", lines=[
                 ("Kementerian <b>belum mempunyai perancangan dalam masa terdekat</b>", ("d2dm", 236.7)),
                 ("— pejabat cawangan Ipoh &amp; Lumut masih dapat memenuhi permintaan setempat.", ("d2dm", 241.2))]),
             dict(at=("d2", 398.0), type="pills", kicker="SOALAN TAMBAHAN YB PARIT", src=S_KK, items=[
                 ("MERAYU KAUNTER DIWUJUDKAN", ("d2", 398.5), "gold"), ("PENDUDUK PERAK TENGAH BERTAMBAH PESAT", ("d2", 406.0), "")]),
             dict(at=("d2", 423.5), type="q", lines=[("Adakah kaunter imigresen boleh dibuka dengan <b>waktu operasi lebih fleksibel</b> — hujung minggu atau selepas waktu kerja?", ("d2", 425.0))]),
             dict(at=("d2dm", 513.8), type="stats", kicker=S_DM, mode="full", items=[
                 dict(label="HARI BEKERJA", value="HINGGA 8 MALAM", t=("d2dm", 522.4), size=54, note="termasuk waktu rehat", t_note=("d2dm", 526.0)),
                 dict(label="HUJUNG MINGGU", value="HINGGA 3 PETANG", t=("d2dm", 532.0), size=54)]),
         ],
         subs=[(r"immigration", "imigresen"), (r"perluka", "perlu ke"), (r"Pariwiparit", "Parit"), (r"\bgym\b", "JIM"), (r"Jim", "JIM"),
               (r"serakyat", "rakyat"), (r"menunjukkan", "menubuhkan"), (r"lalang", "lalu-lalang"), (r"40km", "40 km"), (r"30km", "30 km")]),

    # ------------------------------------------------------------------ 17 pakar hospital (Kamar Khas)
    dict(id="17-pakar-hospital-seri-iskandar", title="Tenaga Pakar Hospital Seri Iskandar (Kamar Khas)", topic="KAMAR KHAS · PAKAR HOSPITAL SERI ISKANDAR",
         outro="PAKAR HOSPITAL<br />SERI ISKANDAR",
         segments=[("d2", 648.25, 652.55), ("d2", 581.0, 588.1), ("d2", 607.45, 611.1), ("d2", 625.25, 635.5), ("d2", 673.6, 685.1),
                   ("d2hm", 812.45, 822.1), ("d2hm", 964.35, 989.0), ("d2hm", 991.1, 1010.1), ("d2hm", 1185.95, 1205.1)],
         hook=dict(kick="SERI ISKANDAR · KAMAR KHAS", lines=["“KETIADAAN TENAGA PAKAR YANG MENCUKUPI AKAN"], big="MENJEJASKAN OPERASI”", t_big=650.4, t_lines=[648.3]),
         cards=[
             dict(at=("d2", 581.3), type="big", kicker="HOSPITAL SERI ISKANDAR, PERAK TENGAH", src=S_KK, big="DIJANGKA SIAP OKTOBER", size=72, t=("d2", 585.9)),
             dict(at=("d2", 607.5), type="stats", kicker="KEMUDAHAN HOSPITAL", items=[
                 dict(label="HANYA", value="76 KATIL", t=("d2", 610.2), size=96)]),
             dict(at=("d2", 625.3), type="big", kicker="KEJAYAAN OPERASI BERGANTUNG KEPADA", big="TENAGA PAKAR", t=("d2", 634.1)),
             dict(at=("d2", 673.7), type="tiles", kicker="PAKAR YANG PERLU MENCUKUPI", items=[
                 ("Perubatan am", ("d2", 675.8)), ("Pakar bedah", ("d2", 676.7)), ("Pediatrik", ("d2", 677.5)),
                 ("Obstetrik &amp; ginekologi", ("d2", 678.8)), ("Perubatan kecemasan", ("d2", 682.5))]),
             dict(at=("d2hm", 812.5), type="stats", kicker=S_HM, mode="full", items=[
                 dict(label="HOSPITAL SERI ISKANDAR DIBINA SEBAGAI", value="TANPA PAKAR", t=("d2hm", 816.4), size=64, note="berkapasiti 76 katil", t_note=("d2hm", 820.5))]),
             dict(at=("d2hm", 964.4), type="pills", kicker="SUSUNAN KLUSTER HOSPITAL", src=S_HM, items=[
                 ("HOSPITAL UTAMA: SERI MANJUNG", ("d2hm", 970.3), "gold"), ("≥ 17 DISIPLIN KEPAKARAN", ("d2hm", 979.3), ""),
                 ("PAKAR PELAWAT (VISITING)", ("d2hm", 987.6), "")]),
             dict(at=("d2hm", 991.2), type="big", kicker="DIRANCANG OLEH KEMENTERIAN", big="PAKAR RESIDEN", t=("d2hm", 997.3),
                  subs=[("kecemasan (ED) &amp; perubatan dalaman", ("d2hm", 1006.8))]),
             dict(at=("d2hm", 1186.0), type="big", kicker="HOSPITAL CHANGKAT MELINTANG", big="STEP-DOWN / HEMODIALISIS", size=64, t=("d2hm", 1203.1),
                  subs=[("perkhidmatan berpindah ke Hospital Seri Iskandar", ("d2hm", 1188.3))]),
         ],
         subs=[(r"Motor", "Bota"), (r"\bTrono\b", "Tronoh"), (r"Suri", "Seri"), (r"jangkat\x00melintang", "Changkat\x00Melintang"),
               (r"presiden", "residen"), (r"imodialisis", "hemodialisis"), (r"Kesehatan", "Kesihatan"), (r"Ketidaan", "Ketiadaan"),
               (r"Paling\x00betul", "Paling\x00betul")]),
]


def main(ids):
    head = open(os.path.join(hfkit.ROOT, "ep3-seri-iskandar", "index.html")).read()
    head = head[: head.index("<body>")]
    for s in SPECS:
        if ids and s["id"] not in ids:
            continue
        s.setdefault("keys", KEYS)
        if s.get("hook") is None:
            s.pop("hook")
        v = hfkit.Video(s, OUT, CROPS)
        v.extract()
        v.build(head)
        print(f"{s['id']}: {v.total:.1f}s, segs={[(f, a, b) for f, a, b, o in v.segs]}")


if __name__ == "__main__":
    main(sys.argv[1:])
