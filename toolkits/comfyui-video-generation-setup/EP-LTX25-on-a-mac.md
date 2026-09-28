# I ran a 22B video model on a MacBook. Two bugs nearly cost me the whole day.

**Runtime target:** ~35 minutes
**Format:** teaching video, concept first, then the real system
**Series position:** standalone. Assumes the viewer has seen ComfyUI before but has never run a video model locally.

---

## Locked structure

| ID | Section | Run | Becomes a Short | Assumes |
|---|---|---|---|---|
| S1 | Cold open: the render that lied | 0:00-1:00 | **Short A** (best hook) | nothing |
| S2 | The promise, the stakes, CTA 1 | 1:00-2:30 | no | nothing |
| S3 | What I was actually trying to do | 2:30-5:00 | Short B | nothing |
| S4 | Picking the model file, and the 42 GB trap | 5:00-7:30 | Short C | S3 loosely |
| S5 | **MEMORY:** the answer nobody expects | 7:30-10:30 | **Short D** (strong) | nothing |
| S6 | **MEMORY:** your tools are lying to you | 10:30-12:30 | Short E | nothing |
| S7 | **TIME:** where the minutes actually go | 12:30-15:30 | Short F | nothing |
| S8 | **TIME:** longer is cheaper than bigger | 15:30-18:00 | **Short G** (strong) | nothing |
| S9 | **TIME:** three things that are free, one that isn't | 18:00-20:30 | Short H | nothing |
| S10 | **FAILURE 1:** my GPU was doing nothing | 20:30-24:00 | **Short I** (strongest) | nothing |
| S11 | **FAILURE 2:** renders that succeed and are blank | 24:00-27:30 | **Short J** (strong) | nothing |
| S11b | **FAILURE 2b:** the bug hiding behind the bug | 27:30-29:00 | Short K | nothing |
| S12 | **FAILURE 3:** I benchmarked black videos. Twice. | 29:00-31:30 | Short L | S11 helps, not required |
| S13 | The demo *(PLACEHOLDER)* | 31:30-33:30 | Short M | S1-S12 |
| S14 | Close: what I would tell myself at 9am | 33:30-35:00 | no | the video |

**Open loops planted and closed**

| Loop | Planted | Closed |
|---|---|---|
| "I published two rounds of numbers that were completely fake" | S2 | S12 |
| "There's a flag every Mac guide recommends that does nothing" | S5 | S9 |
| "The obvious speed fix made it four times slower" | S7 | S9 |

**The turn:** S9 ends the cost-model half by pointing out that every number so far is worthless if the render silently failed. That earns the failure half. Without it S10 reads as a war story instead of a consequence.

---

## PART 1 — OPEN

### S1 — Cold open: the render that lied
`0:00-1:00`

► SHORT STARTS

`[V]` Full screen: a video player. An 8 second clip plays. It is completely black. Silence.
`[VO]`
> This render took eleven minutes.

`[V]` Cut to the terminal log. Highlight the word `success`.
`[VO]`
> The log says success. No error. No warning. Exit status zero.

`[V]` File inspector: `1.3 MB` next to a black thumbnail. Then cut to a second file, `13 KB`, also black.
`[VO]`
> And the file is blank. Every single pixel is zero.

`[V]` Fast montage: sixteen black thumbnails filling a grid.
`[VO]`
> I made thirty seven of these in one day. Sixteen came out like this.
> Not one of them told me anything was wrong.

► SHORT ENDS

`[V]` Cut to talking head.
`[VO]`
> If you have ever tried to run a video model locally on a Mac and thought.. this thing is just broken.. it might not be. It might be doing this.

`[B-ROLL]` Screen capture of a full render completing with `success` in green, then the black video playing. Capture this before anything else. It is the single most important shot in the video.

---

### S2 — The promise, the stakes, CTA 1
`1:00-2:30`

`[V]` Talking head, then a hardware shot: the Mac, quiet, no fans.
`[VO]`
> So here's the setup. A twenty two billion parameter video model. Audio and video together. Running on a laptop chip.
> No cloud. No rented GPU. No four thousand dollar graphics card.

`[V]` On-screen text: `M5 Pro. 48 GB. LTX-2.5 distilled.`
`[VO]`
> Apple Silicon, forty eight gigs of memory, and a model that ships in a format Apple's GPU cannot actually run.

