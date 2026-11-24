#!/usr/bin/env python3
"""Static site generator for the seamc.ru demo.

Reads content/*.json, writes the site to ./site (each page as <slug>/index.html,
so old Joomla URLs like /voditelskaya-medkomissiya keep working).
Run: python3 build.py
"""
import json, os, shutil, re
from html import escape as e

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "site")
C = lambda n: json.load(open(os.path.join(ROOT, "content", n), encoding="utf-8"))

SITE = C("site.json")
SERVICES = C("services.json")
DOCTORS = C("doctors.json")
PRICES = C("prices.json")
for _s in SERVICES:
    if _s["slug"] == "medosmotry": _s["slug"] = "uslugi/medosmotry"  # keep old URL
SVC = {s["slug"]: s for s in SERVICES}
STAFF = "~40"

PHONE = "(812) 244-93-73"
TEL = "+78122449373"
EMAIL = "info@seamc.ru"
ADDR = "Санкт-Петербург, Межевой канал, д. 5, лит. АХ"
ADDR2 = "БЦ «Балтийский морской центр», цокольный этаж"
HOURS = "Пн-Пт 9:00-17:00"
HOURS2 = "Сб-Вс выходной"
YMAPS = "https://yandex.ru/maps/2/saint-petersburg/?text=%D0%9C%D0%B5%D0%B6%D0%B5%D0%B2%D0%BE%D0%B9%20%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%2C%205"
GIS = "https://2gis.ru/spb/search/%D0%9C%D0%B5%D0%B6%D0%B5%D0%B2%D0%BE%D0%B9%20%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%2C%205"
MAP = "https://yandex.ru/map-widget/v1/?text=%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3%2C%20%D0%9C%D0%B5%D0%B6%D0%B5%D0%B2%D0%BE%D0%B9%20%D0%BA%D0%B0%D0%BD%D0%B0%D0%BB%2C%205&z=16"

