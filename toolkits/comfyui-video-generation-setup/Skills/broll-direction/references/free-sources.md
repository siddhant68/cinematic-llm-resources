# Free B-Roll Sources — Reference

Search order: **Pexels → Pixabay → Coverr → Mixkit → Videvo/Dareful**. Stop at the
first usable hit. Generate only after all of these have been tried.

---

## Pexels (API — primary)

Free key from `pexels.com/api`. Rate limits are generous for editing workflows
(hundreds of requests/hour, tens of thousands/month). No attribution required, no
watermark, commercial use allowed.

```
GET https://api.pexels.com/videos/search
Header: Authorization: <API_KEY>
Params: query, per_page (max 80), orientation=landscape|portrait|square,
        size=large|medium|small, page
```

Each result carries `video_files[]` with `width`, `height`, `fps`, `link`. Pick
the largest file at or above your delivery resolution and check `fps` against the
timeline before downloading.

Query tips: two or three concrete words beat a sentence. `"city night traffic"`
works; `"a busy city street at night with cars"` does not. Search the *noun*, not
the concept — searching "productivity" returns stock-photo clichés, searching
"desk lamp notebook" returns usable footage.

---

## Pixabay (API — best for abstract and loops)

Free key from `pixabay.com/api/docs`. No attribution required. Full-resolution
downloads require a free account.

```
GET https://pixabay.com/api/videos/
Params: key, q, video_type=film|animation, category, min_width, per_page
```

Strongest library for **abstract backgrounds, particles, gradients, bokeh, and 4K
loops** — which makes it the first place to look for a background plate before
spending generation credits. Set `video_type=animation` for motion graphics.

Caveat: AI-generated clips are mixed into results without always being obvious.
Check the clip page if provenance matters for your use.

---

## Coverr

`coverr.co` — no API, browse and download. Built originally for website
background loops, so it is unusually good at **ambient, loopable, low-event
footage**. No attribution, commercial use fine, not in YouTube Content ID.

---

## Mixkit

`mixkit.co` — no API. Smaller and more curated than Pexels; genuinely cinematic
clips. **Read the licence on each clip page** — the Mixkit Free License has
per-clip commercial restrictions that the site-level description doesn't convey.

---

## Videvo / Videezy

Fill gaps for motion graphics, overlays, and effects. **Mixed licensing** —
free-tier clips frequently require attribution in the description. Check per clip;
don't assume.

---

## Dareful

4K nature and aerial. CC-BY — **attribution required**. Good quality, but the
credit obligation makes it a last resort for commercial work.

---

## Practical notes

**Grab 4K even for 1080p delivery.** Reframing, punch-ins and stabilisation crops
all cost resolution.

**Look for sets.** Libraries often group several angles from one shoot. Using two
or three clips from the same set makes a sequence feel shot rather than
assembled.

**Match frame rate at download time**, not in the render. Pexels exposes `fps` in
the API response; filter on it rather than conforming later.

**Keep a local catalogue.** Record source URL, licence, download date and a
one-line description of the actual shot content. This makes re-use searchable and
is the only record you'll have if a licence is ever questioned.

---

## Licence quick reference

| Source | Commercial | Attribution | Notes |
|---|---|---|---|
| Pexels | Yes | No | Safest default |
| Pixabay | Yes | No | Contains AI content; no standalone redistribution |
| Coverr | Yes | No | Not in Content ID |
| Mixkit | Per clip | No | Free Licence has restrictions — read each clip |
| Videvo | Per clip | Sometimes | Mixed tiers |
| Videezy | Per clip | Sometimes | Mixed tiers |
| Dareful | Yes | **Yes** | CC-BY |

Free libraries generally do **not** guarantee model or property releases.
Recognisable faces, logos, artwork and private property can carry separate
rights regardless of the footage licence. For anything running as paid media,
move that specific shot to a library that documents releases.
