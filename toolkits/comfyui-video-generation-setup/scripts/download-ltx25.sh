#!/usr/bin/env zsh
# Download the LTX-2.5 distilled int8-convrot model set (~40 GB).
# Repo paths mirror ComfyUI's models/ layout, so --local-dir models lands
# every file in exactly the right subfolder.
# Requires: `hf auth login` first (Lightricks/LTX-2.5 is a gated repo).
set -e
HERE="${0:A:h}"
export HF_HUB_ENABLE_HF_TRANSFER=0   # hf-xet already handles chunked transfer

"$HERE/venv/bin/hf" download Lightricks/LTX-2.5 \
  diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors \
  text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors \
  vae/ltx-2.5-video-vae-bf16.safetensors \
  vae/ltx-2.5-audio-vae-bf16.safetensors \
  latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors \
  model_patches/ltx-2.5-duration-head-bf16.safetensors \
  --local-dir "$HERE/models"

echo
echo "Done. Downloaded into $HERE/models :"
find "$HERE/models" -name "*ltx-2.5*" -o -name "*gemma4-12b-with-proj*" | sort
