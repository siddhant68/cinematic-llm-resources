#!/usr/bin/env zsh
# Launch ComfyUI 0.34.0 on Apple Silicon (MPS).
# Tuned for an M5 Pro / 48 GB unified-memory Mac running LTX-2.5 int8-convrot.
set -e
HERE="${0:A:h}"
cd "$HERE"

# Route ops that Metal has no kernel for to the CPU instead of hard-failing.
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Keep tokenizers from spawning threads that fight the sampler.
export TOKENIZERS_PARALLELISM=false

# REQUIRED on Apple Silicon. ComfyUI's default sub-quadratic attention produces
# NaN on MPS at some seeds -- the whole render decodes to black video and silent
# audio, with no error. Verified: seed 2001 at 864x480 is pure black with the
# default and correct with this flag. Costs ~19% time; worth it.
exec "$HERE/venv/bin/python" main.py \
  --use-pytorch-cross-attention \
  --listen 127.0.0.1 \
  --port 8188 \
  "$@"
