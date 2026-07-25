import { access, readFile } from 'node:fs/promises';
import { constants } from 'node:fs';

const required = [
  'out/main/index.bundle.mjs',
  'out/preload/preload.bundle.cjs',
  'out/config/config.json',
  'out/html/loading.html',
  'out/assets/icon.ico',
  'steam_appid.txt'
];

for (const file of required) {
  await access(file, constants.R_OK);
}

const config = JSON.parse(await readFile('out/config/config.json', 'utf8'));
if (config?.steam?.appId !== 4336770) throw new Error('Unexpected Steam app ID');
if (config?.cache?.assetPathPrefix !== 'game/assets') throw new Error('Unexpected asset cache prefix');
if (!String(config?.gameCanvasUrl ?? '').startsWith('https://')) throw new Error('Game URL must be HTTPS');

const main = await readFile('out/main/index.bundle.mjs', 'utf8');
if (!main.includes('wccache')) throw new Error('Recovered cache protocol is missing');
if (!main.includes('steamworks.js')) throw new Error('Steamworks integration is missing');

console.log('Source verification passed.');
