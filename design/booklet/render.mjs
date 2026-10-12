// PDF для типографии и PNG-превью: node render.mjs booklet-ru
import { createRequire } from 'module';
import { execSync } from 'child_process';
const { chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright');
import { pathToFileURL } from 'url';
import path from 'path';
const name = process.argv[2] || 'booklet-ru';
const file = path.resolve('out', `${name}.html`);
const b = await chromium.launch();
const p = await b.newPage({ viewport: name.startsWith('banya') ? { width: 817, height: 1146 } : name.startsWith('accordion8') ? { width: 1520, height: 817 } : { width: 1146, height: 817 }, deviceScaleFactor: 1.6 });
await p.goto(pathToFileURL(file).href, { waitUntil: 'networkidle' });
await p.evaluate(() => document.fonts.ready);
await p.pdf({ path: `out/${name}.pdf`, preferCSSPageSize: true, printBackground: true });
const sheets = await p.$$('.sheet, .flyer');
for (let i = 0; i < sheets.length; i++) await sheets[i].screenshot({ path: `out/${name}-side${i + 1}.png` });
await b.close();
console.log('ok');
