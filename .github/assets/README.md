# README images

Images used by the root `README.md`.

| File | What it is | How it was made |
| --- | --- | --- |
| `banner-light.png`, `banner-dark.png` | Title banner for light and dark mode | Rendered with headless Chromium from `source/banner.html` (one file with a dark-mode media query) |
| `terminal.png` | Terminal card: the public-evidence CLI downloading a public Supreme Court of India judgment (K. Subba Rao v. State of Telangana, 21 Aug 2018) and checking a quotation on the right and wrong PDF page | Real output from `retrieval.py fetch` and `check-quote` on 2026-10-26, abridged with "…" and rendered as a card |

## Visual identity

Sober legal-publishing look. Indian and international legal research products (SCC Online: a serif display face with a crimson accent; Manupatra: navy; Harvey: serif on warm off-white) favour serif type, paper tones and one deep accent. This banner follows that language without copying any of them, and uses no court or government emblem.

- **Fonts:** Newsreader (headline and memo), Source Sans 3 (text), IBM Plex Mono (pinpoint line). All from Google Fonts.
- **Colours:** paper `#f7f3ea` / `#13161d`, ink `#1b2333` / `#ede6d6`, oxblood `#8a1c2b` (light) / `#d9707c` (dark), rule `#d9cfbc`, secondary `#5d6270`.
- **Motif:** a draft research memo on court-style paper with a red margin rule, highlighted quoted lines, and a round "Quote checked against original" rubber stamp. Illustration only; it is not a real document.
- **README:** badges use `8a1c2b`, `1b2333` and `5d6270`; no emoji. The feature table is numbered I to VIII instead.

To re-render after editing `source/banner.html` (needs Node.js with Playwright and a Chromium build):

```bash
node render-html.mjs .github/assets/source/banner.html .github/assets/banner-light.png --scheme light
node render-html.mjs .github/assets/source/banner.html .github/assets/banner-dark.png --scheme dark
```

`render-html.mjs` is a small Playwright script, not part of this repository: it opens the file at 1600x600, sets `prefers-color-scheme`, waits for fonts and saves a 2x screenshot. Any headless browser screenshot at that size works the same way.

Notes for agents: images must show only public court or government documents, synthetic examples or tool output. Never show client files, matter details, credentials or private AI sessions. Keep file names stable because the README links to them.
