"""Буклет Ак-Тенгир: А4, гармошка в 2 сгиба, 3 панели на сторону. Система «Актенгир 2».

Тексты — texts/<язык>.json. Результат — out/booklet-<язык>.html; PDF и превью делает render.mjs.
Запуск из этой папки:  python3 build.py ru   (или en, ky; без аргумента — все языки с готовыми текстами)

Схема листа (обрезной формат 297×210, вылеты по 3 мм, итого 303×216):
  сторона 1:  [1 обложка | 2 светлое пространство | 3 форматы]
  сторона 2:  [6 задняя обложка: ретриты и бронь | 4 баня и кухня | 5 досуг и что рядом]
Панель 6 печатается на обороте панели 3 и при сложенной гармошке оказывается снизу.
"""
import html, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMG = "../../../site/img/"

def e(t):
    return html.escape(t, quote=False)

CSS = """
@import url(../fonts/fonts.css);
@page{size:303mm 216mm;margin:0}
:root{--milk:#F3F1EC;--sand:#E9E5DD;--ink:#2B2A28;--grey:#6A655D;--line:#D3CEC4;
--serif:"Cormorant Garamond",Georgia,serif;--sans:"Montserrat",Arial,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#fff}
body{font-family:var(--sans);font-weight:400;color:var(--grey);font-size:7.6pt;line-height:1.62;
-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:303mm;height:216mm;display:grid;grid-template-columns:102mm 99mm 102mm;overflow:hidden;page-break-after:always;position:relative}
.sheet:last-child{page-break-after:auto}
.p{position:relative;height:216mm;padding:13mm 7mm 12mm;display:flex;flex-direction:column;gap:4.2mm;overflow:hidden;background:var(--milk)}
.p.l{padding-left:10mm}.p.r{padding-right:10mm}
.sand{background:var(--sand)}
.dark{background:var(--ink);color:#B9B3A8}
h1,h2,h3{font-family:var(--serif);font-weight:500;color:var(--ink);line-height:1.08;text-wrap:balance}
h2{font-size:19pt}
h3{font-size:14pt}
.dark h2,.dark h3{color:var(--milk)}
.it{font-family:var(--serif);font-style:italic;font-size:11pt;color:var(--ink);line-height:1.25;margin-top:-2mm}
.dark .it{color:var(--milk)}
.caps{font-size:6pt;font-weight:500;letter-spacing:.17em;text-transform:uppercase;color:var(--ink)}
.dark .caps{color:var(--milk)}
.ph{background:var(--sand);overflow:hidden;flex:none}
.ph img{width:100%;height:100%;object-fit:cover;display:block;filter:saturate(.82) contrast(.96)}
.rows{list-style:none;border-top:.25mm solid var(--line)}
.rows li{display:flex;justify-content:space-between;align-items:baseline;gap:3mm;padding:1.7mm 0;border-bottom:.25mm solid var(--line)}
.rows b{font-weight:500;color:var(--ink)}
.rows .v{white-space:nowrap;color:var(--ink);font-weight:500}
.dark .rows{border-color:#4A4844}.dark .rows li{border-color:#4A4844}
.dark .rows b,.dark .rows .v{color:var(--milk)}
.stay li{display:grid;grid-template-columns:1fr auto;column-gap:3mm;row-gap:.2mm;padding:2.1mm 0}
.stay .n{font-family:var(--serif);font-size:11.5pt;font-weight:500;color:var(--ink);line-height:1.15}
.stay .d{font-size:6.6pt;grid-column:1}
.stay .pr{grid-column:2;grid-row:1/3;text-align:right;align-self:center;font-weight:500;color:var(--ink);white-space:nowrap;line-height:1.35}
.stay .pr small{display:block;font-weight:400;font-size:6pt;color:var(--grey)}
.box{border:.25mm solid var(--line);padding:3mm 3.4mm;display:grid;gap:1mm}
.small{font-size:6.6pt}
.logo{display:block}
.mt-auto{margin-top:auto}
/* обложка */
.cover{padding:0;color:#fff;background:#41566a}
.cover>img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:55% 50%}
.cover:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(20,24,28,.42) 0%,rgba(20,24,28,.18) 40%,rgba(20,24,28,0) 55%,rgba(20,24,28,0) 60%,rgba(20,24,28,.45) 100%)}
.cover .in{position:relative;z-index:1;height:100%;display:flex;flex-direction:column;align-items:center;text-align:center;padding:19mm 12mm 16mm 15mm}
.cover h1{color:#fff;font-size:25pt;letter-spacing:.06em;margin-top:6mm}
.cover .sub{font-family:var(--serif);font-style:italic;font-size:13pt;line-height:1.25;margin-top:3mm;max-width:62mm}
.cover .place{margin-top:auto;font-size:6.2pt;font-weight:500;letter-spacing:.18em;text-transform:uppercase}
/* задняя обложка */
.qr{display:flex;gap:6mm}
.qr figure{display:grid;gap:1.6mm;justify-items:center}
.qr img{width:21mm;height:21mm;display:block}
.quote{font-family:var(--serif);font-style:italic;font-size:15pt;line-height:1.2;color:var(--milk)}
"""

