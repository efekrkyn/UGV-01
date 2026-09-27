// Frame-by-frame capture of out/film.html through the Chrome DevTools Protocol (Node >= 22: global WebSocket).
// usage: node render.mjs <url> <frames dir> [first frame] [last frame]   (30 fps, 1920x1080, JPEG q92)
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, dir, first = '0', last] = process.argv.slice(2);
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const PORT = 9333, FPS = 30;
mkdirSync(dir, { recursive: true });
const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'ugv-film-'))}`,
  '--window-size=1920,1080', '--hide-scrollbars', '--force-device-scale-factor=1', '--use-angle=metal', '--enable-gpu',
  '--ignore-gpu-blocklist', '--no-first-run', '--no-default-browser-check', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let k = 0; k < 100 && !target; k++) {
  await sleep(100);
  try { target = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(x => x.type === 'page'); } catch { /* starting */ }
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0;
const pending = new Map();
ws.addEventListener('message', e => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const n = ++id;
  pending.set(n, m => (m.error ? reject(new Error(`${method}: ${m.error.message}`)) : resolve(m.result)));
  ws.send(JSON.stringify({ id: n, method, params }));
});
const evaluate = async expression => (await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true })).result.value;

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
for (let k = 0; k < 600 && !(await evaluate('window.__filmReady === true').catch(() => false)); k++) await sleep(200);
const total = Math.round((await evaluate('JSON.parse(document.getElementById("timeline").textContent).duration_s')) * FPS);
console.log(`gpu: ${await evaluate('window.__gpu')}; frames ${first}..${last ?? total - 1} of ${total}`);
const t0 = Date.now();
for (let f = Number(first); f <= Number(last ?? total - 1); f++) {
  await evaluate(`renderAt(${f / FPS})`);
  const { data } = await send('Page.captureScreenshot', { format: 'jpeg', quality: 92, optimizeForSpeed: true });
  writeFileSync(join(dir, `f${String(f).padStart(5, '0')}.jpg`), Buffer.from(data, 'base64'));
  if (f % 150 === 0) console.log(`frame ${f} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
}
ws.close();
chrome.kill();
