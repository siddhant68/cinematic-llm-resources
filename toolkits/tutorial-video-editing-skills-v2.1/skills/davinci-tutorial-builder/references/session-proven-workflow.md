# Session-proven Resolve workflow

- Verify live Resolve product/version, project, current timeline, start/end frame, track counts, media state, and supported methods before editing.
- Duplicate the approved timeline before replacing a long underlying layer. Read back per-track item counts plus the new clip’s name, absolute start/end, duration, transform, opacity, and composite mode.
- A full-length presenter composite may be used as a replacement layer when originals remain immutable, the intermediate has the exact expected frame count, and overlays/audio remain unchanged.
- For changing environments, align geometry first; grade the isolated foreground per environment; despill separately; then add restrained background-colored edge wrap.
- Pin a known video render preset. On Resolve builds without readable render settings, `ExportVideo:true` does not prove an inherited audio-only preset is gone.
- If guarded rendering requires a temporary path, use the actual system `TMPDIR`, verify output before deleting the job, then move it to a new non-overwriting production path.
- Require exact frame/duration agreement plus video and audio streams. Resolve job status `Complete` is not delivery proof.
- QC again after every downstream trim, caption burn, opening replacement, audio rebuild, or remux. Preserve the prior master checksum and export the execution trace.