def rows(items):
    return '<ul class="rows">' + "".join(f'<li><b>{e(a)}</b><span class="v">{e(b)}</span></li>' for a, b in items) + "</ul>"

def page(t):
    stay = '<ul class="rows stay">' + "".join(
        f'<li><span class="n">{e(n)}</span><span class="d">{e(d)}</span><span class="pr">{e(p)}<small>{e(u)}</small></span></li>'
        for n, d, p, u in t["stay_rows"]) + "</ul>"
    facts = '<ul class="rows">' + "".join(f"<li><span>{e(f)}</span></li>" for f in t["facts"]) + "</ul>"
    contacts = '<ul class="rows">' + "".join(
        f'<li><span class="caps" style="font-size:5.6pt">{e(a)}</span><span class="v">{e(b)}</span></li>' for a, b in t["contacts"]) + "</ul>"
    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8">
<title>Ак-Тенгир — буклет ({t['lang'].upper()})</title><style>{CSS}</style></head><body>

<section class="sheet">
  <div class="p l cover"><img src="{IMG}hero-30.jpg" alt="">
    <div class="in"><img class="logo" src="{IMG}logo-white.png" alt="Ak-Tengir" style="width:24mm">
      <h1>{e(t['cover_title'])}</h1><p class="sub">{e(t['cover_sub'])}</p><p class="place">{e(t['cover_place'])}</p></div></div>

  <div class="p sand">
    <img class="logo" src="{IMG}logo-color.png" alt="" style="width:13mm">
    <h2>{e(t['about_h'])}</h2>
    <p>{e(t['about_p1'])}</p>
    <p>{e(t['about_p2'])}</p>
    <div class="ph" style="height:46mm"><img src="{IMG}n-19.jpg" alt=""></div>
    {facts}
    <div class="mt-auto" style="display:flex;align-items:baseline;gap:3mm"><span style="font-family:var(--serif);font-size:26pt;color:var(--ink);line-height:1">{e(t['rating'])}</span><span class="small">{e(t['rating_note'])}</span></div>
  </div>

  <div class="p r">
    <h2>{e(t['stay_h'])}</h2>
    <p class="it">{e(t['stay_sub'])}</p>
    <div class="ph" style="height:44mm"><img src="{IMG}y-d1.jpg" alt="" style="object-position:50% 60%"></div>
    {stay}
    <p class="small">{e(t['stay_year'])}</p>
    <div class="box mt-auto"><span class="caps">{e(t['terms_h'])}</span><span class="small">{e(t['terms_p'])}</span></div>
  </div>
</section>

<section class="sheet">
  <div class="p l dark">
    <p class="quote">{e(t['retreat_quote'])}</p>
    <div class="ph" style="height:38mm"><img src="{IMG}r-fire.jpg" alt=""></div>
    <h3>{e(t['retreat_h'])}</h3>
    <p>{e(t['retreat_p'])}</p>
    <div class="mt-auto" style="display:grid;gap:3.4mm">
      <img class="logo" src="{IMG}logo-white.png" alt="" style="width:13mm">
      <span class="caps">{e(t['book_h'])}</span>
      {contacts}
      <div class="qr"><figure><img src="../qr-wa.svg" alt=""><span class="caps" style="font-size:5.6pt">{e(t['qr_wa'])}</span></figure>
        <figure><img src="../qr-site.svg" alt=""><span class="caps" style="font-size:5.6pt">{e(t['qr_site'])}</span></figure></div>
    </div>
  </div>

  <div class="p sand">
    <div class="ph" style="height:40mm"><img src="{IMG}b-inside.jpg" alt=""></div>
    <h2>{e(t['banya_h'])}</h2>
    <p class="it">{e(t['banya_sub'])}</p>
    <p>{e(t['banya_p'])}</p>
    {rows(t['banya_rows'])}
    <p class="small" style="margin-top:-2mm">{e(t['banya_note'])}</p>
    <h3 style="margin-top:2mm">{e(t['food_h'])}</h3>
    <p>{e(t['food_p'])}</p>
    {rows(t['food_rows'])}
  </div>

  <div class="p r">
    <div class="ph" style="height:40mm"><img src="{IMG}n-3.jpg" alt=""></div>
    <h3>{e(t['leisure_h'])}</h3>
    <p>{e(t['leisure_p'])}</p>
    <h2 style="margin-top:2mm">{e(t['near_h'])}</h2>
    {rows(t['near_rows'])}
    <p class="small">{e(t['near_note'])}</p>
    <div class="mt-auto" style="display:grid;grid-template-columns:1fr 1fr;gap:1.2mm"><div class="ph" style="height:30mm"><img src="{IMG}near-skazka.jpg" alt=""></div><div class="ph" style="height:30mm"><img src="{IMG}near-jeti.jpg" alt=""></div></div>
  </div>
</section>
</body></html>"""

if __name__ == "__main__":
    langs = sys.argv[1:] or [p.stem for p in (HERE / "texts").glob("*.json")]
    (HERE / "out").mkdir(exist_ok=True)
    for lang in langs:
        t = json.loads((HERE / "texts" / f"{lang}.json").read_text(encoding="utf-8"))
        (HERE / "out" / f"booklet-{lang}.html").write_text(page(t), encoding="utf-8")
        print("out/booklet-%s.html" % lang)
