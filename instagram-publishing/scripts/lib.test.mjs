import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { loadConfig, parseArgs, parseBoolean } from './lib.mjs';

test('CLI parameters override a manifest and resolve paths beside it', () => {
  const dir = mkdtempSync(path.join(os.tmpdir(), 'ig-manifest-'));
  const manifest = path.join(dir, 'instagram.json');
  writeFileSync(manifest, JSON.stringify({ account: 'old', video: 'final.mp4',
    cover: 'cover.jpg', captionFile: 'caption.txt', aiLabel: true }));
  const args = parseArgs(['--manifest', manifest, '--account', 'cinematic_llm', '--ai-label', 'no', '--check']);
  const config = loadConfig(args);
  assert.equal(config.account, 'cinematic_llm');
  assert.equal(config.aiLabel, false);
  assert.equal(config.video, path.join(dir, 'final.mp4'));
  assert.equal(config.captionFile, path.join(dir, 'caption.txt'));
  assert.equal(args.check, true);
});

test('AI label choice must be explicit', () => {
  assert.equal(parseBoolean('yes'), true);
  assert.equal(parseBoolean('no'), false);
  assert.throws(() => parseBoolean('maybe'), /aiLabel/);
});

test('stage mode is distinct from publish mode', () => {
  const stage = parseArgs(['--stage', '--account', 'cinematic_llm']);
  assert.equal(stage.stage, true);
  assert.equal(stage.publish, false);
});
