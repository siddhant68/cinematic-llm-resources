#!/usr/bin/env node
// Deterministic release art: keeps every source image's pixels and framing intact.
import { readFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';

const file = process.argv[2];
if (!file) throw new Error('Usage: node art.mjs /absolute/path/art.json');
const manifestPath = path.resolve(file);
const base = path.dirname(manifestPath);
const cfg = JSON.parse(readFileSync(manifestPath, 'utf8'));
const target = path.resolve(base, cfg.outputDir);
mkdirSync(target, { recursive: true });
const browser = await chromium.launch({ channel: 'msedge', headless: true });
const page = await browser.newPage({ deviceScaleFactor: 1 });

function esc(s) { return String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;'); }
function src(rel) {
  const p = path.resolve(base, rel);
  const ext = path.extname(p).toLowerCase();
  const mime = ext === '.png' ? 'image/png' : 'image/jpeg';
  return `data:${mime};base64,${readFileSync(p).toString('base64')}`;
}
const common = `<style>
*{box-sizing:border-box} html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#090c12;color:#f9f9fa;font-family:Arial,Helvetica,sans-serif}
.canvas{position:relative;width:100%;height:100%;background:radial-gradient(circle at 80% 10%,#1d2430,#090c12 48%);overflow:hidden}
.eyebrow{font-size:27px;font-weight:800;letter-spacing:4px;color:#f3c842}
.headline{font-size:75px;line-height:.99;font-weight:900;letter-spacing:-4px;margin:12px 0 0}
.sub{font-size:27px;line-height:1.25;color:#b7bcc8}
.tag{display:inline-block;background:#f3c842;color:#111;padding:10px 17px;border-radius:10px;font-weight:900;font-size:23px;letter-spacing:1px}
.frame{border:3px solid #3d4452;border-radius:18px;overflow:hidden;background:#151820}
.frame img{width:100%;height:100%;object-fit:contain;display:block}
</style>`;
async function render(name, width, height, body) {
  await page.setViewportSize({ width, height });
  await page.setContent(`<!doctype html><html><head>${common}</head><body><div class="canvas">${body}</div></body></html>`);
  await page.locator('img').evaluateAll(imgs => Promise.all(imgs.map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; }))));
  await page.screenshot({ path: path.join(target, name), animations: 'disabled' });
  console.log(path.join(target, name));
}