`[V]` Quick cut through the artifacts: a table of timings, a memory chart, a working duel clip.
`[VO]`
> By the end of this you'll know exactly what it costs. How many minutes per second of video. How much memory. What's expensive, what's free, and the two bugs that will eat your entire afternoon if nobody warns you first.

`[V]` On-screen text card: `every number here came from a render I checked afterwards`
`[VO]`
> Every number I give you came from a real render that I opened afterwards and confirmed was not black.

`[V]` Beat.
`[VO]`
> And I'm telling you that because I did two entire rounds of benchmarking on videos that were completely blank, and I believed the results both times. That story is later.

`[V]` Small subscribe element, bottom corner. No full-screen takeover.
`[VO]`
> If you're trying to get one of these running this week, this will save you a day. Subscribe and you'll get the next one, which is the same thing on a 16 gig machine.

`[RETENTION RISK]` This section is all promise and no payoff. Keep it under ninety seconds and keep the visuals moving. If it drags, cut the hardware shot.

---

## PART 2 — WHAT WAS DONE

### S3 — What I was actually trying to do
`2:30-5:00`

► SHORT STARTS

`[V]` Screen: the LTX-2.5 model card on Hugging Face. Scroll the file list slowly.
`[VO]`
> LTX-2.5 came out in August. Twenty two billion parameters, open weights, and it generates video and matching audio in one pass.

`[V]` Highlight the two big transformer files: `42 GB` each.
`[VO]`
> Here's the first decision that matters. The main model file is forty two gigabytes.

`[V]` On-screen: `48 GB total` with a bar showing 42 of it consumed, and macOS needing the rest.
`[VO]`
> I have forty eight gigs total, and macOS wants about eight of that just to exist. So the headline file was never going to fit. Not close.

`[V]` Scroll to `ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors` — 21.5 GB.
`[VO]`
> What does fit is the distilled version, quantized to int8. Twenty one and a half gigs.
> Distilled means it was trained to get to the same place in fewer steps. Eight instead of thirty or more. So you lose a little quality and you gain a lot of speed, and on a machine like this that trade is not close either.

► SHORT ENDS

`[V]` Terminal: the download running, file sizes ticking up.
`[VO]`
> Full set is about forty gigs. The transformer, a twelve billion parameter text encoder, two small autoencoders for picture and sound, and an upscaler.

`[B-ROLL]` Screen capture of the download completing and the file listing with sizes.

---

### S4 — The install, and the gate that stops you
`5:00-7:30`

► SHORT STARTS

`[V]` Terminal: `hf auth login` succeeding, then a `403` on the actual file.
`[VO]`
> Small thing that will cost you twenty minutes if you hit it.

`[V]` Split screen: `whoami: dappersid` on the left, `403 GatedRepo` on the right.
`[VO]`
> The weights are behind a licence gate. So you log in, it says you're logged in, and then the download still fails with a 403.

`[V]` Highlight `auth.type: oauth`.
`[VO]`
> The reason is that the browser login gives you an OAuth session, and an OAuth session does not carry permission to download gated files. You need an actual access token, generated on the website, pasted in.

`[V]` The Hugging Face model page, the licence agreement button.
`[VO]`
> And separately from that, you have to accept the licence on the model page while logged into the same account. Those are two different things and you need both.

► SHORT ENDS

`[V]` Terminal: python version, torch version, the boot log showing `Device: mps`.
`[VO]`
> Everything else is ordinary. Python 3.12, PyTorch, ComfyUI, point it at the model folder, start it up.

`[V]` Boot log line: `Total VRAM 49152 MB` / `Device: mps` / `Set vram state to: SHARED`
`[VO]`
> It boots. It sees the GPU. It loads the model.
> And then it produced a render so slow I genuinely thought I'd installed something wrong. We'll get there.

`[RETENTION RISK]` Install sections are where people leave. Keep this tight, keep the terminal moving, and do not narrate anything a viewer could read on screen faster than you can say it.

---

## PART 3 — MEMORY

### S5 — The memory answer nobody expects
`7:30-10:30`

► SHORT STARTS

`[V]` On-screen question, big: `How much memory does a 22B video model need?`
`[VO]`
> Everybody asks the memory question first. How much RAM do I need. Will forty eight gigs do it. Should I have bought the ninety six.

`[V]` A table builds row by row: five resolutions, from 608x352 up to 1280x736.
`[VO]`
> So I measured it properly. Same model, same settings, five different picture sizes. Smallest to largest is about four and a half times the pixels.

