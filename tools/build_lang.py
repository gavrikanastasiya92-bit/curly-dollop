"""Собирает языковые версии сайта: английскую (site/en/) и киргизскую (site/ky/).

Источник — русская страница site/index.html и словари site/i18n/<язык>.json
(«русская строка» → «перевод»). Результат — site/<язык>/index.html.

Запуск из корня репозитория:  python3 tools/build_lang.py        (все языки)
                              python3 tools/build_lang.py ky     (один язык)
После правок перевода достаточно поменять словарь и запустить скрипт снова.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "site"

HEAD_EN = {
    '<html lang="ru">': '<html lang="en">',
    "<title>Ак-Тенгир — юрточный резорт на южном берегу Иссык-Куля</title>":
        "<title>Ak-Tengir — a yurt resort on the south shore of Lake Issyk-Kul</title>",
    'content="Юрточный резорт у села Тосор на южном берегу Иссык-Куля: юрты от Стандарта до VIP, пляжная юрта и этно-дом, баня на берегу, свой сад и кухня. Открыто круглый год."':
        'content="A yurt resort near Tosor village on the south shore of Lake Issyk-Kul: yurts from Standard to VIP, a beach yurt and an ethno-house, a lakeside banya, our own garden and kitchen. Open all year round."',
    '<link rel="canonical" href="https://aktengir.com/">': '<link rel="canonical" href="https://aktengir.com/en/">',
    'content="Ак-Тенгир — юрточный резорт на Иссык-Куле"': 'content="Ak-Tengir — a yurt resort on Lake Issyk-Kul"',
    'content="Юрты, баня на берегу и тишина между горами и Иссык-Кулем."': 'content="Yurts, a lakeside banya and silence between the mountains and Issyk-Kul."',
    '<meta property="og:url" content="https://aktengir.com/">': '<meta property="og:url" content="https://aktengir.com/en/">',
    '<a href="./" aria-current="page" lang="ru">RU</a>': '<a href="../" lang="ru" hreflang="ru">RU</a>',
    '<a href="en/" lang="en" hreflang="en">EN</a>': '<a href="./" aria-current="page" lang="en">EN</a>',
}

HEAD_KY = {
    '<html lang="ru">': '<html lang="ky">',
    "<title>Ак-Тенгир — юрточный резорт на южном берегу Иссык-Куля</title>":
        "<title>Ак-Теңир — Ысык-Көлдүн түштүк жээгиндеги боз үй курорту</title>",
    'content="Юрточный резорт у села Тосор на южном берегу Иссык-Куля: юрты от Стандарта до VIP, пляжная юрта и этно-дом, баня на берегу, свой сад и кухня. Открыто круглый год."':
        'content="Ысык-Көлдүн түштүк жээгиндеги Тосор айылынын жанындагы боз үй курорту: Стандарттан VIPке чейинки боз үйлөр, пляждагы боз үй жана этно-үй, жээктеги мончо, өз багыбыз жана ашканабыз. Жыл бою ачык."',
    '<link rel="canonical" href="https://aktengir.com/">': '<link rel="canonical" href="https://aktengir.com/ky/">',
    'content="Ак-Тенгир — юрточный резорт на Иссык-Куле"': 'content="Ак-Теңир — Ысык-Көлдөгү боз үй курорту"',
    'content="Юрты, баня на берегу и тишина между горами и Иссык-Кулем."': 'content="Боз үйлөр, жээктеги мончо жана тоолор менен Ысык-Көлдүн ортосундагы тынчтык."',
    '<meta property="og:url" content="https://aktengir.com/">': '<meta property="og:url" content="https://aktengir.com/ky/">',
    '<a href="./" aria-current="page" lang="ru">RU</a><span aria-hidden="true">·</span><a href="en/" lang="en" hreflang="en">EN</a>':
        '<a href="../" lang="ru" hreflang="ru">RU</a><span aria-hidden="true">·</span><a href="../en/" lang="en" hreflang="en">EN</a><span aria-hidden="true">·</span><a href="./" aria-current="page" lang="ky">KY</a>',
}

# published: False — страница закрыта от поисковиков (noindex) и не видна в переключателе языков.
LANGS = {
    "en": {"head": HEAD_EN, "published": True},
    "ky": {"head": HEAD_KY, "published": False},  # черновик: перевод на вычитке у носителя языка
}

EN = {}  # словарь текущего языка, заполняется в build()
DONE = set()  # уже переведённые куски (киргизский тоже кириллица — их не считать пропусками)

def norm(t):
    return re.sub(r"\s+", " ", t).strip()

def tr_text(seg, missing):
    raw = html.unescape(seg)
    key = norm(raw)
    if not key:
        return seg
    if key in EN:
        lead = re.match(r"^\s*", raw).group(0)
        tail = re.search(r"\s*$", raw).group(0)
        return lead + html.escape(EN[key], quote=False) + tail
    if re.search("[А-Яа-яЁё]", key) and key not in DONE:
        missing.add(key)
    return seg

def tr_attr(m, missing):
    name, val = m.group(1), m.group(2)
    key = norm(html.unescape(val))
    if key in EN:
        return f'{name}="{html.escape(EN[key])}"'
    if re.search("[А-Яа-яЁё]", key) and key not in DONE:
        missing.add(key)
    return m.group(0)

def build(lang):
    cfg = LANGS[lang]
    EN.clear()
    EN.update(json.loads((ROOT / "i18n" / f"{lang}.json").read_text(encoding="utf-8")))
    # Абзацы с выделением внутри (<b>) переводятся целиком: «русский HTML» → «HTML перевода»
    EN_HTML = EN.pop("__html__", {})
    DONE.clear()
    for v in [*EN_HTML.values(), *cfg["head"].values()]:
        DONE.update(norm(html.unescape(t)) for t in re.split(r"<[^>]+>", v))
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    for a, b in cfg["head"].items():
        if a not in src:
            sys.exit(f"не найдено в index.html: {a[:70]}")
        src = src.replace(a, b)
    if not cfg["published"]:
        src = src.replace("<title>", '<meta name="robots" content="noindex">\n<title>', 1)
    for a, b in EN_HTML.items():
        if a not in src:
            sys.exit(f"не найден абзац для перевода: {a[:70]}")
        src = src.replace(a, b)
    missing = set()
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", src, flags=re.S)
    out = []
    for p in parts:
        if p.startswith("<script"):
            for k in ("Предыдущее фото", "Следующее фото"):
                p = p.replace(k, EN.get(k, k))
            out.append(p)
        elif p.startswith("<style") or p.startswith("<!"):
            out.append(p)
        elif p.startswith("<"):
            out.append(re.sub(r'\b(alt|aria-label|title)="([^"]*)"', lambda m: tr_attr(m, missing), p))
        else:
            out.append(tr_text(p, missing))
    page = "".join(out)
    # пути к файлам на уровень выше
    page = re.sub(r'((?:src|href|poster)=")(img/)', r"\1../img/", page)
    page = page.replace("url(img/", "url(../img/")
    (ROOT / lang).mkdir(exist_ok=True)
    (ROOT / lang / "index.html").write_text(page, encoding="utf-8")
    if missing:
        print(f"{lang}: без перевода осталось строк:", len(missing))
        for m in sorted(missing):
            print("  ·", m[:100])
    else:
        print(f"Готово: site/{lang}/index.html, все строки переведены.")

if __name__ == "__main__":
    for lang in sys.argv[1:] or LANGS:
        build(lang)
