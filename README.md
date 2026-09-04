# dWallet — "Your life creates data"

Scroll-driven brand experience. Six pinned acts, an interactive life timeline,
and 32 wide-angle editorial photographs.

The dWallet mark lives at `assets/img/logo.png` and is used in the nav and in
the closing identity block. Swap that one file to change both.

## Open it

Double-click `index.html`. That's it — no build step, no server.

The page ships with GSAP and every photograph locally, so it works with no
internet. One thing still reaches out to the network: **fonts** (Titillium Web
+ Open Sans, from Google Fonts), which fall back to system sans if offline. To
close that last gap, see *Packaging it as one file* below.

## The photographs

All 32 images are committed under `assets/img/`, so the folder is
self-contained — no fetch step, and it works with no internet.

`download-images.sh` and `assets/img/manifest.json` are left over from when the
photos were pulled from a generation CDN at load time. Nothing needs them now.

## What's inside

```
index.html                    the whole experience, one file
assets/img/                   the mark, and all 32 photographs
assets/js/gsap.min.js         animation engine (v3.12.5)
assets/js/ScrollTrigger.min.js
build-standalone.py           folds the whole site into one shareable file
download-images.sh            vestigial — the photos are committed now
```

## Packaging it as one file

To hand the site to someone who can't be given a link — an email attachment, a
stick, a laptop with no wifi:

```bash
python3 build-standalone.py
```

That writes `drumwave-standalone.html`, about 7MB, with every asset folded in
as a data URI: all 32 images, both GSAP scripts, and the fonts. Nothing is
fetched when it opens. The script refuses to write a file that still has an
external `src` or `href`, so a silently-broken build isn't possible.

It is not committed — at 7MB it is larger than the rest of the repo put
together, and it is a build product. Rebuild it after editing `index.html`;
it takes under a second.

Two things to know:

- **Only the latin font subsets are embedded** (16 faces, not 48). That keeps
  the fonts near 490KB instead of some 1.5MB. Non-latin text would fall back —
  there is none on the page today.
- **The whole 7MB loads before the first paint**, where the hosted site streams
  4.8MB progressively as you scroll. Prefer the link when there is one.

Downloaded fonts are cached in `.build-cache/` (gitignored), so rebuilds work
offline.

### If the file won't open

Lightweight HTML previewers — mail clients, chat file previews, Quick Look —
tend to hang on 7MB of base64 in a single document. That is the viewer, not
the file. Open it in a real browser instead:

```bash
open -a "Google Chrome" drumwave-standalone.html
```

For a version those previewers will open, re-encode the photographs:

```bash
python3 build-standalone.py --light
```

That writes `drumwave-standalone-light.html` at about 3.7MB — photos capped at
1400px and JPEG quality 68. Fine for a quick look; use the full build for
anything anyone judges the photography on.

## Two openings, one file

The opening run plays on its own clock when the reader arrives. Add `?scroll` to
the URL and it is scrubbed instead — the reader moves it themselves, one screen of
scroll to about two seconds of the run:

```
index.html            the run plays itself
index.html?scroll     the run follows the scroll
```

`#scroll` works too, which is what the offline single file needs (a `file://` URL
keeps the hash). Changing only the hash on a page that is already open does not
reload it, so the switch needs a fresh load either way.

It is one file rather than two copies on purpose: a duplicate would have drifted
from this one the first time either was edited. Two things differ under the flag,
and nothing else does:

- **The pin is 5.5 screens instead of one**, and the timeline is scrubbed across
  it rather than played.
- **The final hold drops from 5s to 1s.** It exists so the run does not restart
  the instant it ends; scrubbed there is no restart, and five seconds of held
  frame becomes five seconds of scrolling where nothing moves.

Snapping lets go of the opening in this mode — otherwise one gesture from the top
would carry the reader past the whole run. It picks up again at the plan screen.

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