`[V]` The memory column fills in: 30.1, 30.1, 32.1, 31.7, 32.0.
`[VO]`
> Thirty point one gigs. Thirty point one. Thirty two point one. Thirty one point seven. Thirty two.

`[V]` Freeze. Highlight the whole column with a bracket: `2.1 GB spread`.
`[VO]`
> Four and a half times the pixels. Two gigabytes of difference.

`[V]` Bar: 32 GB filled, 16 GB empty, labelled `unused`.
`[VO]`
> The heaviest thing I rendered all day left sixteen gigs sitting there doing nothing.

► SHORT ENDS

`[V]` Diagram: a big block labelled `model weights 21.5 GB`, a tiny sliver labelled `everything else`.
`[VO]`
> Here's why. The memory is almost entirely the model itself, just sitting in RAM. The actual working data.. the frames, the intermediate maths.. that's the small sliver on the end. Making the picture bigger grows the sliver. It does not grow the block.

`[V]` Anchor text: `you are not budgeting memory. you are budgeting minutes.`
`[VO]`
> Which means the memory question is the wrong question. On this machine you are never budgeting memory. You are budgeting time. And I'll show you exactly how much.

`[V]` Beat, then a teaser card: `--highvram`
`[VO]`
> Oh, and while we're here. There's a flag that half the Mac guides online tell you to add for exactly this reason. It does nothing at all. I'll show you why later.

`[RETENTION RISK]` This is one of the strongest sections. Do not rush the number reveal. Let the 2.1 GB land in silence for a beat.

---

### S6 — Your tools are lying to you
`10:30-12:30`

► SHORT STARTS

`[V]` Terminal: `ps -o rss` output showing `2.1 GB` for the ComfyUI process.
`[VO]`
> Early on I checked memory the way you'd check any process. And it told me a twenty gigabyte model was using two gigs.

`[V]` Zoom on `2.1 GB`. Question mark on screen.
`[VO]`
> Which is impossible. The weights alone are twenty one and a half.

`[V]` Terminal: `vmmap -summary` showing `Physical footprint: 24.4G`.
`[VO]`
> The real number was twenty four gigs. Ten times what the tool reported.

`[V]` Side by side: `ps` says 2.1, `vmmap` says 24.4.
`[VO]`
> On Apple Silicon, resident set size just isn't meaningful for a process like this. Unified memory doesn't work the way that number assumes. If you want the truth, use vmmap and read physical footprint.

► SHORT ENDS

`[V]` Terminal: the vmmap command being run against a live render.
`[VO]`
> Every memory figure in this video came from vmmap, sampled every six seconds while the render was actually running.

`[VO]`
> Worth saying out loud.. if your monitoring tool tells you something impossible, believe the impossibility, not the tool. It cost me twenty minutes of thinking the model hadn't loaded.

`[B-ROLL]` Terminal recording of both commands run back to back on the same PID, so the contradiction is visible in one shot.

---

## PART 4 — TIME

### S7 — Where the minutes actually go
`12:30-15:30`

► SHORT STARTS

`[V]` On-screen: `864x480. 2 seconds of video.` Then a stopwatch: `154 seconds`.
`[VO]`
> Two seconds of video, at roughly four eighty. Two and a half minutes of compute.

`[V]` The full resolution table with times: 106, 117, 154, 232, 314 seconds.
`[VO]`
> Here's the whole curve. Smallest size, a minute forty six. Largest, five minutes fourteen.

`[V]` Overlay: pixel ratios above, time ratios below, lining up.
`[VO]`
> And the interesting bit is how boring it is. One point four times the pixels, one point one times the time. One point five times the pixels, one point five times the time.
> It's basically a straight line. Pixels in, seconds out.

`[V]` On-screen text: `no sweet spot`
`[VO]`
> Which means there's no clever middle setting. No sweet spot somebody discovered where you get free quality. You pay for pixels, at roughly the rate you'd expect.

► SHORT ENDS

`[V]` Correction card, plain: `an earlier version of my own results said otherwise`
`[VO]`
> I'll be honest, my first pass at this said there was a sweet spot. There was a dip in the middle of the curve and I wrote it up as a finding.
> It was fake. The first run in that batch included loading the model from disk, which nothing after it paid. So the first number was inflated and the curve looked like it bent.

