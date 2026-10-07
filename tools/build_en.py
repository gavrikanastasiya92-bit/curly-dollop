"""Собирает английскую версию сайта.

Источник — русская страница site/index.html и словарь site/i18n/en.json
(«русская строка» → «английская строка»). Результат — site/en/index.html.

Запуск из корня репозитория:  python3 tools/build_en.py
После правок перевода достаточно поменять en.json и запустить скрипт снова.
"""
import html, json, re, sys
from pathlib import Path

# Пока перевод не утверждён, английская страница закрыта от поисковиков.
# Когда утвердят: поставить True, пересобрать и убрать строку `.lang{display:none!important}` в site/index.html.
EN_PUBLISHED = True

ROOT = Path(__file__).resolve().parent.parent / "site"
EN = json.loads((ROOT / "i18n" / "en.json").read_text(encoding="utf-8"))
# Абзацы с выделением внутри (<b>) переводятся целиком: «русский HTML» → «английский HTML»
EN_HTML = EN.pop("__html__", {})

HEAD = {
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
    if re.search("[А-Яа-яЁё]", key):
        missing.add(key)
    return seg

def tr_attr(m, missing):
    name, val = m.group(1), m.group(2)
    key = norm(html.unescape(val))
    if key in EN:
        return f'{name}="{html.escape(EN[key])}"'
    if re.search("[А-Яа-яЁё]", key):
        missing.add(key)
    return m.group(0)

def build():
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    for a, b in HEAD.items():
        if a not in src:
            sys.exit(f"не найдено в index.html: {a[:70]}")
        src = src.replace(a, b)
    if not EN_PUBLISHED:
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
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en" / "index.html").write_text(page, encoding="utf-8")
    if missing:
        print("Без перевода осталось строк:", len(missing))
        for m in sorted(missing):
            print("  ·", m[:100])
    else:
        print("Готово: site/en/index.html, все строки переведены.")

if __name__ == "__main__":
    build()
