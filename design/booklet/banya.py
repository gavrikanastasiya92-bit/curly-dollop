"""Листовка А4 про баню — для соседних мест отдыха, где своей бани нет. Система «Актенгир 2».

Тексты — texts/banya-<язык>.json. Результат — out/banya-<язык>[-blue].html; PDF: node render.mjs banya-ru
Формат: А4 вертикально, одна сторона, вылеты по 3 мм (216×303).
"""
import json, sys
from pathlib import Path
from build import CSS, VARIANTS, IMG, e, rows

HERE = Path(__file__).resolve().parent

FLYER = """
@page{size:216mm 303mm;margin:0}
.flyer{width:216mm;height:303mm;background:var(--bg);display:flex;flex-direction:column;overflow:hidden}
.hero{position:relative;height:90mm;flex:none}
.hero img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 45%;filter:saturate(.82) contrast(.96)}
.hero:after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:42%;background:linear-gradient(180deg,transparent 0%,color-mix(in srgb,var(--bg) 70%,transparent) 60%,var(--bg) 95%)}
.body{flex:1;min-height:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:auto auto minmax(40mm,1fr) auto auto;column-gap:12mm;padding:0 16mm 14mm;margin-top:-14mm;position:relative}
.head{grid-column:1/-1;display:grid;justify-items:center;text-align:center;gap:2.4mm;margin-bottom:6mm}
.head h1{font-size:30pt}
.head .it{font-size:14pt;margin-top:0}
.col{display:flex;flex-direction:column;gap:4mm;min-width:0}
.body p{font-size:8.6pt}
.flyer .rows li{font-size:8.4pt;padding:2.1mm 0}
.dots{list-style:none;display:grid;gap:1.2mm;font-size:8.4pt}
.dots li{padding-left:4mm;position:relative}.dots li:before{content:"";position:absolute;left:0;top:.75em;width:1.6mm;height:.25mm;background:var(--ink)}
.strip{grid-column:1/-1;display:grid;grid-template-columns:repeat(3,1fr);gap:1.4mm;margin:6mm 0;min-height:0}
.strip .ph{height:100%}
.q{font-family:var(--serif);font-style:italic;font-size:15pt;line-height:1.3;color:var(--ink)}
.foot{grid-column:1/-1;display:grid;grid-template-columns:1fr auto;gap:8mm;align-items:end;border-top:.25mm solid var(--line);padding-top:6mm}
.phone{font-family:var(--serif);font-size:24pt;color:var(--ink);line-height:1}
.flyer .qr{grid-template-columns:repeat(3,22mm);gap:5mm}
.flyer .qr .caps{font-size:5.6pt;text-align:center}
"""

def page(t, variant="milk"):
    qr = '<div class="qr">' + "".join(
        f'<figure><img src="../{f}.svg" alt=""><span class="caps">{e(c)}</span></figure>' for f, c in t["qr"]) + "</div>"
    dots = '<ul class="dots">' + "".join(f"<li>{e(x)}</li>" for x in t["incl"]) + "</ul>"
    notes = "".join(f'<p class="small" style="font-size:7.4pt">{e(x)}</p>' for x in t["price_notes"])
    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8">
<title>Ак-Тенгир — баня ({t['lang'].upper()})</title><style>{CSS}{FLYER}{VARIANTS[variant]}</style></head><body>
<section class="flyer">
  <div class="hero"><img src="{IMG}b-inside.jpg" alt=""></div>
  <div class="body">
    <div class="head">
      <img class="logo" src="{IMG}logo-color.png" alt="Ak-Tengir" style="width:17mm">
      <span class="caps">{e(t['brand'])}</span>
      <h1>{e(t['h'])}</h1>
      <p class="it">{e(t['sub'])}</p>
    </div>
    <div class="col">
      <p>{e(t['p1'])}</p>
      <p style="color:var(--ink)">{e(t['p2'])}</p>
      <span class="caps" style="margin-top:2mm">{e(t['incl_h'])}</span>
      {dots}
    </div>
    <div class="col">
      <span class="caps">{e(t['price_h'])}</span>
      {rows(t['prices'])}
      <div style="display:grid;gap:.8mm">{notes}</div>
    </div>
    <div class="strip"><div class="ph"><img src="{IMG}b-room.jpg" alt=""></div><div class="ph"><img src="{IMG}b-beach-house.jpg" alt=""></div><div class="ph"><img src="{IMG}b-hats.jpg" alt=""></div></div>
    <div style="grid-column:1/-1;display:grid;gap:1.6mm;margin-bottom:5mm;text-align:center;justify-items:center">
      <p class="q">{e(t['quote'])}</p><span class="small">{e(t['quote_who'])}</span>
    </div>
    <div class="foot">
      <div style="display:grid;gap:2.4mm">
        <span class="caps">{e(t['book_h'])}</span>
        <span class="phone">{e(t['phone'])}</span>
        <span class="small" style="font-size:7.4pt">{e(t['phone_note'])} · {e(t['addr'])}</span>
      </div>
      {qr}
    </div>
  </div>
</section></body></html>"""

if __name__ == "__main__":
    langs = sys.argv[1:] or [p.stem[6:] for p in (HERE / "texts").glob("banya-*.json")]
    (HERE / "out").mkdir(exist_ok=True)
    for lang in langs:
        t = json.loads((HERE / "texts" / f"banya-{lang}.json").read_text(encoding="utf-8"))
        for v in VARIANTS:
            name = f"banya-{lang}" + ("" if v == "milk" else f"-{v}")
            (HERE / "out" / f"{name}.html").write_text(page(t, v), encoding="utf-8")
            print(f"out/{name}.html")