`[V]` The corrected curve replacing the old one.
`[VO]`
> Once every run started from the same state, the bend disappeared. Straight line.

`[VO]`
> If you take one methodology thing from this video.. the first measurement in any batch is different from the rest. Throw it away or pay the cost in every run.

`[V]` Terminal: two runs side by side, same prompt, different seed. 156 seconds and 135 seconds.
`[VO]`
> There's one more piece of the time budget worth knowing, because it only hits you sometimes.

`[V]` Highlight the difference: `21 seconds`.
`[VO]`
> Changing the prompt costs you twenty one seconds. Changing the seed costs you nothing extra.

`[V]` Diagram: prompt goes into the text encoder once, then the result is reused.
`[VO]`
> The text encoder runs once per prompt and the answer gets cached. So if you're iterating on a shot, keeping the same words and rolling seeds, you never pay it again. Rewrite one adjective and you're back to twenty one seconds.

`[VO]`
> Which sounds small. It is small. But it means the honest answer to how long does a render take is.. depends whether you touched the prompt. First one is slower. Everything after is the number I gave you.

---

### S8 — Longer is cheaper than bigger
`15:30-18:00`

► SHORT STARTS

`[V]` Two paths on screen. Left: same clip, bigger picture. Right: same picture, longer clip.
`[VO]`
> Say you've got a fixed time budget and you want more video out of it. You can make the picture bigger, or you can make the clip longer. Those cost different amounts and it surprised me which way round.

`[V]` Duration table: 2s = 154s, 4s = 262s, 6s = 403s.
`[VO]`
> Two seconds of video takes a hundred and fifty four seconds. Six seconds takes four hundred and three.

`[V]` Big on-screen: `3x the length = 2.6x the time`
`[VO]`
> So triple the length costs you two point six times the compute. You get a small discount for going long.

`[V]` Next to it: `3x the pixels = 2.9x the time`
`[VO]`
> Triple the pixel count and it costs two point nine. Almost no discount.

`[V]` Both side by side, the length side highlighted.
`[VO]`
> So if you're choosing.. go longer before you go bigger. A six second clip at four eighty costs less than a two second clip at something enormous, and you have four more seconds of usable footage.

► SHORT ENDS

`[V]` Memory column of the duration table: 32.1, 31.9, 32.1.
`[VO]`
> And the memory across all of that? Thirty two point one. Thirty one point nine. Thirty two point one. Tripling the length moved memory by two hundred megabytes.

`[V]` Anchor text again: `minutes, not gigabytes`
`[VO]`
> Same story as before. You're buying minutes.

---

### S9 — Three things that are free, one that isn't
`18:00-20:30`

► SHORT STARTS

`[V]` On-screen list, items appearing as spoken. Item one: `long prompts`.
`[VO]`
> Three things I expected to cost me time, that cost nothing at all.
> First. Long prompts are free.

`[V]` Code: the tokenizer config, `min_length=1024` highlighted.
`[VO]`
> The text encoder pads every prompt out to a thousand and twenty four tokens no matter what you give it. So a three word prompt and a full paragraph of camera direction take exactly the same time. Write the paragraph.

`[V]` Item two: `reference images`.
`[VO]`
> Second. Reference images are nearly free. Three of them, guiding the start, the middle and the end of a clip, cost twenty four percent more time and zero extra memory.

`[V]` Table: 158s, 174s, 196s. Memory column: 32.2, 32.0, 32.0.
`[VO]`
> And that's the cheapest quality you can buy in this whole system. Twenty four percent, and your character actually stays the same person across the shot.

`[V]` Item three: `one reference may be enough`.
`[VO]`
> Third. I put one reference on the very first frame and measured how much it still influenced the last frame, four seconds later. Zero point seven six correlation. It carried most of the way through on its own.

► SHORT ENDS

`[V]` Turn the list over. New header: `and one that is not free`.
`[VO]`
> Now the one that went the other way.

`[V]` Boot log: `text encoder model load device: cpu`.
`[VO]`
> The text encoder, the twelve billion parameter one, loads on the CPU by default. I saw that and thought.. obviously that's a bug, it should be on the GPU, that's free speed.

`[V]` Table: CPU 21s, GPU 46s, GPU pinned 81s.
`[VO]`
> On the CPU it takes twenty one seconds. I moved it to the GPU and it took forty six. I pinned it fully to the GPU and it took eighty one.