# ---------------------------------------------------------------- icons (stroke, 24 grid)
P = {
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 5L2 7"/>',
 "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
 "check": '<circle cx="12" cy="12" r="10"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
 "car": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/>',
 "sail": '<path d="M22 18H2a4 4 0 0 0 4 4h12a4 4 0 0 0 4-4Z"/><path d="M21 14 10 2 3 14h18Z"/><path d="M10 2v16"/>',
 "waves": '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
 "anchor": '<circle cx="12" cy="5" r="3"/><path d="M12 22V8M5 12H2a10 10 0 0 0 20 0h-3"/>',
 "ship": '<path d="M2 21c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1 .6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M19.4 20A11.6 11.6 0 0 0 21 14l-9-4-9 4c0 2.9.9 5.3 2.8 7.8"/><path d="M19 13V7a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v6M12 10v4M12 2v3"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "clip": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
 "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2M15 18H9M19 18h2a1 1 0 0 0 1-1v-3.7a1 1 0 0 0-.2-.6l-3.5-4.3a1 1 0 0 0-.8-.4H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
 "kit": '<path d="M12 11v4M10 13h4M16 6V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/><rect x="2" y="6" width="20" height="14" rx="2"/>',
 "book": '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M9 7h7M9 11h5"/>',
 "cap": '<path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
 "pulse": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7Z"/><path d="M3.2 12h6.3l.5-1 2 4.5 2-7 1.5 3.5h5.3"/>',
 "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
 "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="4"/>',
 "tooth": '<path d="M7 3C4.5 3 3 5 3 7.5c0 2 1 3.5 1.5 5.5.6 2.5.8 8 3 8 1.8 0 1.5-5 4.5-5s2.7 5 4.5 5c2.2 0 2.4-5.5 3-8 .5-2 1.5-3.5 1.5-5.5C21 5 19.5 3 17 3c-2 0-3 1-5 1S9 3 7 3Z"/>',
 "steth": '<path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6 6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6 6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/>',
 "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
 "brain": '<path d="M12 5a3 3 0 1 0-6 .1 4 4 0 0 0-2.5 5.8 4 4 0 0 0 .6 6.6A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 6 .1 4 4 0 0 1 2.5 5.8 4 4 0 0 1-.6 6.6A4 4 0 1 1 12 18Z"/><path d="M12 5v13"/>',
 "ear": '<path d="M6 8.5a6.5 6.5 0 1 1 13 0c0 6-6 6-6 10a3.5 3.5 0 1 1-7 0"/><path d="M15 8.5a2.5 2.5 0 0 0-5 0v1a2 2 0 1 1 0 4"/>',
 "heart": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7Z"/>',
 "drop": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
 "venus": '<circle cx="12" cy="9" r="6"/><path d="M12 15v7M9 19h6"/>',
 "mars": '<circle cx="10" cy="14" r="6"/><path d="M14.2 9.8 21 3M15 3h6v6"/>',
 "spark": '<path d="M12 3l1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2Z"/>',
 "cross": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M8 12h8M12 8v8"/>',
 "chat": '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
 "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
 "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
 "x": '<path d="M18 6 6 18M6 6l12 12"/>',
 "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M8 13h8M8 17h5"/>',
 "brief": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
 "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
 "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
 "glasses": '<circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path d="M14 15a2 2 0 0 0-4 0M2.5 13 5 7c.7-1.3 1.4-2 3-2M21.5 13 19 7c-.7-1.3-1.5-2-3-2"/>',
 "timer": '<path d="M10 2h4M12 14l3-3"/><circle cx="12" cy="14" r="8"/>',
 "tag": '<path d="M12.6 2.6A2 2 0 0 0 11.2 2H4a2 2 0 0 0-2 2v7.2a2 2 0 0 0 .6 1.4l8.7 8.7a2.4 2.4 0 0 0 3.4 0l6.6-6.6a2.4 2.4 0 0 0 0-3.4z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
 "building": '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M12 6h.01M16 6h.01M8 10h.01M12 10h.01M16 10h.01M8 14h.01M12 14h.01M16 14h.01"/>',
 "metro": '<path d="M4 18 8 6l4 8 4-8 4 12"/><path d="M2 18h5M17 18h5"/>',
}
def I(name, cls="icon"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{P.get(name, P["cross"])}</svg>'

SVC_ICON = {
 "voditelskaya-medkomissiya": "car", "oruzhejnaya-medkomissiya": "shield", "medkomissiya-malomernye-suda": "sail",
 "vodolaznaya-medkomissiya": "waves", "medkomissiya-plavsostava": "ship", "profosmotry": "users",
 "uslugi/medosmotry": "clip", "predrejsovye-osmotry": "truck", "organizatsiya-feldsherskikh-punktov": "kit",
 "sanitarnye-knizhki": "book", "med-spravka-086-u-dlya-studentov": "cap", "spravka-dlya-poseshcheniya-bassejna": "waves",
 "sutochnoe-monitorirovanie-ekg": "pulse", "ultrazvukovaya-diagnostika-uzi": "scan", "stoma-t": "tooth",
}
DOC_ICON = {"kardiolog": "heart", "nevrolog": "brain", "oftalmolog": "eye", "lor": "ear", "urolog": "mars",
            "ginekolog": "venus", "dermatolog": "spark", "khirurg": "cross", "psikhoterapevt": "chat",
            "endokrinolog": "drop", "terapevt": "steth", "semejnyj-vrach": "user"}
GROUPS = [("komissii", "Медкомиссии"), ("spravki", "Справки и книжки"), ("business", "Для работодателей"),
          ("diagnostika", "Диагностика"), ("stomatologiya", "Стоматология")]

MARK_SVG = open(os.path.join(ROOT, "src", "img", "logo-mark.svg"), encoding="utf-8").read()
MARK_PATHS = re.search(r"</style>(.*)</svg>", MARK_SVG, re.S).group(1)
LOGO = '<img src="/img/logo-mark.svg" alt="" width="46" height="45">'
PRELOADER = f'''<div class="preloader" id="preloader" aria-hidden="true"><div class="pl-in">
<svg class="pl-mark" viewBox="86 74 330 324"><defs><mask id="plsweep" maskUnits="userSpaceOnUse" x="0" y="0" width="600" height="600">
<circle class="pl-sweep" cx="300" cy="228" r="112" fill="none" stroke="#fff" stroke-width="130" pathLength="100" transform="rotate(-98 300 228)"/></mask></defs>
<g class="pl-green" mask="url(#plsweep)">{MARK_PATHS.replace('class="lg-blue"', 'class="lg-blue" style="display:none"')}</g>
<g class="pl-blue">{MARK_PATHS.replace('class="lg-green"', 'class="lg-green" style="display:none"')}</g></svg>
<div class="pl-name"><b>Морской Медицинский Центр</b><span>Санкт-Петербург</span></div>
<div class="pl-line"><i></i></div></div></div>'''

def url(slug): return "/" if not slug else f"/{slug.strip('/')}/"

def svc_card(s, tag=True):
    meta = s.get("price_from") or s.get("duration") or "Подробнее"
    t = ""
    if tag:
        aud = {"people": "Частным лицам", "business": "Компаниям", "both": "Лицам и компаниям"}.get(s.get("audience"), "")
        t = f'<span class="tag">{e(aud)}</span>' if aud else ""
    return (f'<a class="card rv" href="{url(s["slug"])}"><span class="ic">{I(SVC_ICON.get(s["slug"], "cross"))}</span>'
            f'{t}<h3>{e(s["title"])}</h3><p>{e(s.get("short",""))}</p>'
            f'<span class="meta"><span>{e(meta)}</span><span class="arr">{I("arrow")}</span></span></a>')

def by_group(g): return [s for s in SERVICES if s.get("group") == g]

NAV = [("uslugi", "Справки и комиссии"), ("kompaniyam", "Компаниям"), ("konsultatsii-vrachej", "Врачи"),
       ("stoimost-uslug", "Цены"), ("o-centre", "О центре"), ("kontakty", "Контакты")]

def layout(slug, title, desc, body):
    nav = "".join(f'<a href="{url(s)}"{" aria-current=page" if slug.split("/")[0]==s else ""}>{e(t)}</a>' for s, t in NAV)
    mnav = "".join(f'<a class="l" href="{url(s)}">{e(t)}</a>' for s, t in NAV)
    msvc = "".join(f'<a class="s" href="{url(s["slug"])}">{e(s["title"])}</a>' for s in by_group("komissii") + by_group("spravki"))
    foot_svc = "".join(f'<a href="{url(s["slug"])}">{e(s.get("menu") or s["title"])}</a>' for s in by_group("komissii") + by_group("spravki"))
    foot_biz = "".join(f'<a href="{url(s["slug"])}">{e(s.get("menu") or s["title"])}</a>' for s in by_group("business") + by_group("diagnostika") + by_group("stomatologiya"))
    full_title = title if slug == "" else f"{title} - Морской Медицинский Центр"
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#0d2a47">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="/img/hero.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={VER}">
<script>(function(h){{h.classList.add("js");try{{if(!sessionStorage.getItem("pl")&&!/[?&]shot/.test(location.search)&&!matchMedia("(prefers-reduced-motion: reduce)").matches){{h.classList.add("pl");sessionStorage.setItem("pl","1")}}}}catch(e){{}}}})(document.documentElement)</script>
</head>
<body>
{PRELOADER}
<a class="skip" href="#main">К содержанию</a>
<div class="topbar"><div class="wrap">
<span class="hide-m">{I("pin")}Межевой канал, 5 - рядом с Морским портом</span>
<span class="hide-s">{I("clock")}{HOURS}, {HOURS2.lower()}</span>
<span class="sp"></span>
<button type="button" id="a11y">{I("glasses")}Версия для слабовидящих</button>
</div></div>
<header class="hdr" id="hdr"><div class="wrap">
<a class="logo" href="/">{LOGO}<span>Морской<br>Медицинский Центр<small>Санкт-Петербург</small></span></a>
<nav class="nav" aria-label="Главное меню">{nav}</nav>
<a class="hdr-phone" href="tel:{TEL}">{PHONE}</a>
<a class="btn btn-buoy btn-sm" href="#zapis">Записаться</a>
<button class="burger" type="button" id="burger" aria-label="Открыть меню" aria-expanded="false">{I("menu")}</button>
</div></header>
<div class="mnav" id="mnav" role="dialog" aria-label="Меню">
<div class="mnav-top"><a class="logo" href="/">{LOGO}<span>Морской<br>Медицинский Центр</span></a><button class="burger" type="button" id="mclose" aria-label="Закрыть меню" style="display:block">{I("x")}</button></div>
{mnav}
<div class="mnav-sub">Справки и комиссии</div>{msvc}
<a class="btn btn-buoy" href="tel:{TEL}">{I("phone")}Позвонить {PHONE}</a>
</div>
<main id="main">
{body}
</main>
<footer class="ftr"><div class="wrap">
<div class="cols">
<div><a class="logo" href="/">{LOGO}<span>Морской<br>Медицинский Центр<small>Санкт-Петербург</small></span></a>
<p>Морская и промышленная медицина, медкомиссии и профосмотры рядом с Морским портом.</p>
<a href="tel:{TEL}" style="font-size:22px;font-weight:700;color:#fff">{PHONE}</a>
<a href="mailto:{EMAIL}">{EMAIL}</a>
<p style="margin-top:12px">{e(ADDR)}<br>{e(ADDR2)}<br>{HOURS}, {HOURS2.lower()}</p></div>
<div><h4>Справки и комиссии</h4>{foot_svc}</div>
<div><h4>Компаниям и диагностика</h4>{foot_biz}</div>
<div><h4>Центр</h4><a href="/konsultatsii-vrachej/">Врачи</a><a href="/stoimost-uslug/">Цены</a><a href="/o-centre/">О центре</a><a href="/vakansii/">Вакансии</a><a href="/kontakty/">Контакты</a><a href="/info/">Информация для пациентов</a><a href="/politika/">Политика конфиденциальности</a></div>
</div>
<div class="legal">
<div class="warn">Имеются противопоказания. Необходима консультация специалиста.</div>
<div>ООО «Морской Медицинский Центр». Лицензия на осуществление медицинской деятельности № [уточняется] от [уточняется]. ОГРН [уточняется], ИНН [уточняется].</div>
<div><span class="demo-badge">Демо</span>Демонстрационная версия нового сайта. Цены и сведения перенесены с seamc.ru и уточняются. © 2026 Морской Медицинский Центр</div>
</div>
</div></footer>
<div class="callbar"><a class="btn btn-navy" href="tel:{TEL}">{I("phone")}Позвонить</a><a class="btn btn-buoy" href="#zapis">Записаться</a></div>
<script src="/main.js?v={VER}" defer></script>
</body>
</html>'''

def form_band(title="Запишитесь или задайте вопрос", text=None, company=False):
    text = text or "Оставьте телефон - администратор перезвонит в рабочее время, подскажет, какие врачи нужны, сколько это стоит и что взять с собой."
    opts = "".join(f'<option>{e(s["title"])}</option>' for s in SERVICES)
    comp = '<input name="company" placeholder="Компания" autocomplete="organization">' if company else ""
    return f'''<section class="sec" id="zapis"><div class="wrap"><div class="form-band rv">
<div><span class="eyebrow">Запись</span><h2>{e(title)}</h2><p>{e(text)}</p>
<p style="margin:0">Или позвоните: <a href="tel:{TEL}" style="color:#fff;font-weight:700">{PHONE}</a><br>{HOURS}</p></div>
<form class="form" data-demo>
<input name="name" placeholder="Как к вам обращаться" required autocomplete="name">
{comp}<input name="phone" type="tel" placeholder="Телефон" required autocomplete="tel">
<select name="service" aria-label="Услуга"><option value="">Что нужно оформить?</option>{opts}<option>Другое</option></select>
<label class="chk"><input type="checkbox" required> <span>Согласен на обработку персональных данных в соответствии с <a href="/politika/">политикой конфиденциальности</a></span></label>
<button class="btn btn-buoy" type="submit">Отправить заявку {I("arrow")}</button>
<div class="form-ok" hidden>Спасибо! Это демо-версия сайта, заявка никуда не отправлена. Чтобы записаться сейчас, позвоните: {PHONE}.</div>
</form></div></div></section>'''

def contacts_block():
    route = "".join(f'<li><span class="m">М</span><span>{e(r)}</span></li>' for r in SITE.get("directions", [])[:6])
    return f'''<section class="sec" id="kontakty"><div class="wrap">
<div class="sec-head rv"><div><span class="eyebrow">Как добраться</span><h2>Рядом с Морским портом</h2></div><p>Удобно, если вы работаете в порту или на соседних терминалах. Из центра города - на метро и маршрутке.</p></div>
<div class="contact rv">
<div class="contact-info"><dl>
<dt>Телефон</dt><dd><a class="big" href="tel:{TEL}">{PHONE}</a></dd>
<dt>Адрес</dt><dd>{e(ADDR)}<br>{e(ADDR2)}</dd>
<dt>Часы работы</dt><dd>{HOURS}<br>{HOURS2}</dd>
<dt>Почта</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd>
</dl>
<div class="maplinks"><a class="btn btn-navy btn-sm" href="{YMAPS}" target="_blank" rel="noopener">{I("pin")}Яндекс Карты</a><a class="btn btn-line btn-sm" href="{GIS}" target="_blank" rel="noopener">{I("pin")}2ГИС</a></div>
<div style="margin-top:24px"><ul class="route">{route}</ul></div></div>
<div class="map"><iframe src="{MAP}" title="Карта: Межевой канал, 5" loading="lazy"></iframe></div>
</div></div></section>'''

def page_hero(crumbs, h1, lead, facts=""):
    cr = '<a href="/">Главная</a>' + "".join(f' / <a href="{url(s)}">{e(t)}</a>' for s, t in crumbs)
    return f'''<section class="page-hero"><div class="wrap"><nav class="crumbs" aria-label="Навигация">{cr}</nav>
<h1>{e(h1)}</h1><p class="lead">{e(lead)}</p>{facts}</div></section>'''

def aside(extra_links=None, title="Другие услуги"):
    links = "".join(f'<a href="{url(s)}">{e(t)}</a>' for s, t in (extra_links or []))
    lk = f'<div class="aside-links"><h4>{e(title)}</h4>{links}</div>' if links else ""
    return f'''<aside class="aside"><div class="aside-card"><h3>Запись и вопросы</h3>
<a class="tel" href="tel:{TEL}">{PHONE}</a><p>Администратор подскажет стоимость, список врачей и что взять с собой.</p>
<a class="btn btn-buoy" href="#zapis">Оставить заявку</a>
<ul><li>{I("clock")}<span>{HOURS}<br>{HOURS2}</span></li><li>{I("pin")}<span>Межевой канал, 5, лит. АХ, цокольный этаж</span></li><li>{I("card")}<span>Оплата картой: МИР, Visa, Mastercard</span></li></ul>
</div>{lk}</aside>'''

def ul(items, icon="check", cls="list"):
    return f'<ul class="{cls}">' + "".join(f'<li>{I(icon)}<span>{e(x)}</span></li>' for x in items) + "</ul>"

def ol(items):
    return '<ol class="olist">' + "".join(f'<li><span>{e(x)}</span></li>' for x in items) + "</ol>"

def faq(items):
    return '<div class="faq">' + "".join(f'<details><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in items) + "</div>"

# ---------------------------------------------------------------- pages
pages = {}

def home():
    people = by_group("komissii") + by_group("spravki")
    biz = by_group("business")
    pl = "".join(f'<li><a href="{url(s["slug"])}">{I(SVC_ICON.get(s["slug"],"cross"))}{e(s.get("menu") or s["title"])}</a></li>' for s in people)
    bl = "".join(f'<li><a href="{url(s["slug"])}">{I(SVC_ICON.get(s["slug"],"cross"))}{e(s.get("menu") or s["title"])}</a></li>' for s in biz)
    docs = "".join(f'<a class="doc rv" href="/konsultatsii-vrachej/{d["slug"]}/"><span class="ic">{I(DOC_ICON.get(d["slug"],"steth"))}</span><span>{e(d["title"])}<small>{e(first_price(d))}</small></span></a>' for d in DOCTORS)
    partners = "".join(f"<span>{e(p)}</span>" for p in SITE.get("partners", [])[:6])
    body = f'''
<section class="hero"><div class="hero-bg"><picture><source media="(max-width:640px)" srcset="/img/hero-m.jpg"><img src="/img/hero.jpg" alt="" fetchpriority="high"></picture></div>
<div class="wrap">
<span class="eyebrow">Морская и промышленная медицина</span>
<h1>Медкомиссии и справки рядом с Морским портом</h1>
<p class="lead">Водительская и оружейная комиссия, плавсостав, водолазы, маломерные суда. Профосмотры и предрейсовые осмотры для компаний по договору. Все врачи - в одном месте.</p>
<div class="cta-row"><a class="btn btn-buoy" href="tel:{TEL}">{I("phone")}{PHONE}</a><a class="btn btn-ghost" href="/uslugi/">Выбрать справку {I("arrow")}</a></div>
<div class="hero-facts"><span class="chip">{I("clock")}{HOURS}</span><span class="chip">{I("users")}Около 40 специалистов</span><span class="chip">{I("anchor")}Опыт работы с портом и флотом</span></div>
</div></section>
<svg class="wave" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true"><path fill="currentColor" d="M0 34c120-18 240-26 360-18s240 30 360 30 240-24 360-30 240 6 360 18v26H0z"/></svg>

<section><div class="wrap"><div class="doors">
<div class="door rv"><div class="door-top"><span class="door-ic">{I("user")}</span><h2>Мне нужна справка</h2></div>
<p>Для ГИБДД, разрешения на оружие, судоводителя, бассейна, учёбы или работы. Приходите в рабочее время.</p>
<ul>{pl}</ul><a class="btn btn-navy" href="/uslugi/">Все справки и комиссии {I("arrow")}</a></div>
<div class="door biz rv"><div class="door-top"><span class="door-ic">{I("brief")}</span><h2>Мы - компания</h2></div>
<p>Предварительные и периодические медосмотры, предрейсовые осмотры, медпункт на вашей территории. Работаем по договору.</p>
<ul>{bl}</ul><a class="btn btn-buoy" href="/kompaniyam/">Условия для компаний {I("arrow")}</a></div>
</div></div></section>

<section class="sec"><div class="wrap">
<div class="sec-head rv"><div><span class="eyebrow">Популярное</span><h2>Медкомиссии</h2></div><p>Специальные комиссии - наш основной профиль. Особенно для тех, кто связан с морем.</p></div>
<div class="grid grid-5">{"".join(svc_card(s, False) for s in by_group("komissii"))}</div>
<div class="group-title">Справки и медицинские книжки</div>
<div class="grid">{"".join(svc_card(s, False) for s in by_group("spravki"))}</div>
</div></section>

<section class="sec sec-mist"><div class="wrap">
<div class="sec-head rv"><div><span class="eyebrow">Как это проходит</span><h2>Без беготни по поликлиникам</h2></div><p>Все нужные специалисты и исследования - в одном центре, по одному адресу.</p></div>
<div class="steps">
<div class="step rv"><h3>Позвоните</h3><p>Администратор скажет, каких врачей нужно пройти, сколько это стоит и какие документы взять.</p></div>
<div class="step rv"><h3>Приходите</h3><p>Пн-Пт с 9:00 до 17:00. Межевой канал, 5, рядом с Морским портом.</p></div>
<div class="step rv"><h3>Пройдите врачей</h3><p>Осмотры и обследования проходят в одном здании, без переездов.</p></div>
<div class="step rv"><h3>Получите документ</h3><p>Заключение или справку установленного образца - на руки.</p></div>
</div></div></section>

<section class="sec"><div class="wrap why">
<div class="rv"><span class="eyebrow">О центре</span><h2>Медицина для тех, кто работает в порту и на флоте</h2>
<p>Морской Медицинский Центр - частное медицинское учреждение, которое проверяет и сохраняет профессиональное здоровье моряков, портовиков и работников промышленных предприятий. К нам приходят и горожане - за консультацией врача, диагностикой или справкой.</p>
<ul class="ticks"><li>{I("check")}<span>Морская и промышленная медицина - основной профиль</span></li><li>{I("check")}<span>Медкомиссии для плавсостава, водолазов и судоводителей маломерных судов</span></li><li>{I("check")}<span>Профосмотры сотрудников предприятий по договору</span></li></ul>
<div class="partners">{partners}</div>
<p style="margin-top:24px"><a href="/o-centre/" class="btn btn-line">Подробнее о центре {I("arrow")}</a></p></div>
<div class="stats rv">
<div class="stat"><b>{STAFF}</b><span>специалистов в команде</span></div>
<div class="stat"><b>{len(DOCTORS)}</b><span>врачебных специальностей</span></div>
<div class="stat"><b>{len(SERVICES)}</b><span>видов комиссий, осмотров и справок</span></div>
<div class="stat"><b>1</b><span>адрес - все врачи и обследования рядом</span></div>
</div></div></section>

<section class="sec sec-mist"><div class="wrap">
<div class="sec-head rv"><div><span class="eyebrow">Консультации</span><h2>Врачи-специалисты</h2></div><p>Приём узких специалистов без направления. Цены первичного приёма - ниже, полный прайс на странице цен.</p></div>
<div class="docs">{docs}</div>
<div class="group-title" style="margin-top:56px">Диагностика и стоматология</div>
<div class="grid">{"".join(svc_card(s, False) for s in by_group("diagnostika") + by_group("stomatologiya"))}</div>
</div></section>
{form_band()}
{contacts_block()}'''
    pages[""] = ("Морской Медицинский Центр - медкомиссии и справки в Санкт-Петербурге",
                 "Медкомиссии, справки, профосмотры и консультации врачей рядом с Морским портом Санкт-Петербурга. Межевой канал, 5. Тел. (812) 244-93-73.", body)

def first_price(d):
    for r in d.get("price_rows") or []:
        if "первич" in r["name"].lower() and r.get("price"):
            return "Приём " + r["price"]
    return "Консультация"

def service_page(s):
    facts = []
    if s.get("price_from"): facts.append(f'<span class="fact">{I("tag")}{e(s["price_from"])}</span>')
    if s.get("duration"): facts.append(f'<span class="fact">{I("timer")}{e(s["duration"])}</span>')
    aud = {"people": "Частным лицам", "business": "Компаниям", "both": "Частным лицам и компаниям"}.get(s.get("audience"))
    if aud: facts.append(f'<span class="fact">{I("user" if s.get("audience")=="people" else "brief")}{aud}</span>')
    fr = f'<div class="facts-row">{"".join(facts)}</div>' if facts else ""
    grp = dict(GROUPS).get(s.get("group"), "Услуги")
    parts = []
    if s.get("includes"): parts.append(f'<h2>Что входит</h2>{ul(s["includes"], cls="list cols" if len(s["includes"])>4 else "list")}')
    if s.get("steps"): parts.append(f'<h2>Как проходит</h2>{ol(s["steps"])}')
    elif s.get("audience") == "business":
        parts.append('<h2>Как начать работу</h2>' + ol(["Пришлите заявку: количество сотрудников и их профессии или вредные факторы", "Согласуем стоимость, договор и график", "Проводим осмотры в согласованные даты", "Передаём заключения и итоговые документы"]))
    elif s.get("group") != "stomatologiya":
        parts.append('<h2>Как записаться</h2>' + ol([f"Позвоните {PHONE} - администратор назовёт стоимость и список врачей", f"Приходите {HOURS.replace('Пн-Пт', 'в будни,')}, возьмите паспорт", "Пройдите врачей и обследования в одном здании", "Получите заключение или справку на руки"]))
    if s.get("documents"): parts.append(f'<h2>Что взять с собой</h2>{ul(s["documents"], "file")}')
    if s.get("facts"): parts.append(f'<h2>Важно знать</h2>{ul(s["facts"], "check")}')
    if s.get("faq"): parts.append(f'<h2>Частые вопросы</h2>{faq(s["faq"])}')
    if s["slug"] == "stoma-t":
        rows = next((c["items"] for c in PRICES if "томатол" in c["category"]), [])
        if rows: parts.append(f'<h2>Цены</h2>{ptable(rows)}')
    parts.append('<p class="note">Стоимость и перечень врачей зависят от вашей ситуации - точно скажет администратор по телефону. Имеются противопоказания, необходима консультация специалиста.</p>')
    rel = [(x["slug"], x["title"]) for x in SERVICES if x.get("group") == s.get("group") and x["slug"] != s["slug"]]
    body = page_hero([("uslugi", grp)], s["title"], s.get("lead", ""), fr) + \
        f'<div class="wrap layout"><div class="prose">{"".join(parts)}</div>{aside(rel)}</div>' + \
        form_band(company=s.get("audience") == "business")
    pages[s["slug"]] = (s["title"], s.get("short") or s.get("lead", "")[:150], body)

def ptable(rows):
    return '<table class="ptable"><tbody>' + "".join(
        f'<tr><td>{e(r["name"])}</td><td>{e(r.get("price",""))}</td></tr>' for r in rows) + "</tbody></table>"

def doctor_page(d):
    parts = []
    if d.get("treats"): parts.append(f'<h2>С чем обращаются</h2>{ul(d["treats"], cls="list cols" if len(d["treats"])>4 else "list")}')
    if d.get("price_rows"): parts.append(f'<h2>Стоимость</h2>{ptable(d["price_rows"])}')
    parts.append('<p class="note">Цены перенесены с прежнего сайта и уточняются. Имеются противопоказания, необходима консультация специалиста.</p>')
    rel = [("konsultatsii-vrachej/" + x["slug"], x["title"]) for x in DOCTORS if x["slug"] != d["slug"]]
    body = page_hero([("konsultatsii-vrachej", "Врачи")], d["title"], d.get("lead", ""),
                     f'<div class="facts-row"><span class="fact">{I("tag")}{e(first_price(d))}</span>' + (f'<span class="fact">{I("user")}{e(d["doctor"])}</span>' if d.get("doctor") else "") + f'<span class="fact">{I("clock")}{HOURS}</span></div>') + \
        f'<div class="wrap layout"><div class="prose">{"".join(parts)}</div>{aside(rel, "Другие врачи")}</div>' + form_band()
    pages["konsultatsii-vrachej/" + d["slug"]] = (f'{d["title"]} - приём в Санкт-Петербурге', d.get("short", ""), body)

def hub_services():
    blocks = ""
    for g, name in GROUPS:
        items = by_group(g)
        if items:
            blocks += f'<div class="group-title">{e(name)}</div><div class="grid">{"".join(svc_card(s) for s in items)}</div>'
    body = page_hero([], "Справки, комиссии и осмотры", "Выберите, что нужно оформить. На странице каждой услуги - что входит, как проходит и что взять с собой.") + \
        f'<section class="sec" style="padding-top:56px"><div class="wrap">{blocks}</div></section>' + form_band()
    pages["uslugi"] = ("Справки, комиссии и осмотры", "Все медкомиссии, справки и профосмотры Морского Медицинского Центра.", body)

def hub_doctors():
    docs = "".join(f'<a class="card rv" href="/konsultatsii-vrachej/{d["slug"]}/"><span class="ic">{I(DOC_ICON.get(d["slug"],"steth"))}</span><h3>{e(d["title"])}</h3><p>{e(d.get("short",""))}</p><span class="meta"><span>{e(first_price(d))}</span><span class="arr">{I("arrow")}</span></span></a>' for d in DOCTORS)
    body = page_hero([], "Консультации врачей", "Приём узких специалистов в одном центре: осмотр, консультация, назначения и процедуры.") + \
        f'<section class="sec" style="padding-top:56px"><div class="wrap"><div class="grid">{docs}</div></div></section>' + form_band()
    pages["konsultatsii-vrachej"] = ("Консультации врачей", "Кардиолог, невролог, офтальмолог, ЛОР, уролог, гинеколог и другие специалисты.", body)

def prices_page():
    def slugify(i): return f"cat-{i}"
    cats = "".join(f'<a href="#{slugify(i)}">{e(c["category"])}</a>' for i, c in enumerate(PRICES))
    secs = ""
    for i, c in enumerate(PRICES):
        rows = "".join(f'<tr data-q="{e((c["category"]+" "+r["name"]).lower())}"><td>{e(r["name"])}</td><td>{e(r.get("price",""))}</td></tr>' for r in c["items"])
        secs += f'<section class="pcat" id="{slugify(i)}"><h2>{e(c["category"])} <small>{len(c["items"])} поз.</small></h2><table class="ptable"><tbody>{rows}</tbody></table></section>'
    total = sum(len(c["items"]) for c in PRICES)
    search = f'<div class="psearch">{I("search")}<input id="psearch" type="search" placeholder="Найти услугу: например, ЭКГ, аудиометрия, кариес" aria-label="Поиск по ценам"></div>'
    body = page_hero([], "Цены на услуги", f"{total} позиций в одном списке. Начните вводить название - список отфильтруется.", search) + \
        f'<div class="wrap" style="padding-bottom:96px"><nav class="pcats" aria-label="Разделы">{cats}</nav>{secs}<div class="pempty" id="pempty" hidden>Ничего не нашлось. Позвоните {PHONE} - подскажем.</div>' \
        f'<p class="note">Цены перенесены с прежнего сайта и уточняются. Не являются публичной офертой. Имеются противопоказания, необходима консультация специалиста.</p></div>'
    pages["stoimost-uslug"] = ("Цены на услуги", "Прайс-лист Морского Медицинского Центра: приёмы врачей, процедуры, диагностика, стоматология.", body)

def business_page():
    biz = by_group("business")
    partners = "".join(f"<span>{e(p)}</span>" for p in SITE.get("partners", []))
    body = page_hero([], "Медосмотры сотрудников по договору",
                     "Предварительные и периодические медосмотры, предрейсовые осмотры, организация медпункта на территории предприятия. Большой опыт в промышленной и морской медицине.",
                     f'<div class="cta-row" style="margin-top:24px"><a class="btn btn-buoy" href="#zapis">Запросить договор {I("arrow")}</a><a class="btn btn-line" href="tel:{TEL}">{I("phone")}{PHONE}</a></div>') + \
    f'''<section class="sec" style="padding-top:56px"><div class="wrap"><div class="grid">{"".join(svc_card(s, False) for s in biz)}</div></div></section>
<section class="sec sec-mist"><div class="wrap">
<div class="sec-head rv"><div><span class="eyebrow">Как работаем</span><h2>От заявки до заключительного акта</h2></div></div>
<div class="steps">
<div class="step rv"><h3>Заявка</h3><p>Вы присылаете количество сотрудников и вредные факторы. Мы считаем стоимость.</p></div>
<div class="step rv"><h3>Договор</h3><p>Согласуем список, график и формат: в центре или с выездом.</p></div>
<div class="step rv"><h3>Осмотр</h3><p>Сотрудники проходят врачей и обследования по согласованному графику.</p></div>
<div class="step rv"><h3>Документы</h3><p>Заключения на каждого сотрудника и итоговые документы для отдела кадров.</p></div>
</div></div></section>
<section class="sec"><div class="wrap"><div class="sec-head rv"><div><span class="eyebrow">Нам доверяют</span><h2>Партнёры центра</h2></div><p>Морской порт, терминалы, строительные и учебные организации.</p></div><div class="partners rv">{partners}</div></div></section>
{form_band("Рассчитаем медосмотр для вашей компании", "Оставьте контакт - пришлём коммерческое предложение и проект договора.", company=True)}'''
    pages["kompaniyam"] = ("Медосмотры для компаний", "Профосмотры, предрейсовые осмотры и медпункты для предприятий по договору.", body)

def about_page():
    hist = SITE.get("history") or []
    hist = hist if isinstance(hist, list) else [hist]
    deps = SITE.get("departments") or []
    head = SITE.get("head") or {}
    hname = head.get("name", "") if isinstance(head, dict) else str(head)
    hrole = head.get("role", "") if isinstance(head, dict) else ""
    partners = "".join(f"<span>{e(p)}</span>" for p in SITE.get("partners", []))
    parts = [
        '<h2>Кто мы</h2><p>Морской Медицинский Центр занимает особую нишу среди клиник Санкт-Петербурга: мы проверяем и сохраняем профессиональное здоровье моряков, портовиков и сотрудников промышленных предприятий. К нам приходят и горожане - за консультацией, диагностикой и справками.</p>',
        f'<h2>Отделения</h2>{ul(deps)}' if deps else "",
        f'<h2>История</h2>{ul(hist, "anchor")}' if hist else "",
        f'<h2>Партнёры</h2><div class="partners">{partners}</div>' if partners else "",
        f'<h2>Руководство</h2><p><b>{e(hname)}</b><br>{e(hrole)}</p>' if hname else "",
    ]
    body = page_hero([], "О центре", "Морская и промышленная медицина в Санкт-Петербурге: медкомиссии, профосмотры, консультации и диагностика рядом с Морским портом.") + \
        f'<div class="wrap layout"><div class="prose">{"".join(parts)}</div>{aside([("uslugi","Справки и комиссии"),("kompaniyam","Компаниям"),("konsultatsii-vrachej","Врачи")], "Разделы")}</div>' + contacts_block()
    pages["o-centre"] = ("О центре", "История, профиль и партнёры Морского Медицинского Центра.", body)

def contacts_page():
    body = page_hero([], "Контакты", f"{ADDR}, {ADDR2}. {HOURS}, {HOURS2.lower()}.") + contacts_block() + form_band()
    pages["kontakty"] = ("Контакты", f"Адрес, телефон и схема проезда: {ADDR}.", body)

def simple(slug, title, lead, html_body, desc):
    body = page_hero([], title, lead) + f'<div class="wrap layout"><div class="prose">{html_body}</div>{aside()}</div>'
    pages[slug] = (title, desc, body)

def static_pages():
    simple("vakansii", "Вакансии", "Ищем медиков, которые любят свою работу.",
           f'<h2>Открытые позиции</h2>{ul(["Фельдшер, посуточно", "Врач-оториноларинголог, с 9:00 до 14:00", "Врач-офтальмолог, с 9:00 до 14:00"], "brief")}'
           f'<p style="margin-top:24px">Резюме присылайте на <a href="mailto:{EMAIL}">{EMAIL}</a> или звоните {PHONE}.</p>'
           '<p class="note">Список перенесён с прежнего сайта (обновлялся в 2021 году) и требует актуализации.</p>',
           "Вакансии Морского Медицинского Центра.")
    simple("politika", "Политика конфиденциальности", "Как мы обрабатываем персональные данные посетителей сайта.",
           '<h2>1. Общие положения</h2><p>Настоящая политика определяет порядок обработки персональных данных ООО «Морской Медицинский Центр» в соответствии с Федеральным законом № 152-ФЗ «О персональных данных».</p>'
           '<h2>2. Какие данные мы получаем</h2><p>Имя, номер телефона, название компании и выбранная услуга - только то, что вы указываете в форме заявки.</p>'
           '<h2>3. Цели обработки</h2><p>Связаться с вами, чтобы записать на приём или ответить на вопрос.</p>'
           '<h2>4. Хранение и передача</h2><p>Данные хранятся на серверах в Российской Федерации и не передаются третьим лицам, кроме случаев, предусмотренных законом.</p>'
           f'<h2>5. Отзыв согласия</h2><p>Отозвать согласие можно письмом на <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>'
           '<p class="note">Черновик для демо-версии. Окончательный текст утверждается клиникой.</p>',
           "Политика обработки персональных данных.")
    simple("info", "Информация для пациентов", "Сведения о медицинской организации по требованиям приказа Минздрава № 956н.",
           '<h2>Сведения об организации</h2>' + ul(["Полное наименование: Общество с ограниченной ответственностью «Морской Медицинский Центр»",
               "ОГРН и дата регистрации: [уточняется]", f"Адрес: {ADDR}", f"Режим работы: {HOURS}, {HOURS2.lower()}"], "building") +
           '<h2>Лицензия</h2>' + ul(["Лицензия на осуществление медицинской деятельности № [уточняется] от [уточняется]", "Перечень работ и услуг по лицензии: [уточняется]"], "file") +
           '<h2>Контролирующие органы</h2>' + ul(["Комитет по здравоохранению Санкт-Петербурга", "Территориальный орган Росздравнадзора по г. Санкт-Петербургу и Ленинградской области",
               "Управление Роспотребнадзора по г. Санкт-Петербургу"], "shield") +
           '<h2>Также на странице будут</h2>' + ul(["Сведения о медицинских работниках и их квалификации", "Правила внутреннего распорядка для пациентов",
               "Права и обязанности граждан в сфере охраны здоровья", "Информация о программе госгарантий и ОМС (если центр участвует)", "Порядок и условия оплаты"], "clip") +
           '<p class="note">Раздел-заготовка: данные помечены [уточняется] и заполняются по документам клиники.</p>',
           "Сведения о медицинской организации по приказу 956н.")

# ---------------------------------------------------------------- build
def write(slug, title, desc, body):
    d = os.path.join(OUT, slug) if slug else OUT
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(layout(slug, title, desc, body))

def main():
    global VER
    VER = str(int(os.path.getmtime(os.path.join(ROOT, "src", "style.css"))) % 100000)
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    home(); hub_services(); hub_doctors(); prices_page(); business_page(); about_page(); contacts_page(); static_pages()
    for s in SERVICES: service_page(s)
    for d in DOCTORS: doctor_page(d)
    for slug, (t, desc, body) in pages.items(): write(slug, t, desc, body)
    shutil.copy(os.path.join(ROOT, "src", "style.css"), OUT)
    shutil.copy(os.path.join(ROOT, "src", "main.js"), OUT)
    os.makedirs(os.path.join(OUT, "img"))
    for f in ("hero.jpg", "hero-m.jpg"): shutil.copy(os.path.join(ROOT, "src", "img", f), os.path.join(OUT, "img", f))
    shutil.copy(os.path.join(ROOT, "src", "img", "logo-mark.svg"), os.path.join(OUT, "img", "logo-mark.svg"))
    shutil.copy(os.path.join(ROOT, "src", "img", "logo-mark.svg"), os.path.join(OUT, "img", "favicon.svg"))
    with open(os.path.join(OUT, "robots.txt"), "w") as f: f.write("User-agent: *\nDisallow: /\n")
    bad = [p for p in pages if "—" in pages[p][2] or "–" in pages[p][2]]
    print(f"built {len(pages)} pages -> {OUT}" + (f"  WARNING dashes in: {bad}" if bad else ""))

VER = "1"
if __name__ == "__main__":
    main()
