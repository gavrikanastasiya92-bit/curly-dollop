"""Брошюра-гармошка на 8 панелей по ТЗ заказчицы. Система «Актенгир 2».

Панель 99×210 мм (еврофлаер в сложенном виде), лист 396×210, с вылетами по 3 мм — 402×216.
Три сгиба гармошкой. Снаружи при сложенной брошюре — обложка (1) и контакты (8):
  сторона A:  [8 контакты | 6 отдых | 7 что рядом | 1 обложка]
  сторона B:  [2 о нас | 3 проживание | 4 баня | 5 группы]   (панель 2 — на обороте обложки)

Тексты — texts/accordion8-<язык>.json. Запуск: python3 accordion8.py ru; PDF: node render.mjs accordion8-ru
"""
import json, sys
from pathlib import Path
from build import CSS, VARIANTS, IMG, e, rows

HERE = Path(__file__).resolve().parent

EXTRA = """
@page{size:402mm 216mm;margin:0}
.sheet{width:402mm;grid-template-columns:102mm 99mm 99mm 102mm}
.tags{display:flex;flex-wrap:wrap;gap:1mm 2.6mm;font-size:5.8pt;font-weight:500;letter-spacing:.15em;text-transform:uppercase;color:var(--ink)}
.tags span:not(:last-child):after{content:"·";margin-left:2.6mm;color:var(--grey)}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:1.2mm}
.fill{flex:1 1 0;min-height:0}
.cards{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:4mm 3mm}
.card{display:flex;flex-direction:column;gap:1.2mm;min-height:0}
.card .ph{flex:1 1 0;min-height:18mm}
.card .n{font-family:var(--serif);font-size:11pt;font-weight:500;color:var(--ink);line-height:1.1;margin-top:.8mm}
.card .d{font-size:6.3pt;line-height:1.4}
.card .pr{font-size:7pt;font-weight:500;color:var(--ink)}
.near{list-style:none;display:flex;flex-direction:column;gap:2.4mm}
.near li{display:grid;grid-template-columns:30mm 1fr;gap:3mm;align-items:center;flex:1 1 0;min-height:0}
.near .ph{height:100%;min-height:15mm}
.near b{display:block;font-family:var(--serif);font-size:11pt;font-weight:500;color:var(--ink);line-height:1.15}
.near span{font-size:6.6pt}
.pn{font-size:6.2pt;font-style:normal;color:var(--grey);border-left:.4mm solid var(--line);padding-left:2.4mm}
.cta{display:grid;grid-template-columns:19mm 1fr;gap:3mm;align-items:center;border-top:.25mm solid var(--line);padding-top:3mm}
.cta img{width:19mm;height:19mm}
.p.cover.rr .in{padding:0 15mm 14mm 12mm}
.end .qr{grid-template-columns:repeat(3,21mm);gap:4.5mm}
"""

def tags(items):
    return '<div class="tags">' + "".join(f"<span>{e(x)}</span>" for x in items) + "</div>"

def ph(src, cls="", style=""):
    st = f' style="{style}"' if style else ""
    return f'<div class="ph {cls}"><img src="{IMG}{src}" alt=""{st}></div>'

