"""Буклет Ак-Тенгир: А4, гармошка в 2 сгиба, 3 панели на сторону. Система «Актенгир 2».

Тексты — texts/<язык>.json. Результат — out/booklet-<язык>.html; PDF и превью делает render.mjs.
Запуск из этой папки:  python3 build.py ru   (или en, ky; без аргумента — все языки с готовыми текстами)

Схема листа (обрезной формат 297×210, вылеты по 3 мм, итого 303×216):
  сторона 1:  [1 обложка | 2 светлое пространство | 3 форматы]
  сторона 2:  [6 задняя обложка: ретриты и бронь | 4 баня и кухня | 5 досуг и что рядом]
Панель 6 печатается на обороте панели 3 и при сложенной гармошке оказывается снизу.
Все панели на одном молочном фоне. В каждой панели одно фото тянется (.grow) и забирает свободное
место, поэтому пустот внизу нет при любой длине текста — это важно для EN и KY, где строки длиннее.
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
:root{--milk:#F3F1EC;--bg:var(--milk);--sand:#E9E5DD;--ink:#2B2A28;--grey:#6A655D;--line:#D3CEC4;
--serif:"Cormorant Garamond",Georgia,serif;--sans:"Montserrat",Arial,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:var(--bg)}
body{font-family:var(--sans);font-weight:400;color:var(--grey);font-size:7.6pt;line-height:1.62;
-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sheet{width:303mm;height:216mm;display:grid;grid-template-columns:102mm 99mm 102mm;overflow:hidden;page-break-after:always;background:var(--bg)}
.sheet:last-child{page-break-after:auto}
.p{position:relative;height:216mm;padding:13mm 7mm 12mm;display:flex;flex-direction:column;gap:4mm;overflow:hidden}
.p.l{padding-left:10mm}.p.r{padding-right:10mm}
h1,h2,h3{font-family:var(--serif);font-weight:500;color:var(--ink);line-height:1.08;text-wrap:balance}
h2{font-size:19pt}
h3{font-size:14pt}
.it{font-family:var(--serif);font-style:italic;font-size:11pt;color:var(--ink);line-height:1.25;margin-top:-2mm}
.caps{font-size:6pt;font-weight:500;letter-spacing:.17em;text-transform:uppercase;color:var(--ink)}
.ph{background:var(--sand);overflow:hidden;flex:none}
.ph.grow{flex:1 1 0;min-height:24mm}
.ph img{width:100%;height:100%;object-fit:cover;display:block;filter:saturate(.82) contrast(.96)}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:1.2mm;flex:1 1 0;min-height:24mm}
.pair .ph{height:100%}
.rows{list-style:none;border-top:.25mm solid var(--line)}
.rows li{display:flex;justify-content:space-between;align-items:baseline;gap:3mm;padding:1.6mm 0;border-bottom:.25mm solid var(--line)}
.rows b{font-weight:500;color:var(--ink)}
.rows .v{white-space:nowrap;color:var(--ink);font-weight:500}
.stay li{display:grid;grid-template-columns:1fr auto;column-gap:3mm;row-gap:.2mm;padding:2mm 0}
.stay .n{font-family:var(--serif);font-size:11.5pt;font-weight:500;color:var(--ink);line-height:1.15}
.stay .d{font-size:6.6pt;grid-column:1}
.stay .pr{grid-column:2;grid-row:1/3;text-align:right;align-self:center;font-weight:500;color:var(--ink);white-space:nowrap;line-height:1.35}
.stay .pr small{display:block;font-weight:400;font-size:6pt;color:var(--grey)}
.box{border:.25mm solid var(--line);padding:3mm 3.4mm;display:grid;gap:1mm}
.small{font-size:6.6pt}
.logo{display:block}
/* обложка: фото сверху растворяется в молочном фоне, ниже знак и название */
.p.cover{padding:0}
.cover .photo{position:relative;flex:1 1 0;min-height:0}
.cover .photo img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:55% 40%;filter:saturate(.82) contrast(.96)}
.cover .photo:after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:48%;background:linear-gradient(180deg,transparent 0%,color-mix(in srgb,var(--bg) 75%,transparent) 60%,var(--bg) 92%)}
.cover .in{display:flex;flex-direction:column;align-items:center;text-align:center;gap:3mm;padding:0 12mm 14mm 15mm;margin-top:-16mm;position:relative}
.cover h1{font-size:25pt;letter-spacing:.06em;margin-top:2mm}
.cover .sub{font-family:var(--serif);font-style:italic;font-size:13pt;line-height:1.25;color:var(--ink);max-width:66mm}
.cover .place{margin-top:5mm}
/* задняя обложка */
.qr{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.qr figure{display:grid;gap:1.4mm;justify-items:center}
.qr img{width:100%;max-width:21mm;aspect-ratio:1;display:block}
.qr .caps{font-size:5.4pt}
.quote{font-family:var(--serif);font-style:italic;font-size:15pt;line-height:1.2;color:var(--ink)}
"""

# Варианты фона: milk — молочный по системе «Актенгир 2», blue — нежно-голубой в тон неба на обложке
VARIANTS = {
    "milk": "",
    "blue": ":root{--bg:#E3EAEF;--sand:#D5DFE6;--line:#C3CFD8}",
}

