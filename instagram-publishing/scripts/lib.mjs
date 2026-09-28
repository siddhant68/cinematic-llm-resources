import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFileSync, statSync } from 'node:fs';
import path from 'node:path';

export const ROOT = path.dirname(new URL(import.meta.url).pathname);
export const PROFILE = path.join(ROOT, '.profile');
export const RUNS = path.join(ROOT, '.runs');

export function parseArgs(argv) {
  const out = { check: false, stage: false, login: false, publish: false, noHold: false };
  const keys = new Set(['manifest', 'video', 'cover', 'caption-file', 'account', 'ai-label', 'profile-dir']);
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--check') out.check = true;
    else if (arg === '--stage') out.stage = true;
    else if (arg === '--login') out.login = true;
    else if (arg === '--publish') out.publish = true;
    else if (arg === '--no-hold') out.noHold = true;
    else if (arg.startsWith('--') && keys.has(arg.slice(2))) {
      if (!argv[i + 1] || argv[i + 1].startsWith('--')) throw new Error(`Missing value for ${arg}`);
      out[arg.slice(2).replaceAll('-', '_')] = argv[++i];
    } else throw new Error(`Unknown argument: ${arg}`);
  }
  return out;
}

export function loadConfig(args) {
  let config = {};
  if (args.manifest) {
    const manifestPath = path.resolve(args.manifest);
    config = JSON.parse(readFileSync(manifestPath, 'utf8'));
    const base = path.dirname(manifestPath);
    for (const key of ['video', 'cover', 'captionFile']) {
      if (config[key] && !path.isAbsolute(config[key])) config[key] = path.resolve(base, config[key]);
    }
  }
  if (args.video) config.video = path.resolve(args.video);
  if (args.cover) config.cover = path.resolve(args.cover);
  if (args.caption_file) config.captionFile = path.resolve(args.caption_file);
  if (args.account) config.account = args.account;
  if (args.ai_label) config.aiLabel = parseBoolean(args.ai_label);
  return config;
}

export function parseBoolean(value) {
  if (value === true || value === 'yes' || value === 'true') return true;
  if (value === false || value === 'no' || value === 'false') return false;
  throw new Error('aiLabel must be yes or no');
}

export function probe(file) {
  const raw = execFileSync('ffprobe', [
    '-v', 'error', '-show_entries', 'stream=codec_type,width,height:format=duration',
    '-of', 'json', file,
  ], { encoding: 'utf8' });
  const data = JSON.parse(raw);
  const video = data.streams?.find(s => s.codec_type === 'video');
  if (!video) throw new Error(`No video stream: ${file}`);
  return { width: video.width, height: video.height, duration: Number(data.format.duration) };
}

export function validate(config) {
  if (!/^[A-Za-z0-9._]+$/.test(config.account ?? '')) throw new Error('A valid --account is required');
  for (const key of ['video', 'cover', 'captionFile']) {
    if (!config[key]) throw new Error(`${key} is required`);
    if (!statSync(config[key]).isFile()) throw new Error(`${key} is not a file: ${config[key]}`);
  }
  if (typeof config.aiLabel !== 'boolean') throw new Error('aiLabel must be explicitly yes or no');
  if (path.extname(config.video).toLowerCase() !== '.mp4') throw new Error('Video must be an MP4');
  if (!['.jpg', '.jpeg', '.png'].includes(path.extname(config.cover).toLowerCase())) throw new Error('Cover must be JPG or PNG');
  const video = probe(config.video);
  const cover = probe(config.cover);
  if (video.width / video.height < 0.56 || video.width / video.height > 0.565) {
    throw new Error(`Video must be 9:16; got ${video.width}×${video.height}`);
  }
  if (cover.width / cover.height < 0.56 || cover.width / cover.height > 0.565) {
    throw new Error(`Cover must be 9:16; got ${cover.width}×${cover.height}`);
  }
  if (video.duration < 3 || video.duration > 180) throw new Error(`Unexpected Reel duration: ${video.duration}s`);
  const caption = readFileSync(config.captionFile, 'utf8').trim();
  if (!caption || [...caption].length > 2200) throw new Error('Caption must contain 1–2,200 characters');
  const hash = createHash('sha256');
  hash.update(readFileSync(config.video));
  hash.update(readFileSync(config.cover));
  hash.update(caption);
  hash.update(config.account);
  hash.update(String(config.aiLabel));
  return { ...config, caption, videoInfo: video, coverInfo: cover, runId: hash.digest('hex').slice(0, 16) };
}
