#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { chromium } from 'playwright';
import { PROFILE, RUNS, parseArgs, probe } from './lib.mjs';

const args = parseArgs(process.argv.slice(2));
if (!args.manifest) throw new Error('--manifest is required');
const manifestPath = path.resolve(args.manifest);
const base = path.dirname(manifestPath);
const raw = JSON.parse(readFileSync(manifestPath, 'utf8'));
const account = args.account ?? raw.account;
if (!/^[A-Za-z0-9._]+$/.test(account ?? '')) throw new Error('Valid account required');
const slides = (raw.slides ?? []).map(p => path.resolve(base, p));
if (slides.length < 2 || slides.length > 20) throw new Error('Carousel requires 2–20 slides');
const crop = raw.crop ?? '1:1';
if (!['1:1','4:5'].includes(crop)) throw new Error('crop must be 1:1 or 4:5');
const ratio = crop === '1:1' ? 1 : 4/5;
for (const file of slides) {
  if (!statSync(file).isFile() || !['.png','.jpg','.jpeg','.mp4'].includes(path.extname(file).toLowerCase())) throw new Error('Invalid slide: '+file);
  const info = probe(file);
  if (Math.abs(info.width/info.height-ratio)>0.002 || info.width < 600) throw new Error(`Slides must be ${crop}, at least 600px: `+file);
}
const captionFile = path.resolve(base, raw.captionFile);
const caption = readFileSync(captionFile, 'utf8').trim();
if (!caption || [...caption].length > 2200) throw new Error('Caption must be 1–2200 characters');
if (typeof raw.aiLabel !== 'boolean') throw new Error('Explicit aiLabel required');
const hash = createHash('sha256');
for (const file of slides) hash.update(readFileSync(file));
hash.update(caption + account + String(raw.aiLabel));
const runId = hash.digest('hex').slice(0,16);
const runDir = path.join(RUNS, 'carousel-'+runId);
const statePath = path.join(runDir, 'state.json');
const profileDir = path.resolve(args.profile_dir ?? PROFILE);
mkdirSync(runDir,{recursive:true,mode:0o700});
let step = 'preflight', context, page;
function record(status, more={}) {
  writeFileSync(statePath,JSON.stringify({status,step,time:new Date().toISOString(),...more},null,2)+'\n',{mode:0o600});
  console.log(step+': '+status);
}
async function evidence(label) {
  await page.screenshot({path:path.join(runDir,label+'.png'),animations:'disabled'});
  writeFileSync(path.join(runDir,label+'.txt'),await page.locator('body').innerText(),{mode:0o600});
}
async function navigate(url) {
  try { await page.goto(url,{waitUntil:'domcontentloaded'}); }
  catch(e) { if (!String(e.message).includes('net::ERR_ABORTED')) throw e; await page.goto(url,{waitUntil:'domcontentloaded'}); }
}
async function button(name) {
  const b=page.getByRole('button',{name,exact:true}).last();
  await b.waitFor({state:'visible',timeout:15000});
  await b.click();
}
async function profileLinks() {
  await navigate('https://www.instagram.com/'+account+'/');
  await page.getByRole('link',{name:'Edit Profile'}).waitFor({state:'visible',timeout:20000});
  await page.locator('a[href*="/p/"]').first().waitFor({timeout:3000}).catch(()=>{});
  return new Set(await page.locator('a[href*="/p/"]').evaluateAll(as=>as.map(a=>new URL(a.href).pathname)));
}
try {
  if (args.check || (!args.stage && !args.publish)) {
    console.log(JSON.stringify({ready:true,account,slides:slides.length,captionCharacters:[...caption].length,aiLabel:raw.aiLabel,runId,publish:false},null,2));
  } else {
    let prior; try { prior=JSON.parse(readFileSync(statePath,'utf8')); } catch {}
    if (prior?.status==='published') throw new Error('Already published: '+prior.url);
    if (prior?.status==='share_clicked') throw new Error('Share status unresolved; check Instagram first');
    mkdirSync(profileDir,{recursive:true,mode:0o700});
    context=await chromium.launchPersistentContext(profileDir,{channel:'msedge',headless:false,viewport:{width:1440,height:1000}});
    page=context.pages()[0]??await context.newPage();
    page.setDefaultTimeout(15000);
    step='account';
    const before=await profileLinks();
    record('ok');
    step='slides';
    await page.getByRole('link',{name:'New post'}).click();
    await page.getByRole('link',{name:/^Post\b/}).click();
    const [chooser]=await Promise.all([page.waitForEvent('filechooser'),button('Select From Computer')]);
    await chooser.setFiles(slides);
    await page.getByRole('heading',{name:'Crop',exact:true}).waitFor({timeout:30000});
    await evidence('uploaded');
    record('ok');
    step='crop_'+crop.replace(':','_');
    await button('Select Crop');
    await button(crop==='1:1' ? '1:1 Crop square icon' : '4:5 Crop portrait icon');
    await evidence(step);
    await button('Next');
    await page.getByRole('heading',{name:'Edit',exact:true}).waitFor();
    record('ok');
    step='edit';
    await evidence('edit');
    await button('Next');
    await page.getByRole('heading',{name:'Create new post',exact:true}).waitFor();
    record('ok');
    step='details';
    const editor=page.locator('[contenteditable="true"]:visible').last();
    await editor.fill(caption);
    await page.getByRole('heading',{name:'Create new post',exact:true}).click();
    if ((await editor.innerText()).trim()!==caption) throw new Error('Caption mismatch');
    const switches=page.getByRole('switch');
    const n=await switches.count();
    if (n!==1) throw new Error('Expected one AI label switch; found '+n);
    const sw=switches.first();
    const checked=await sw.getAttribute('aria-checked')==='true';
    if (checked!==raw.aiLabel) await sw.click();
    if ((await sw.getAttribute('aria-checked')==='true')!==raw.aiLabel) throw new Error('AI label mismatch');
    await evidence('ready_to_share');
    record('ready');
    if (args.stage) {
      record('staged');
      console.log('STAGED '+path.join(runDir,'ready_to_share.png'));
    } else {
      step='share';
      record('share_clicked');
      await button('Share');
      await page.getByText('Your post has been shared.',{exact:true}).waitFor({timeout:180000});
      await button('Done');
      const after=await profileLinks();
      const added=[...after].filter(x=>!before.has(x));
      if (added.length!==1) throw new Error('Published but could not identify one new post: '+added.length);
      const url=new URL(added[0],'https://www.instagram.com').href;
      await navigate(url);
      await page.getByRole('button',{name:'View Insights'}).waitFor({timeout:20000});
      await evidence('published');
      record('published',{url});
      console.log('PUBLISHED '+url);
    }
  }
} catch(e) {
  console.error('TAKEOVER_REQUIRED at '+step+': '+e.message);
  if (page) {
    try { await evidence('failure'); } catch {}
    record(step==='share'?'share_clicked':'failed',{error:e.message});
  }
  process.exitCode=1;
  if (page && process.stdin.isTTY && !args.noHold) {
    console.error('Edge remains open for computer-use takeover. Press Enter when finished.');
    const rl=readline.createInterface({input,output});
    await rl.question('Takeover complete? ');
    rl.close();
  }
} finally { if (context) await context.close(); }
