"""Shared page chrome (head assets, announcement bar, header, footer, split hero) for
build_site.py and build_guide.py, so every page on flowframe.shop shares one design."""
import html, datetime

E = html.escape
SITE_CSS_V = "5"
DEAL_DATE = "2026-11-27"
U = lambda i: "https://images.unsplash.com/photo-" + i

FONTS = ('<link rel="preconnect" href="https://images.unsplash.com"><link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,500..700,50'
         '&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')

MARK_FF = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#14213D"/>'
           '<rect x="7.5" y="7.5" width="17" height="17" rx="3.5" fill="none" stroke="#F2A541" stroke-width="2.6"/>'
           '<path d="M9 19.5c3-4 6 1 9-2.5s4-3 5.5-2" fill="none" stroke="#3FC1C3" stroke-width="2.6" stroke-linecap="round"/></svg>')
MARK_DF = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="9" fill="#E4572E"/>'
           '<path d="M9 13.2 15.6 7h7.4v7.4L16.8 21a2 2 0 0 1-2.8 0L9 16a2 2 0 0 1 0-2.8Z" fill="#FFF8EF"/>'
           '<circle cx="19.4" cy="10.6" r="1.7" fill="#E4572E"/><path d="M9.5 23.5h13" stroke="#FFC93C" stroke-width="2.6" stroke-linecap="round"/></svg>')

FINDS_NAV = [("/finds/", "All gift guides"), ("/finds/gifts-for-her-under-60/", "For her"),
             ("/finds/gifts-under-25/", "Under $25"), ("/finds/work-from-home-gifts/", "Home office"),
             ("/finds/kitchen-gifts-home-cook/", "Kitchen")]
FF_NAV = [("/guides/", "AI guides"), ("/finds/", "Gift guides"), ("/about/", "About")]


def days_left():
    return max(0, (datetime.date.fromisoformat(DEAL_DATE) - datetime.date.today()).days)


def head(title, desc, url, theme, og=None, extra_css=""):
    finds = theme == "finds"
    ogimg = f'<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">' if og else ""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="https://flowframe.shop{url}">'
            f'<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">'
            f'<meta property="og:url" content="https://flowframe.shop{url}">{ogimg}'
            f'<meta name="theme-color" content="#FBF7F2"><link rel="icon" href="/{"favicon-finds" if finds else "favicon"}.svg" type="image/svg+xml">'
            f'{FONTS}<link rel="stylesheet" href="/site.css?v={SITE_CSS_V}">{extra_css}')


def top(theme, active=""):
    finds = theme == "finds"
    d = days_left()
    ann = (f'<div class="ann" data-countdown="{DEAL_DATE}"><div class="s-wrap"><span>Black Friday is 27 November: '
           f'<b class="ann-days">{d} days</b> to go.<i class="x"> Our gift guides are re-checked every week.</i></span>'
           f'<a href="/finds/">Shop the gift guides</a></div></div>')
    if finds:
        brand = f'<a class="brand" href="/finds/">{MARK_DF}<span>Digittouch <em>Finds</em></span></a>'
        nav = "".join(f'<a href="{u}"{" aria-current=page" if u == active else ""}>{E(t)}</a>' for u, t in FINDS_NAV)
        cta = '<a class="hcta ghost" href="/">FlowFrame AI guides</a>'
    else:
        brand = f'<a class="brand" href="/">{MARK_FF}<span>Flow<em>Frame</em></span></a>'
        nav = "".join(f'<a href="{u}"{" aria-current=page" if u == active else ""}>{E(t)}</a>' for u, t in FF_NAV)
        cta = '<a class="hcta" href="/finds/">Black Friday picks</a>'
    return (f'{ann}<header class="hd"><div class="s-wrap hd-in">{brand}<nav class="hd-nav" aria-label="Main">{nav}</nav>{cta}</div></header>')