`[V]` On-screen: `4x slower`
`[VO]`
> Four times slower. My first theory was memory pressure, so I built a version that runs on the GPU but hands memory back afterwards. Healthy memory, no warnings, still twice as slow.
> The default was right. I was wrong.

`[V]` Callback card: `--highvram`
`[VO]`
> And that flag I mentioned. Highvram. On Apple Silicon it gets read, and then two lines later the code overwrites the setting unconditionally. It does nothing. Every guide that tells you to add it is wrong, and you can see it in the source in about ten seconds.

`[V]` Beat. Tone shift. Slow down.
`[VO]`
> Right. So that's the cost model. Memory is free, time is linear, prompts are free, references are cheap.
> And every single one of those numbers is worthless if the render came out black and you didn't check.

`[VO]`
> Which brings us to the part where I lost most of a day.

`[RETENTION RISK]` This is the hinge. The tonal gear change at the end has to be real. If it's flat, part five reads as a war story instead of a consequence.

---

## PART 5 — FAILURES AND FIXES

### S10 — Failure one: my GPU was doing nothing
`20:30-24:00`

► SHORT STARTS

`[V]` Activity Monitor: CPU at 498%. GPU history graph: flat at the bottom.
`[VO]`
> Five hundred percent CPU. Five cores pinned. And the GPU, on a machine I bought for the GPU, is doing nothing.

`[V]` Terminal: the progress bar sitting at 0/8. A clock ticking past four minutes.
`[VO]`
> This is one sampling step. Step one, of eight. It did not finish in four minutes.

`[V]` The warning in the log, highlighted line by line.
`[VO]`
> And here's the whole story, buried in a warning I nearly scrolled past.
> The operator int mm is not currently supported on the MPS backend, and will fall back to run on the CPU.

`[V]` Diagram: weights in int8, an arrow to the GPU with a red X, an arrow bending down to the CPU.
`[VO]`
> The model weights are int8. Apple's GPU has no int8 matrix multiply. So PyTorch quietly moved that operation to the CPU instead of failing.

`[V]` Diagram animates: data bouncing GPU to CPU to GPU, over and over.
`[VO]`
> And it does that for every quantized layer, thousands of times per step. Copy to the CPU, multiply, copy back.

► SHORT ENDS

`[V]` Highlight the environment variable `PYTORCH_ENABLE_MPS_FALLBACK=1` in the launch script.
`[VO]`
> The part that stings is that this is a safety feature. That fallback exists so unsupported operations don't crash your run. Every Mac guide tells you to switch it on. I switched it on.
> The safety net was the bug.

`[V]` Source code: `pick_operations()` with the capability checks visible.
`[VO]`
> Now here's the good news. ComfyUI already knows how to handle this. When a device can't run a quantized format natively, it unpacks the weights and does ordinary maths on the GPU instead. It's built in.

`[V]` Highlight the three checks: nvfp4, mxfp8, fp8. Then a gap where int8 should be.
`[VO]`
> It checks for three formats. And int8 isn't one of them. So int8 always took the fast path, on hardware with no fast path to take.

`[V]` Code diff: the new capability check.
`[VO]`
> So I added the check. Ran it. Nothing changed.

`[V]` The same CPU-pegged Activity Monitor again.
`[VO]`
> Still five hundred percent CPU. Still crawling.

`[V]` Stack trace on screen, the dispatch line highlighted.
`[VO]`
> So I stopped guessing and traced the actual function call. And the answer is that the flag doesn't matter, because the weight object intercepts the multiply itself and reroutes it before any flag gets read. You have to unpack the weight before you call the function, not ask nicely afterwards.

`[V]` Split screen. Left: 498% CPU, 4 minutes, no result. Right: 7% CPU, 8.4 seconds per step.
`[VO]`
> Three lines of change. CPU drops from four ninety eight to seven percent. A step goes from not finishing in four minutes, to eight point four seconds.

`[V]` On-screen: the first successful render playing.
`[VO]`
> That's the same machine. Same model. Same settings. The only difference is that the work is happening on the chip I bought it for.

`[B-ROLL]` Activity Monitor with the GPU history graph visible, captured during both a broken run and a fixed run. The flat-then-active GPU graph is the money shot for this section.

---

### S11 — Failure two: renders that succeed and are blank
`24:00-27:30`

► SHORT STARTS

`[V]` The black video from S1 plays again. Terminal beside it says `success`.
`[VO]`
> Back to this one. Eleven minutes of compute, log says success, file is black.

