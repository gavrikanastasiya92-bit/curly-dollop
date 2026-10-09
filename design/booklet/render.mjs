// PDF для типографии и PNG-превью: node render.mjs ru
import { createRequire } from 'module';
import { execSync } from 'child_process';
const { chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright');
import { pathToFileURL } from 'url';
import path from 'path';
const lang = process.argv[2] || 'ru';
const file = path.resolve('out', `booklet-${lang}.html`);
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1146, height: 817 }, deviceScaleFactor: 1.6 });
await p.goto(pathToFileURL(file).href, { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts.ready);
await p.pdf({ path: `out/booklet-${lang}.pdf`, preferCSSPageSize: true, printBackground: true });
const sheets = await p.$$('.sheet');
for (let i = 0; i < sheets.length; i++) await sheets[i].screenshot({ path: `out/booklet-${lang}-side${i + 1}.png` });
await b.close();
console.log('ok');
