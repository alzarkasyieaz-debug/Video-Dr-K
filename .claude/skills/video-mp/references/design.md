# Video MP — design system

## Palette

| Token | Hex | Use |
| --- | --- | --- |
| Deep Navy | `#081A32` | Top information band, card backgrounds, end-card scrim |
| Royal Gold | `#D6AC52` | Kickers, rules, list numbers, hero numbers, "gold" words |
| Highlight Yellow | `#FFD447` | The one word that carries the meaning, the spoken caption word, chips |
| White | `#FFFFFF` | Body type |
| Dark Background | `#080B13` | Ground, caption scrim (50%), bottom floor gradient |

Use one accent word per line. Yellow means "this is the point"; gold means "this is the label or the figure".

## Type

- **Anton** (shipped woff2, OFL): headlines and numbers. Uppercase, line-height 1. Sizes: hero 92–104, numbers 118–190, lower-third name 66, end-card name 88.
- **Montserrat** (bundled): kickers 700/28 px/0.14 em; small lines 800/31–38 px; captions 800/54–70 px; list rows 800/30 px; credits 600/28 px.
- Nothing under 28 px (the lint floor, 2.6% of 1080).

## Frame (1080×1920)

| Zone | y (px) | Holds |
| --- | --- | --- |
| Platform status bar | 0–168 | Nothing |
| Information band | 196–~480 | Every card, at x 72–1008 (936 wide), over a navy gradient 0→640 |
| Face | ~500–1000 | Nothing, ever. Check every card in a snapshot |
| Captions | 1150–1326 | One caption group, centred, one line |
| Platform UI | 1330–1920 | Footage and the dark floor gradient only |

Footage is a 3:4 crop of the 16:9 recording, shown as a 1080×1440 plate inside `#cam`. Wide framing is scale 1.36 (fills the frame); the face lands around y 890.

## Motion vocabulary

- **Camera:** hard punch-in (scale 1.6–1.86) on the key word of the hook and the climax; slow linear push inside every shot; a dip cut (40% black for 0.1 s) at each seam between clips; an eased 1 s pull-back only inside a segment. Never a crossfade between clips.
- **Cards:** the kicker rule draws (0.6 s expo.out); big words rise from a mask (0.45 s power4.out) **on the frame the word is spoken**; small words light from 25% to 100%; numbers pop in (scale 1.3 → 1, blur 10 → 0); chips land with back.out(1.6). Exit is blur 8 px + fade over 0.2 s. A landed title does not move.
- **Captions:** a group pops in (scale 0.88 → 1, back.out); the spoken word turns yellow; keywords stay yellow and pulse to 1.14×. 3 words per group for hook and climax, otherwise 4. Groups clear before every cut.
- **Sound:** a bass impact on the hook punch-in, one bigger hit on the climax figure, a soft hit under the end-card name, and a short whoosh at each seam. Speech is always dominant; SFX sit at 0.15–0.26 gain (the bundled files clip internally).
- **Footage look:** media-treatment Natural Portrait (`skin-soft`) with vignette 0.05. Never CSS filters on footage.

## Cards: what each kind is for

| Kind | When |
| --- | --- |
| Headline (`big`, no `at`) | Frame 0 of the hook: what the speech is about, 4–6 words |
| Lower third | Name, seat and location, once, early (in the band, not at the bottom) |
| `stats` | Figures the MP states (hectares, lots, RM). Pill "Petikan ucapan" when not independently verified |
| `big` + `small` | An argument in the MP's own words, with the location or detail lit word by word |
| `num` | One hero figure: a target (70% SSR), a claim (lebih 50%, shown as a quote) or a programme (RMK13) |
| `list` | The MP's numbered proposals or issues, with the one being spoken highlighted |
| `chip` | A short status in the MP's words ("✓ Telah pun dilaksanakan baru-baru ini") |
| End card | Name, seat, and either the closing quote or an attributed box with the ministry's answer, plus the credit |