`[V]` Two thumbnails side by side, identical filenames, different seeds. One black, one a real shot.
`[VO]`
> Same machine. Same prompt. Same settings. The only thing different between these two is the random seed.

`[V]` On-screen: `seed 1234567 → works` / `seed 2001 → black`
`[VO]`
> One seed gives you a duel. The other gives you eight seconds of nothing. And there is no way to tell which you're getting until it finishes.

`[V]` Grid of sixteen black thumbnails again.
`[VO]`
> Sixteen out of thirty seven. Almost half my day.

► SHORT ENDS

`[V]` Terminal: the audio inspection showing all-zero samples.
`[VO]`
> Now, tracking this down took three wrong guesses, and the wrong guesses are the useful part.

`[V]` On-screen: `guess 1: the audio model` with a strike through it.
`[VO]`
> First guess. It looked like an audio problem, because at first only the audio was broken. So I blamed the audio decoder. Wrong.

`[V]` On-screen: `guess 2: certain resolutions` struck through.
`[VO]`
> Second guess. The failures clustered at particular picture sizes, so I decided it was a size limit. Wrote that down as a finding. Also wrong.

`[V]` A control run: no reference images, plain settings, still black.
`[VO]`
> What broke it open was a control. I ran the simplest possible version, nothing fancy attached, and it came out black too. Which killed every theory that involved something I'd built.

`[V]` Warning line: `Audio waveform contains 192960 non-finite samples`
`[VO]`
> So I put a counter inside the code, and there it is. A hundred and ninety two thousand nine hundred and sixty broken numbers. That's every single sample in the track. Not a few. All of them.

`[V]` Diagram: attention block, NaN spreading forward through the network into the decoder.
`[VO]`
> The source is the attention step. The default attention code on Apple's GPU produces broken numbers at some seeds. Those spread through the rest of the model, the decoder turns broken numbers into zeros, and zeros are black.

`[V]` Terminal: adding `--use-pytorch-cross-attention` to the launch line.
`[VO]`
> The fix is one flag. Switch to PyTorch's own attention instead of ComfyUI's optimized one.

`[V]` Same bad seed, now producing a real render.
`[VO]`
> Same seed that was black five minutes ago. Now it's a duel.

`[V]` On-screen: `costs 19% more time`
`[VO]`
> It costs about nineteen percent more time. Which is not a trade. A render that works and takes nineteen percent longer beats a fast render that's blank.

`[V]` On-screen text card, held: `13 KB is not a video`
`[VO]`
> One practical tell, if you don't want to check every file properly. A real eight second clip at this size is around a megabyte. A black one compresses to about thirteen kilobytes. If your output is suspiciously tiny, it's empty.

---

### S11b — The second bug hiding behind the first
`27:30-29:00`

► SHORT STARTS

`[V]` Terminal: a render completing eight steps, then a red error on the final save. `avcodec_send_frame() returned 22`.
`[VO]`
> Before I found the attention bug, this is what I was actually staring at.

`[V]` Highlight the log: sampler done, decode done, then the crash at save.
`[VO]`
> The model finishes. All eight steps. The picture gets decoded. And then it falls over while writing the file, and you lose the whole render.

`[V]` On-screen: `eleven minutes of compute, discarded at the last step`
`[VO]`
> Eleven minutes of GPU time, thrown away at the final step, because of the audio track.

► SHORT ENDS

`[V]` Split: same audio saved as FLAC, opens fine. Saved as AAC, refuses.
`[VO]`
> Here's the bit I actually enjoyed. The same broken audio saves perfectly as a FLAC file, and gets rejected by the AAC encoder.

`[V]` FLAC waveform: a flat line at zero.
`[VO]`
> Because FLAC quietly rounds broken numbers down to zero and writes a silent track. AAC looks at the same numbers and refuses.

`[V]` On-screen: `one encoder says fine, one says no. that gap is the clue.`
`[VO]`
> And that difference is what told me the numbers were broken rather than just quiet. If both had accepted it I'd have shipped silent audio and never known why.

`[V]` Code: the muxer handing the whole waveform to the encoder in one call.
`[VO]`
> There's a second, separate thing wrong in that same code. The encoder wants audio in fixed size chunks, and it's being handed the entire soundtrack in one go. It only survives when something else happens to break it up first, which is why it looked random.

