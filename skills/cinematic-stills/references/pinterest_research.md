# Pinterest research: finding real faces and cinematic worlds

Pinterest is where the film's **look** is decided. That makes this search the most important creative step, so make it exhaustive. One search is never enough. Earlier runs reviewed 134–167 pins over 4–6 searches per film, plus extra sweeps whenever the creator redirected.

## Setup
- Use a **browser session signed in to Pinterest** (we used Claude's built-in browser). Never sign out or touch the account.
- Every search URL is `https://www.pinterest.com/search/pins/?q=<url-encoded query>&filter_genai=true`. `filter_genai=true` is Pinterest's **"Less AI"** filter. Always keep it on.
- To harvest a search:
  1. Run `scripts/pinterest_harvest.js` with the javascript tool. It scrolls 4 screens and returns about 40–50 lines of `pinId path alt`.
  2. Paste them into `<work>/02_pinterest/<group>/list.txt`.
  3. Run `scripts/contact_sheet.py <group_dir>` to get a numbered sheet, then **look at it**.
  4. Run `scripts/fetch_originals.py <group_dir> <slot> <numbers…> --query "<q>"` for the picks. It downloads the full-size images and appends to `sources.json`. Fill in each `why`.
- Use a Python that has Pillow; the system python3 may not.

## Search like a casting director and a cinematographer, not like a stock site
Build each query from **subject + setting + light/time + medium words**, then vary one axis at a time.

| Axis | Words that pull real photographs |
|---|---|
| Medium | `film still`, `35mm film`, `film photography`, `analog`, `cinestill`, `documentary photography`, `editorial`, `street casting`, `candid` |
| Light / time | `golden hour`, `blue hour`, `overcast`, `noon hard light`, `candlelit`, `lamplight`, `moonlight`, `backlit`, `window light`, `chiaroscuro`, `fluorescent`, `headlights in haze` |
| Mood | `quiet`, `lonely`, `tense`, `intimate`, `melancholic`, `windy`, `dusty`, `rain` |
| Framing | `over the shoulder`, `profile`, `from behind`, `low angle`, `aerial`, `wide shot`, `close up` |

**Faces** (Stage 1 trait sources):
- `street casting portrait <man/woman> <trait> natural light`
- `<trait> portrait 35mm film`
- `candid <emotion> portrait film`
- `<role> portrait weathered`

Traits: freckles, strong nose, heavy brows, deep-set eyes, gap tooth, crooked smile, scar, grey stubble, curly hair, sun-worn skin.

**Worlds** (Stage 2): name the real place type plus the light, as in these past queries that worked:

| Film | Queries |
|---|---|
| Reel 010 | "abandoned gas station desert road dusk film photography" · "haboob dust storm wall approaching road" · "woman road trip desert portrait 35mm film wind hair" |
| HOLD STILL | "dreamy colorful wildflower meadow farm 35mm film wind" · "red vintage car in flower field film photography" · "flower farm dirt lane rolling hills film photography" |
| STAY | "desert bus stop dawn film photography" · "headlights desert highway dawn haze film photography" · "over the shoulder shot film still couple golden hour" · "emotional close up film still woman teary eyes golden light" |
| Violet | "ancient stone chamber oil lamp night film still" · "sheer curtain moonlight window night" · "candlelit portrait chiaroscuro 35mm" · "woman trying not to smile candid" · "woman holding back tears smiling candid film" |

**Expressions** (one search per emotional beat): `<emotion> candid close up film`, `woman blushing looking down candid portrait`, `man serious profile looking out window night`.

**Wardrobe and props:** `<garment> <era> <fabric>`, `<prop> in hand close up film`. Product-shot results are common here; if every result is a catalogue shot, skip it and let ChatGPT draw the prop.

## Exhaustive means
- At least **4–8 searches per scene**: the world, the light, each key framing, and each expression beat.
- **Rephrase whenever a page is dominated by AI renders, stock or the wrong era.** Swap the medium word, add or remove the time of day, try the profession or place name in another way.
- **Go wider than the script's literal words.** The ritual or architecture from another culture, a documentary photo of the real place type, a film still with the same light. Taste is the job; ChatGPT cannot choose it for you.

## Keep and reject
**Keep:**
- **Faces with character:** asymmetry, an unusual nose, uneven brows, real pores, freckles, fine lines, redness, untidy hair, a caught (not posed) expression.
- **Worlds that look photographed:** motivated light from a visible source, real wear, clutter and weather, a composition you would frame as a film still.

**Reject:**
- **AI tells:** plastic skin, glassy eyes, perfect symmetry, melted hands, over-smooth bokeh, impossible light.
- **Text, logos, watermarks**, and Facebook or stock credits burned into the image.
- **Celebrities, known models and actors.** For a show or book adaptation, never the cast. Show stills may be broken down **only** for a room or costume, with T2 (no faces).
- Beauty-retouched campaign images.
- Images where the whole frame is a single famous shot (copying it).

**How many to keep:**
- per character: 3–4 trait pins, each for a different trait (nose and lips / eyes and face shape / hair / wardrobe and wind);
- per beat: 1–2 world pins plus 1 light pin;
- per emotional beat: 1 expression pin.

Make a shortlist board with `scripts/make_board.py --fit contain` and show it at the checkpoint.

## Records
`<work>/02_pinterest/sources.json` holds `{slot, pin, orig, query, file, why}` for every kept pin, where `why` says what the pin is FOR ("world: planted flower bands; the field's palette"). **Pins are references only:**
- never attached when generating our images;
- never published (carousel, GitHub pack, captions);
- never uploaded to Higgsfield.

A tutorial may show a few, labelled "PINTEREST".