def footer(theme):
    finds = theme == "finds"
    brand = (f'<a class="brand" href="/finds/">{MARK_DF}<span>Digittouch <em>Finds</em></span></a>' if finds
             else f'<a class="brand" href="/">{MARK_FF}<span>Flow<em>Frame</em></span></a>')
    blurb = ("Gift guides and weekly roundups of what people are actually buying, with the honest catch on every pick."
             if finds else "Plain-English comparisons of AI tools and home-office gear, so you pick the right one the first time.")
    gl = "".join(f'<a href="{u}">{E(t)}</a>' for u, t in FINDS_NAV)
    fl = ('<a href="/">FlowFrame home</a><a href="/guides/">All AI guides</a>'
          '<a href="/guides/gamma-vs-canva-vs-copilot/">AI presentation makers</a><a href="/guides/best-ai-meeting-note-takers/">AI note-takers</a>')
    cl = '<a href="/about/">About us</a><a href="/contact/">Contact</a><a href="/disclosure/">Affiliate disclosure</a><a href="/privacy/">Privacy</a>'
    return (f'<footer class="ft"><div class="s-wrap"><div class="ft-grid"><div class="ft-brand">{brand}<p>{blurb}</p></div>'
            f'<div><h4>Gift guides</h4>{gl}</div><div><h4>FlowFrame</h4>{fl}</div><div><h4>Company</h4>{cl}</div></div>'
            f'<div class="ft-legal"><span>&copy; 2026 Digittouch Enterprise. FlowFrame and Digittouch Finds.</span>'
            f'<span>As an Amazon Associate we earn from qualifying purchases.</span></div></div></footer>'
            f'<script src="/site.js?v={SITE_CSS_V}" defer></script>')


def mosaic(tiles, badge=None, countdown=False):
    """tiles: 3 <img> strings; badge: (big, small) round sticker; countdown=True makes site.js keep the number live."""
    cd = f' data-countdown="{DEAL_DATE}"' if countdown else ""
    b = f'<div class="mz-badge"{cd}><b>{badge[0]}</b><span>{E(badge[1])}</span></div>' if badge else ""
    return f'<div class="mz">{"".join(f"<figure>{t}</figure>" for t in tiles[:3])}{b}</div>'


ARROW = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8h9M8.5 4.5 12 8l-3.5 3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICONS = {
 "scale": '<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="12" fill="currentColor" opacity=".12"/><path d="M20 11v18M13 29h14M12 15h16M12 15l-3 7h6zM28 15l-3 7h6z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/></svg>',
 "tag": '<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="12" fill="currentColor" opacity=".12"/><path d="M11 20.5 19.5 12H28v8.5L19.5 29a1.5 1.5 0 0 1-2.1 0L11 22.6a1.5 1.5 0 0 1 0-2.1Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="24" cy="16" r="1.6" fill="currentColor"/></svg>',
 "eye": '<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="12" fill="currentColor" opacity=".12"/><path d="M9 20s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7Z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="20" cy="20" r="3.2" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
 "people": '<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="12" fill="currentColor" opacity=".12"/><circle cx="16" cy="16" r="3.6" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="25.5" cy="17.5" r="2.8" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M9.5 28c.8-3.8 3.4-6 6.5-6s5.7 2.2 6.5 6M22.5 23.3c.9-.5 1.9-.8 3-.8 2.4 0 4.4 1.8 5 5.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}


def promise(items):
    """items: list of (icon, title, text)."""
    return '<section class="promise">' + "".join(f'<div>{ICONS[i]}<b>{E(t)}</b><p>{E(p)}</p></div>' for i, t, p in items) + '</section>'


def split_hero(crumb, h1, lede, btns, points, mosaic_html):
    pts = "".join(f"<li>{E(p)}</li>" for p in points)
    return (f'<section class="hero2"><div class="s-wrap hero2-in"><div class="hero2-copy">{crumb}<h1>{h1}</h1>'
            f'<p class="lede">{E(lede)}</p>{btns}<ul class="ticks">{pts}</ul></div>{mosaic_html}</div></section>')
