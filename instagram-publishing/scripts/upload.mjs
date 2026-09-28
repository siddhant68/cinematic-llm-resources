#!/usr/bin/env node
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { chromium } from 'playwright';
import { loadConfig, parseArgs, PROFILE, RUNS, validate } from './lib.mjs';

const args = parseArgs(process.argv.slice(2));
const profileDir = path.resolve(args.profile_dir ?? PROFILE);
const baseUrl = 'https://www.instagram.com';
let context;
let page;
let runDir;
let statePath;
let step = 'preflight';

function record(status, more = {}) {
  const state = { status, step, time: new Date().toISOString(), ...more };
  writeFileSync(statePath, JSON.stringify(state, null, 2) + '\n', { mode: 0o600 });
  console.log(`${step}: ${status}`);
}

async function clickButton(name, timeout = 12000) {
  const button = page.getByRole('button', { name, exact: true }).last();
  await button.waitFor({ state: 'visible', timeout });
  await button.click();
}

async function chooseFile(buttonName, file) {
  const [chooser] = await Promise.all([
    page.waitForEvent('filechooser', { timeout: 15000 }),
    clickButton(buttonName),
  ]);
  await chooser.setFiles(file);
}

async function navigate(url) {
  try {
    await page.goto(url, { waitUntil: 'commit', timeout: 30000 });
  } catch (error) {
    // Edge can abort the first navigation while restoring its persistent session.
    if (!String(error.message).includes('net::ERR_ABORTED')) throw error;
    await page.goto(url, { waitUntil: 'commit', timeout: 30000 });
  }
}

async function ensureLoggedIn(account) {
  await navigate(`${baseUrl}/${account}/`);
  await page.getByRole('link', { name: 'Edit Profile' }).waitFor({ state: 'visible', timeout: 30000 });
  const name = await page.getByText(account, { exact: true }).first().textContent();
  if (name !== account) throw new Error(`Expected @${account} profile`);
}

async function reelLinks() {
  await navigate(`${baseUrl}/${config.account}/`);
  await page.getByRole('link', { name: 'Edit Profile' }).waitFor({ state: 'visible' });
  // Existing accounts may have no posts. Give hydrated post links a short chance to appear.
  await page.locator(`a[href*="/${config.account}/reel/"]`).first().waitFor({ timeout: 4000 }).catch(() => {});
  return new Set(await page.locator(`a[href*="/${config.account}/reel/"]`).evaluateAll(
    links => links.map(a => new URL(a.href).pathname),
  ));
}

async function takeEvidence(label) {
  await page.screenshot({ path: path.join(runDir, `${label}.png`), fullPage: false,
    animations: 'disabled' });
  writeFileSync(path.join(runDir, `${label}.txt`), await page.locator('body').innerText(), { mode: 0o600 });
}

async function holdForTakeover() {
  if (args.noHold || !process.stdin.isTTY) return;
  console.error('Edge is still open for computer-use takeover. Press Enter here after the post is handled.');
  const rl = readline.createInterface({ input, output });
  await rl.question('Takeover complete? ');
  rl.close();
}

async function waitForShareOutcome() {
  const outcome = await Promise.race([
    page.getByText('Your reel has been shared.', { exact: true })
      .waitFor({ timeout: 180000 }).then(() => 'shared'),
    page.getByText("Post couldn't be shared", { exact: true })
      .waitFor({ timeout: 180000 }).then(() => 'rejected'),
    page.getByRole('heading', { name: /You submitted an appeal/i })
      .waitFor({ timeout: 180000 }).then(() => 'account_restricted'),
  ]);
  if (outcome === 'rejected') {
    throw new Error("Instagram displayed 'Post couldn't be shared'. Check account status and profile before any retry.");
  }
  if (outcome === 'account_restricted') {
    throw new Error('Instagram says the account is under appeal. Stop uploads until access returns.');
  }
}