if (cfg.type === 'two-frame-cover') {
  const body = `<div style="position:absolute;left:65px;top:245px"><div class="eyebrow">${esc(cfg.eyebrow)}</div>
    <div class="headline">${esc(cfg.title).replaceAll('\n','<br>')}</div></div>
    <div class="frame" style="position:absolute;left:65px;top:585px;width:455px;height:810px"><img src="${src(cfg.start)}" style="object-fit:cover"></div>
    <div class="frame" style="position:absolute;left:560px;top:585px;width:455px;height:810px"><img src="${src(cfg.end)}" style="object-fit:cover"></div>
    <div class="tag" style="position:absolute;left:65px;top:1420px">START → END</div>
    <div class="sub" style="position:absolute;left:65px;top:1540px;font-weight:800">${esc(cfg.subtitle)}</div>
    <div style="position:absolute;left:65px;bottom:65px;color:#8590a1;font-size:25px;letter-spacing:3px;font-weight:900">@CINEMATIC_LLM</div>`;
  await render('cover_1080x1920.png',1080,1920,body);
} else if (cfg.type === 'portrait-cover') {
  const body = `<img src="${src(cfg.image)}" style="position:absolute;width:100%;height:100%;object-fit:cover">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.06) 20%,rgba(0,0,0,.08) 48%,rgba(0,0,0,.9) 84%)"></div>
    <div style="position:absolute;left:65px;right:65px;top:1060px"><div class="eyebrow">${esc(cfg.eyebrow)}</div>
    <div class="headline" style="font-size:112px;line-height:.91;text-shadow:0 5px 22px #000">${esc(cfg.title).replaceAll('\n','<br>')}</div>
    <div class="sub" style="margin-top:32px;font-weight:800">${esc(cfg.subtitle)}</div></div>
    <div style="position:absolute;left:65px;bottom:65px;font-size:25px;letter-spacing:3px;font-weight:900">@CINEMATIC_LLM</div>`;
  await render('cover_1080x1920.png', 1080, 1920, body);
} else if (cfg.type === 'feed-safe-cover') {
  // Instagram centres a 4:5 feed preview within a 9:16 Reel.
  // Keep all type in y=285..1635 so the message survives that preview.
  const textTop = Number(cfg.textTop ?? 710);
  const handleTop = Number(cfg.handleTop ?? 1500);
  if (textTop < 285 || textTop > 1200 || handleTop > 1610) throw new Error('Text outside feed safe area');
  const body = `<img src="${src(cfg.image)}" style="position:absolute;width:100%;height:100%;object-fit:cover">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.08) 10%,rgba(0,0,0,.35) 30%,rgba(0,0,0,.72) 54%,rgba(0,0,0,.46) 84%,rgba(0,0,0,.10) 100%)"></div>
    <div style="position:absolute;left:66px;right:66px;top:${textTop}px">
      <div class="eyebrow">${esc(cfg.eyebrow)}</div>
      <div class="headline" style="font-size:115px;line-height:.9;text-shadow:0 5px 24px #000">${esc(cfg.title).replaceAll('\n','<br>')}</div>
      <div class="sub" style="margin-top:32px;font-size:32px;color:#f7f7f8;font-weight:800;text-shadow:0 3px 12px #000">${esc(cfg.subtitle)}</div>
    </div>
    <div style="position:absolute;left:66px;top:${handleTop}px;color:#f3c842;font-size:25px;letter-spacing:3px;font-weight:900;text-shadow:0 3px 10px #000">@CINEMATIC_LLM</div>`;
  await render('cover_1080x1920.png', 1080, 1920, body);
} else if (cfg.type === 'four-panel-cover') {
  if (cfg.images?.length !== 4) throw new Error('four-panel-cover needs four images');
  const panels = cfg.images.map((p,i)=>`<img src="${src(p)}" style="position:absolute;left:${(i%2)*540}px;top:${Math.floor(i/2)*960}px;width:540px;height:960px;object-fit:cover">`).join('');
  const body = `${panels}<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.07),rgba(0,0,0,.1) 42%,rgba(0,0,0,.88) 80%)"></div>
    <div style="position:absolute;left:62px;right:62px;top:1030px"><div class="eyebrow">${esc(cfg.eyebrow)}</div>
    <div class="headline" style="font-size:105px;line-height:.9;text-shadow:0 5px 22px #000">${esc(cfg.title).replaceAll('\n','<br>')}</div>
    <div class="sub" style="margin-top:27px;font-weight:800">${esc(cfg.subtitle)}</div></div>
    <div style="position:absolute;left:62px;bottom:65px;font-size:25px;letter-spacing:3px;font-weight:900">@CINEMATIC_LLM</div>`;
  await render('cover_1080x1920.png',1080,1920,body);
} else if (cfg.type === 'reel-cover') {
  const body = `<div style="position:absolute;left:70px;top:258px"><div class="eyebrow">ONE PHOTO → A SCENE</div><div class="headline">SIX ANGLES.<br><span style="color:#f3c842">ONE PROMPT.</span></div></div>
    <div class="frame" style="position:absolute;left:45px;top:535px;width:990px;height:990px"><img src="${src(cfg.image)}"></div>
    <div style="position:absolute;left:70px;top:1590px" class="tag">SAVE THE PROMPT</div>
    <div style="position:absolute;left:70px;top:1670px" class="sub">One square grid. Six shots to crop apart.</div>
    <div style="position:absolute;left:70px;top:1790px;color:#8590a1;font-size:23px;font-weight:800;letter-spacing:3px">@CINEMATIC_LLM</div>`;
  await render('cover_1080x1920.png', 1080, 1920, body);
} else if (cfg.type === 'reference-carousel') {
  for (let n = 0; n < cfg.slides.length; n++) {
    const item = cfg.slides[n];
    const body = item.original ? `<div class="eyebrow" style="position:absolute;left:55px;top:48px">THE STARTING PHOTO · ${n+1}/${cfg.slides.length}</div>
      <div class="frame" style="position:absolute;left:225px;top:138px;width:630px;height:840px"><img src="${src(item.original)}"></div>
      <div class="tag" style="position:absolute;left:55px;bottom:38px">SAME FACE · SIX LOOKS</div>` :
      `<div class="eyebrow" style="position:absolute;left:55px;top:45px">THE PIN → THE PORTRAIT · ${n+1}/${cfg.slides.length}</div>
      <div class="frame" style="position:absolute;left:52px;top:137px;width:555px;height:832px"><img src="${src(item.result)}"></div>
      <div class="frame" style="position:absolute;left:673px;top:268px;width:340px;height:510px"><img src="${src(item.reference)}"></div>
      <div class="tag" style="position:absolute;left:673px;top:800px">PINTEREST REF</div>
      <div style="position:absolute;left:52px;bottom:32px;color:#acb6c4;font-size:25px;font-weight:700">${esc(item.label ?? '')}</div>`;
    await render(`slide_${String(n+1).padStart(2,'0')}.png`, 1080, 1080, body);
  }
} else if (cfg.type === 'grid-carousel') {
  for (let n = 0; n < cfg.slides.length; n++) {
    const item = cfg.slides[n];
    const body = `<div class="eyebrow" style="position:absolute;left:50px;top:30px">ONE PHOTO · SIX ANGLES · ${n+1}/${cfg.slides.length}</div>
      <div class="frame" style="position:absolute;left:40px;top:118px;width:1000px;height:900px;border:0"><img src="${src(item.image)}"></div>
      <div style="position:absolute;left:50px;bottom:22px;color:#f3c842;font-size:26px;font-weight:900;letter-spacing:2px">${esc(item.label ?? '')}</div>`;
    await render(`slide_${String(n+1).padStart(2,'0')}.png`, 1080, 1080, body);
  }
} else if (cfg.type === 'contain-carousel') {
  for (let n = 0; n < cfg.slides.length; n++) {
    const item = cfg.slides[n];
    const body = item.image ? `<img src="${src(item.image)}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:contain">
      <div style="position:absolute;left:24px;right:24px;top:20px;text-align:center;color:#f3c842;font-size:22px;font-weight:900;letter-spacing:2px;text-shadow:0 2px 10px #000">${esc(item.label ?? '')}</div>` :
      `<div style="position:absolute;left:80px;right:80px;top:260px"><div class="eyebrow">${esc(item.label ?? 'THE FULL PACK')}</div>
        <div class="headline" style="font-size:94px;line-height:.93;margin-top:30px">${esc(item.title ?? '').replaceAll('\n','<br>')}</div>
        <div class="sub" style="font-size:38px;color:#f9f9fa;margin-top:44px">${esc(item.body ?? '')}</div></div>
        <div style="position:absolute;left:80px;bottom:85px;color:#f3c842;font-size:27px;font-weight:900;letter-spacing:2px">@CINEMATIC_LLM</div>`;
    await render(`slide_${String(n+1).padStart(2,'0')}.png`, 1080, 1350, body);
  }
} else throw new Error(`Unknown art type: ${cfg.type}`);
await browser.close();