def rows(items):
    return '<ul class="rows">' + "".join(f'<li><b>{e(a)}</b><span class="v">{e(b)}</span></li>' for a, b in items) + "</ul>"

def ph(src, cls="grow", style=""):
    return f'<div class="ph {cls}"><img src="{IMG}{src}" alt=""{f" style={chr(34)}{style}{chr(34)}" if style else ""}></div>'

def page(t, variant="milk"):
    stay = '<ul class="rows stay">' + "".join(
        f'<li><span class="n">{e(n)}</span><span class="d">{e(d)}</span><span class="pr">{e(p)}<small>{e(u)}</small></span></li>'
        for n, d, p, u in t["stay_rows"]) + "</ul>"
    facts = '<ul class="rows">' + "".join(f"<li><span>{e(f)}</span></li>" for f in t["facts"]) + "</ul>"
    contacts = '<ul class="rows">' + "".join(
        f'<li><span class="caps" style="font-size:5.6pt">{e(a)}</span><span class="v">{e(b)}</span></li>' for a, b in t["contacts"]) + "</ul>"
    qr = '<div class="qr">' + "".join(
        f'<figure><img src="../{f}.svg" alt=""><span class="caps">{e(t[k])}</span></figure>'
        for f, k in (("qr-wa", "qr_wa"), ("qr-ig", "qr_ig"), ("qr-site", "qr_site"))) + "</div>"
    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8">
<title>Ак-Тенгир — буклет ({t['lang'].upper()})</title><style>{CSS}{VARIANTS[variant]}</style></head><body>

<section class="sheet">
  <div class="p l cover">
    <div class="photo"><img src="{IMG}hero-30.jpg" alt=""></div>
    <div class="in"><img class="logo" src="{IMG}logo-color.png" alt="Ak-Tengir" style="width:22mm">
      <h1>{e(t['cover_title'])}</h1><p class="sub">{e(t['cover_sub'])}</p><p class="caps place">{e(t['cover_place'])}</p></div>
  </div>

  <div class="p">
    <h2>{e(t['about_h'])}</h2>
    <p>{e(t['about_p1'])}</p>
    <p>{e(t['about_p2'])}</p>
    {ph("n-19.jpg")}
    {facts}
    <div style="display:flex;align-items:baseline;gap:3mm"><span style="font-family:var(--serif);font-size:26pt;color:var(--ink);line-height:1">{e(t['rating'])}</span><span class="small">{e(t['rating_note'])}</span></div>
  </div>

  <div class="p r">
    <h2>{e(t['stay_h'])}</h2>
    <p class="it">{e(t['stay_sub'])}</p>
    {ph("y-d1.jpg", style="object-position:50% 60%")}
    {stay}
    <p class="small">{e(t['stay_year'])}</p>
    <div class="box"><span class="caps">{e(t['terms_h'])}</span><span class="small">{e(t['terms_p'])}</span></div>
  </div>
</section>

<section class="sheet">
  <div class="p l">
    <p class="quote">{e(t['retreat_quote'])}</p>
    {ph("r-fire.jpg")}
    <h3>{e(t['retreat_h'])}</h3>
    <p>{e(t['retreat_p'])}</p>
    <div style="display:flex;align-items:center;gap:3mm;margin-top:1mm"><img class="logo" src="{IMG}logo-color.png" alt="" style="width:10mm"><span class="caps">{e(t['book_h'])}</span></div>
    {contacts}
    {qr}
  </div>

  <div class="p">
    {ph("b-inside.jpg")}
    <h2>{e(t['banya_h'])}</h2>
    <p class="it">{e(t['banya_sub'])}</p>
    <p>{e(t['banya_p'])}</p>
    {rows(t['banya_rows'])}
    <p class="small" style="margin-top:-2mm">{e(t['banya_note'])}</p>
    <h3 style="margin-top:1mm">{e(t['food_h'])}</h3>
    <p>{e(t['food_p'])}</p>
    {rows(t['food_rows'])}
  </div>

  <div class="p r">
    <div class="ph" style="height:34mm"><img src="{IMG}n-3.jpg" alt=""></div>
    <h3>{e(t['leisure_h'])}</h3>
    <p>{e(t['leisure_p'])}</p>
    <h2 style="margin-top:1mm">{e(t['near_h'])}</h2>
    {rows(t['near_rows'])}
    <p class="small">{e(t['near_note'])}</p>
    <div class="pair">{ph("near-skazka.jpg", cls="")}{ph("near-jeti.jpg", cls="")}</div>
  </div>
</section>
</body></html>"""

if __name__ == "__main__":
    langs = sys.argv[1:] or [p.stem for p in (HERE / "texts").glob("*.json") if not p.stem.startswith(("banya-", "accordion8-"))]
    (HERE / "out").mkdir(exist_ok=True)
    for lang in langs:
        t = json.loads((HERE / "texts" / f"{lang}.json").read_text(encoding="utf-8"))
        for v in VARIANTS:
            name = f"booklet-{lang}" + ("" if v == "milk" else f"-{v}")
            (HERE / "out" / f"{name}.html").write_text(page(t, v), encoding="utf-8")
            print(f"out/{name}.html")