let config;
try {
  if (args.login) {
    mkdirSync(profileDir, { recursive: true, mode: 0o700 });
    context = await chromium.launchPersistentContext(profileDir, { channel: 'msedge', headless: false });
    page = context.pages()[0] ?? await context.newPage();
    await navigate(`${baseUrl}/`);
    console.log('Sign in to @cinematic_llm in this Edge window yourself. This separate profile is reused for later uploads.');
    const rl = readline.createInterface({ input, output });
    await rl.question('Press Enter after the profile is open: ');
    rl.close();
    if (args.account) await ensureLoggedIn(args.account);
    console.log(`Profile saved in ${profileDir}`);
    process.exitCode = 0;
  } else {
    config = validate(loadConfig(args));
    runDir = path.join(RUNS, config.runId);
    statePath = path.join(runDir, 'state.json');
    mkdirSync(runDir, { recursive: true, mode: 0o700 });
    if (args.check || (!args.publish && !args.stage)) {
      console.log(JSON.stringify({ ready: true, account: config.account, video: config.videoInfo,
        cover: config.coverInfo, captionCharacters: [...config.caption].length, aiLabel: config.aiLabel,
        runId: config.runId, publish: false }, null, 2));
    } else {
      let prior;
      try { prior = JSON.parse(readFileSync(statePath, 'utf8')); } catch { /* first run */ }
      if (prior?.status === 'published') throw new Error(`Already published: ${prior.url}`);
      if (prior?.status === 'share_clicked') throw new Error('Previous Share click is unresolved. Check Instagram before retrying.');
      mkdirSync(profileDir, { recursive: true, mode: 0o700 });
      context = await chromium.launchPersistentContext(profileDir, {
        channel: 'msedge', headless: false, viewport: { width: 1440, height: 1000 },
        acceptDownloads: false,
      });
      page = context.pages()[0] ?? await context.newPage();
      page.setDefaultTimeout(15000);
      step = 'account';
      await ensureLoggedIn(config.account);
      const before = await reelLinks();
      record('ok');

      step = 'video';
      await page.getByRole('link', { name: 'New post' }).click();
      await page.getByRole('link', { name: /^Post\b/ }).click();
      await chooseFile('Select From Computer', config.video);
      const reelNotice = page.getByText('Video posts are now shared as reels', { exact: true });
      if (await reelNotice.waitFor({ state: 'visible', timeout: 5000 }).then(() => true).catch(() => false)) {
        await clickButton('OK');
      }
      await page.getByRole('heading', { name: 'Crop', exact: true }).waitFor();
      record('ok');

      step = 'crop_9_16';
      await clickButton('Select Crop');
      await clickButton('9:16 Crop portrait icon');
      await takeEvidence('crop_9_16');
      // This explicit 9:16 choice is essential. Instagram previously defaulted to 1:1.
      await clickButton('Next');
      await page.getByRole('heading', { name: 'Edit', exact: true }).waitFor();
      record('ok');

      step = 'cover';
      await chooseFile('Select From Computer', config.cover);
      await takeEvidence('cover');
      if (!(await page.getByText('Sound on', { exact: true }).isVisible())) throw new Error('Sound is not on');
      await clickButton('Next');
      await page.getByRole('heading', { name: 'New reel' }).waitFor();
      record('ok');

      step = 'details';
      const editor = page.locator('[contenteditable="true"]:visible').last();
      await editor.fill(config.caption);
      await page.getByRole('heading', { name: 'New reel' }).click(); // dismiss hashtag suggestions
      const actual = (await editor.innerText()).trim();
      if (actual !== config.caption) throw new Error('Caption mismatch after entry');
      const switches = page.getByRole('switch');
      const count = await switches.count();
      if (count !== 1) throw new Error(`Expected one AI label switch; found ${count}`);
      const aiSwitch = switches.first();
      const checked = await aiSwitch.getAttribute('aria-checked') === 'true';
      if (checked !== config.aiLabel) await aiSwitch.click();
      if ((await aiSwitch.getAttribute('aria-checked') === 'true') !== config.aiLabel) {
        throw new Error('AI label did not reach requested state');
      }
      await takeEvidence('ready_to_share');
      record('ready');

      if (args.stage) {
        record('staged');
        console.log(`STAGED ${path.join(runDir, 'ready_to_share.png')}`);
      } else {
        step = 'share';
        record('share_clicked'); // never blindly retry after this boundary
        await clickButton('Share');
        await waitForShareOutcome();
        await clickButton('Done');
        await page.waitForFunction((oldLinks) => {
          const current = [...document.querySelectorAll(`a[href*="/${location.pathname.split('/')[1]}/reel/"]`)]
            .map(a => new URL(a.href).pathname);
          return current.some(href => !oldLinks.includes(href));
        }, [...before], { timeout: 30000 });
        const after = await reelLinks();
        const added = [...after].filter(link => !before.has(link));
        if (added.length !== 1) throw new Error(`Shared, but could not identify exactly one new Reel (${added.length} found)`);
        const url = new URL(added[0], baseUrl).href;
        await navigate(url);
        await page.getByRole('button', { name: 'View Insights' }).waitFor({ timeout: 20000 });
        await takeEvidence('published');
        record('published', { url });
        console.log(`PUBLISHED ${url}`);
      }
    }
  }
} catch (error) {
  console.error(`TAKEOVER_REQUIRED at ${step}: ${error.message}`);
  if (page && runDir) {
    try { await takeEvidence('failure'); } catch { /* page may have closed */ }
    if (statePath) record(step === 'share' ? 'share_clicked' : 'failed', { error: error.message });
  }
  process.exitCode = 1;
  await holdForTakeover();
} finally {
  if (context) await context.close();
}
