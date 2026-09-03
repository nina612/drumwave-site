# dWallet — "Your life creates data"

Scroll-driven brand experience. Six pinned acts, an interactive life timeline,
and 18 wide-angle editorial photographs.

The dWallet mark lives at `assets/img/logo.png` and is used in the nav and in
the closing identity block. Swap that one file to change both.

## Open it

Double-click `index.html`. That's it — no build step, no server.

The page ships with GSAP bundled locally in `assets/js/`, so animation works
with no internet. Two things still reach out to the network:

- **Fonts** (Titillium Web + Open Sans, from Google Fonts) — falls back to
  system sans if offline.
- **Photographs** — see below.

## The photographs

`assets/img/` holds only the logo on first download. The `<img>` tags point at
local files but fall back automatically to the hosted originals, so the page
looks correct straight away as long as you're online.

To make the folder fully self-contained, run once:

```bash
bash download-images.sh
```

That pulls all 18 files listed in `assets/img/manifest.json` into
`assets/img/`. After it finishes, the whole folder works with no internet at
all and can be zipped and passed around freely.

**Before this goes anywhere public**, host the images yourself. The current
URLs point at a generation CDN and should not be treated as permanent.

## What's inside

```
index.html                    the whole experience, one file
assets/img/logo.png           the dWallet mark
assets/img/manifest.json      filename → source URL for all 18 photos
assets/js/gsap.min.js         animation engine (v3.12.5)
assets/js/ScrollTrigger.min.js
download-images.sh            fetches the photos into assets/img/
```

## The timeline

Ages 18 → 70 with an illustrative value curve:

| Age | Value    | Scene                  |
|-----|----------|------------------------|
| 18  | $0       | Graduating             |
| 25  | $820     | First apartment        |
| 32  | $3,460   | Building a life        |
| 40  | $8,900   | Family                 |
| 55  | $18,420  | Child heads to college |
| 70  | $31,800  | Retirement, together   |

Values are illustrative only and labelled as such on the page. Edit the `AGES`,
`VALS`, and `CAPS` arrays near the bottom of `index.html` to change them.

Drag the track to scrub — dragging scrolls the page, so the photo, the number,
and the year ticks stay in sync no matter which input you use. Arrow keys work
too (Shift for five-year jumps).

## Notes

- Respects `prefers-reduced-motion`.
- Responsive to mobile: the nav collapses, the split screen stacks vertically.
- To swap a photo, drop a new file into `assets/img/` under the same name.