`[V]` Code diff: the fix, chunking plus a check for broken numbers.
`[VO]`
> Two changes. Feed it the right size chunks. And check for broken numbers first, and if you find them, write silence and warn, instead of destroying the render.

`[VO]`
> That's the difference between a bad clip and no clip. I'd rather have eight seconds of video with no sound than eleven minutes of nothing.

---

### S12 — Failure three: I benchmarked black videos. Twice.
`29:00-31:30`

► SHORT STARTS

`[V]` A clean results table. Reference image timings: 1.02x, 1.30x. Looks perfect.
`[VO]`
> Here's a set of benchmark results. Reference images cost two percent for one, thirty percent for three. Clean numbers. Sensible. They go up in the right order.

`[V]` The videos those numbers came from: all black.
`[VO]`
> Every render behind those numbers was completely black.

`[V]` Second table: 1.42x, 1.24x.
`[VO]`
> So I fixed my graph, ran it again, got a second set. Also plausible. Also black.

`[V]` On-screen, held: `a render time tells you nothing about whether it worked`
`[VO]`
> Both times the compute was real. The GPU worked hard for the full duration. It just produced nothing, and a stopwatch cannot tell the difference.

► SHORT ENDS

`[V]` The verification code: frame count, pixel variation, audio level.
`[VO]`
> So now every run gets opened and checked before its number counts. Three things. Did I get the number of frames I asked for. Do the pixels actually vary, or is the whole thing flat. Is there sound.

`[V]` Terminal output: `frames=193 std=43.35 rms=0.06045 [ok]`
`[VO]`
> A real render has pixel variation somewhere around forty to eighty. A broken one is exactly zero. Not near zero. Zero.

`[V]` The final verified table replacing the fake ones.
`[VO]`
> Third time, with the attention fix and the checking in place, the numbers came out different. Not slightly. The whole shape of the reference cost changed.

`[V]` Terminal: a run finishing in `5.0s`, then another in `0.1s`.
`[VO]`
> And there's a second way the clock lies, which caught me twice as well.

`[V]` Highlight: `Prompt executed in 0.13 seconds`
`[VO]`
> A run came back in a tenth of a second. An eight billion operation render, done instantly. Obviously not.

`[V]` Diagram: the node graph, with cached nodes greyed out.
`[VO]`
> ComfyUI caches every step by its inputs. So if you change the resolution but keep the prompt, it reuses the prompt work. And if you change nothing at all, it hands you the previous result and calls it a success.

`[V]` On-screen: `vary the seed`
`[VO]`
> Which is completely reasonable behaviour, and completely fatal if you're timing things. If you want a cold measurement, change the seed. Every time.

`[VO]`
> If you're benchmarking anything generative, this is the lesson. Measure the output, not the clock. The clock will happily tell you a beautiful story about nothing.

---

## PART 6 — DEMO AND CLOSE

### S13 — The demo
`31:30-33:30`

> **PLACEHOLDER SECTION.** The clip that exists is a proof of concept, not a hero shot. Do not ship this section until there is a render worth pausing on. Script below is written to fit the final piece; adjust the specifics once it exists.

`[V]` **PLACEHOLDER:** final hero clip, full screen, sound up. No talking over the first few seconds.
`[VO]`
> *(silence over the opening of the clip)*

`[V]` Clip continues.
`[VO]`
> Eight seconds. Two characters. Three shot sizes. Rendered on the laptop, in about eleven minutes.

`[V]` The three reference keyframes shown next to the frames they produced.
`[VO]`
> Three reference images, one on the first frame, one on the impact, one on the last. Cost twenty four percent extra, and it's the reason the same two men are recognisably the same two men in every shot.

`[V]` The frame-difference graph, with two spikes marked.
`[VO]`
> And here's the thing I didn't expect. I thought I'd get one long continuous camera move, because that's what interpolating between keyframes usually gives you.
> It cut. Two real hard cuts, at three and a quarter seconds and five and a half. Not a drift. Cuts.

`[V]` The motion graph next to the storyboard beats.
`[VO]`
> Still. Attack. Impact. Hold. It followed the shot list.

`[B-ROLL]` **TO CAPTURE:** the hero render at final quality. Also capture the three keyframes, the ComfyUI graph, and the render actually running with the progress bar.
`[PRODUCTION NOTE]` Do not fake the eleven minute timer. If the final render takes longer, say the real number.

---

### S14 — Close: what I would tell myself at 9am
`33:30-35:00`