def page(t, variant="milk"):
    pn = f'<p class="pn">{e(t["price_note"])}</p>'
    cards = '<div class="cards fill">' + "".join(
        f'<div class="card">{ph(img)}<span class="n">{e(n)}</span><span class="d">{e(d)}</span><span class="pr">{e(p)}</span></div>'
        for img, n, d, p in t["stay"]) + "</div>"
    near = '<ul class="near fill">' + "".join(
        f'<li>{ph(img)}<div><b>{e(n)}</b><span>{e(tm)}</span></div></li>' for img, n, tm in t["near"]) + "</ul>"
    notes = "".join(f'<p class="small">{e(x)}</p>' for x in t["banya_notes"])
    contacts = '<ul class="rows">' + "".join(
        f'<li><span class="caps" style="font-size:5.6pt">{e(a)}</span><span class="v">{e(b)}</span></li>' for a, b in t["contacts"]) + "</ul>"
    return f"""<!doctype html><html lang="{t['lang']}"><head><meta charset="utf-8">
<title>Ак-Тенгир — гармошка 8 панелей ({t['lang'].upper()})</title><style>{CSS}{EXTRA}{VARIANTS[variant]}</style></head><body>

<section class="sheet">
  <div class="p l end">
    {ph("n-6.jpg", "fill")}
    <h2>{e(t['end_h'])}</h2>
    <span class="caps" style="margin-top:-1.5mm">{e(t['end_place'])}</span>
    {contacts}
    <p class="small">{e(t['end_note'])}</p>
    <div class="qr"><figure><img src="../qr-wa.svg" alt=""><span class="caps" style="font-size:5.4pt">{e(t['qr_wa'])}</span></figure>
      <figure><img src="../qr-ig.svg" alt=""><span class="caps" style="font-size:5.4pt">{e(t['qr_ig'])}</span></figure>
      <figure><img src="../qr-site.svg" alt=""><span class="caps" style="font-size:5.4pt">{e(t['qr_site'])}</span></figure></div>
  </div>

  <div class="p">
    <h2>{e(t['rest_h'])}</h2>
    {tags(t['rest_tags'])}
    <p>{e(t['rest_p'])}</p>
    <div class="grid2 fill" style="grid-template-rows:repeat(3,1fr)">
      {ph("n-3.jpg")}{ph("n-22.jpg")}{ph("n-47.jpg")}{ph("n-8.jpg")}{ph("t-umbrella-lake.jpg")}{ph("v-boards-sunset.jpg")}
    </div>
  </div>

  <div class="p">
    <h2>{e(t['near_h'])}</h2>
    {near}
    <p class="small">{e(t['near_note'])}</p>
  </div>

  <div class="p r cover rr">
    <div class="photo"><img src="{IMG}hero-30.jpg" alt=""></div>
    <div class="in"><img class="logo" src="{IMG}logo-color.png" alt="Ak-Tengir" style="width:22mm">
      <h1>{e(t['cover_title'])}</h1><p class="sub">{e(t['cover_tag'])}</p><p class="caps place">{e(t['cover_place'])}</p></div>
  </div>
</section>

<section class="sheet">
  <div class="p l">
    <h2>{e(t['about_h'])}</h2>
    <p>{e(t['about_p'])}</p>
    {tags(t['about_tags'])}
    {ph("n-19.jpg", "fill")}
    <div class="grid2" style="height:36mm">{ph("t-garden-arch.jpg")}{ph("k-table.jpg")}</div>
  </div>

  <div class="p">
    <h2>{e(t['stay_h'])}</h2>
    {cards}
    <p class="small">{e(t['stay_note'])}</p>
    {pn}
  </div>

  <div class="p">
    {ph("b-room.jpg", "fill")}
    <h2>{e(t['banya_h'])}</h2>
    <p>{e(t['banya_p'])}</p>
    {rows(t['banya_rows'])}
    <div style="display:grid;gap:1mm">{notes}</div>
    {pn}
  </div>

  <div class="p r">
    {ph("r-group.jpg", "fill")}
    <h2>{e(t['groups_h'])}</h2>
    {tags(t['groups_tags'])}
    <p>{e(t['groups_p'])}</p>
    <ul class="rows">{"".join(f"<li><span>{e(x)}</span></li>" for x in t['groups_offer'])}</ul>
    <div class="cta"><img src="../qr-wa.svg" alt=""><span class="caps" style="line-height:1.6">{e(t['groups_cta'])}</span></div>
  </div>
</section>
</body></html>"""

if __name__ == "__main__":
    langs = sys.argv[1:] or [p.stem[11:] for p in (HERE / "texts").glob("accordion8-*.json")]
    (HERE / "out").mkdir(exist_ok=True)
    for lang in langs:
        t = json.loads((HERE / "texts" / f"accordion8-{lang}.json").read_text(encoding="utf-8"))
        for v in VARIANTS:
            name = f"accordion8-{lang}" + ("" if v == "milk" else f"-{v}")
            (HERE / "out" / f"{name}.html").write_text(page(t, v), encoding="utf-8")
            print(f"out/{name}.html")