`[V]` Talking head. Calm. No music swell.
`[VO]`
> So. If I could go back and tell myself four things before starting.

`[V]` On-screen list building.
`[VO]`
> One. Stop worrying about memory. You have sixteen gigs spare at full tilt. It was never the constraint and it was the only thing I researched before starting.

`[VO]`
> Two. The two bugs that cost me the day were both silent. Not crashes. Not error messages. One made the machine slow, one made the output blank, and neither said a word. On unfamiliar hardware, assume the failures will be quiet.

`[VO]`
> Three. Check your output. Not the exit code, the actual pixels. I wrote up two sets of results that were completely fictional because I trusted a stopwatch.

`[VO]`
> Four, and this is the one I'd actually act on. The cheapest way to make a shot better on this machine is not more resolution. It's a longer prompt and a reference image. One of those is free and the other costs twenty four percent. Resolution is the most expensive thing you can buy and it's the first thing everybody reaches for.

`[V]` The working setup, rendering, quietly.
`[VO]`
> The whole thing runs on a laptop now. Eleven minutes for eight seconds with sound. That was not true a year ago.

`[V]` End card: next episode title. No outro music sting.
`[VO]`
> Next one I'm putting the same model on a sixteen gigabyte machine, which by every number in this video should be impossible. I want to find out where it actually breaks.

---

## Shorts production plan

Publish order is by hook strength, not script order. Each Short ends on the same card: the long video title plus `full breakdown, link below`.

| # | From | Hook line (first 2 seconds) | Why it works | Publish |
|---|---|---|---|---|
| **A** | S10 | "My GPU was doing nothing. Five hundred percent CPU." | Visible absurdity, a number, and a graph that proves it instantly | Day 1 |
| **B** | S11 | "This render took eleven minutes and the file is black." | Mystery plus a visual you cannot look away from | Day 3 |
| **C** | S5 | "Four and a half times the pixels. Two gigabytes of difference." | Counter-intuitive, resolves in fifteen seconds | Day 5 |
| **D** | S8 | "Longer video is cheaper than bigger video. Here's the maths." | Directly useful, saves the viewer money | Day 7 |
| **E** | S9 | "I moved it to the GPU and it got four times slower." | Reversal, everybody assumes the opposite | Day 9 |
| **F** | S12 | "I benchmarked black videos. Twice. The numbers looked perfect." | Confession, high trust, very shareable | Day 11 |
| **F2** | S11b | "One encoder saved this file. The other refused. That gap was the clue." | Detective beat, satisfying in 30 seconds | Day 12 |
| **G** | S6 | "Your process monitor is lying about memory by ten times." | Useful beyond this topic, reaches a wider dev audience | Day 13 |
| **H** | S3 | "The main model file is forty two gigs. I have forty eight." | Sets up a problem in one line | Day 15 |
| **I** | S4 | "You're logged in. It still says 403. Here's why." | Pure search intent, will pick up long tail | Day 17 |
| **J** | S7 | "Two seconds of AI video. Two and a half minutes of compute." | Sets the expectation people actually search for | Day 19 |

Every one of these opens cold. None of them require the long video to make sense. That is the whole point of the section rule.

---

## Production notes

**Must capture before editing**

- Activity Monitor GPU history graph during a broken run and a fixed run. This is the single most valuable shot in the video and it cannot be recreated from stills.
- A full render completing with `success` in the log while the output plays back black.
- `ps` and `vmmap` run against the same process ID in one unbroken take.
- The download completing with real file sizes.
- The hero duel render at final quality, plus its three keyframes.
- The frame-difference graph showing the two cuts.

**Must not be faked**

- The eleven minute render time. If the final version is slower, say the real number.
- The sixteen out of thirty seven figure. It is specific and checkable.
- The pixel variation numbers. Show the actual terminal output, not a recreation.
- The wrong guesses in S11. Three failed hypotheses in order is the most credible material in the video. Do not tidy it into one clean deduction.

**Tone**

Calm throughout. The material is surprising on its own and does not need selling. The only two places to lift energy are the CPU reveal in S10 and the black render reveal in S11, and both work better with a pause before them than with volume.

**Runtime discipline**

If this comes in at twenty eight minutes, ship twenty eight. Do not pad to thirty five. The install section in S4 is the first thing to cut if it drags, and S6 can be folded into S5 if the memory part feels slow.
