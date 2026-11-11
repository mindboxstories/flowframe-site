"""Build the v5 hub pages, FlowFrame articles and simple pages.
Usage: python3 _tools/build_site.py
- Hubs (/, /guides/, /finds/) are generated from the data below and from _tools/guides/*.json.
- Articles (/guides/<slug>/) and simple pages keep their written content: the script reads the
  <article> body from the current file (or from _tools/src/ once archived) and re-wraps it."""
import html, json, os, re, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "_tools", "src")
E = html.escape
V = "3"
FONTS = ('<link rel="preconnect" href="https://images.unsplash.com"><link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,600..700,50'
         '&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">')
U = lambda i: "https://images.unsplash.com/photo-" + i

AI_GUIDES = [
    {"url": "/guides/gamma-vs-canva-vs-copilot/", "tag": "AI presentations", "img": U("1590098563734-bcea80ce34c7"),
     "alt": "Someone building slides on a laptop", "chip": "Most read",
     "title": "Gamma vs Canva vs Copilot: which AI presentation maker should you use?",
     "desc": "Free options, prices, exports and exactly who each AI presentation maker suits, in plain English."},
    {"url": "/guides/best-ai-meeting-note-takers/", "tag": "AI note-takers", "img": U("1588196749597-9ff075ee6b5b"),
     "alt": "A video call on a laptop next to a mug",
     "title": "Best AI meeting note-takers in 2026: Fathom, Granola, Otter or Fireflies?",
     "desc": "Free plans, prices, and whether a bot joins your call: the right note-taker for how you work."},
]
ARTICLE_HERO = {
    "gamma-vs-canva-vs-copilot": AI_GUIDES[0],
    "best-ai-meeting-note-takers": AI_GUIDES[1],
}


def img(src, alt, sizes="100vw", w=1600, h=900, eager=False):
    def u(px):
        return f"{src}?auto=format&fit=crop&q=70&w={px}&h={round(px*h/w)}"
    ws = (640, 1200, 2000) if w >= 1200 else (480, 800, 1200)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="{u(ws[1])}" srcset="{", ".join(f"{u(x)} {x}w" for x in ws)}" sizes="{sizes}" '
            f'alt="{E(alt)}" width="{ws[1]}" height="{round(ws[1]*h/w)}" {load}>')


def page(title, desc, url, theme, body, og=None):
    finds = theme == "finds"
    brand = "Digittouch Finds" if finds else "FlowFrame"
    logo = ('<a class="logo" href="/finds/">Digittouch <span>Finds</span></a>' if finds
            else '<a class="logo" href="/">Flow<span>Frame</span></a>')
    nav = ('<nav><a href="/finds/">Finds</a><a href="/">FlowFrame</a><a href="/about/">About</a></nav>' if finds
           else '<nav><a href="/guides/">Guides</a><a href="/finds/">Gift guides</a><a href="/about/">About</a></nav>')
    full = title if brand in title else f"{title} | {brand}"
    ogimg = f'<meta property="og:image" content="{og}">' if og else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="https://flowframe.shop{url}">
<meta property="og:title" content="{E(full)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="https://flowframe.shop{url}">{ogimg}
<meta name="theme-color" content="{'#17151A' if finds else '#14213D'}">
{FONTS}<link rel="stylesheet" href="/site.css?v={V}">
</head><body class="v5 {'finds' if finds else 'ff'}">
<header class="site"><div class="s-wrap">{logo}{nav}</div></header>
<main>{body}</main>
<footer class="site"><div class="s-wrap"><p><a href="/disclosure/">Affiliate disclosure</a><a href="/privacy/">Privacy</a><a href="/about/">About</a><a href="/contact/">Contact</a></p>
<p>&copy; 2026 {brand}, part of Digittouch Enterprise. As an Amazon Associate we earn from qualifying purchases.</p></div></footer>
</body></html>'''


def card(c, feature=False):
    chip = f'<span class="chip{" pop" if c.get("pop") else ""}">{E(c["chip"])}</span>' if c.get("chip") else ""
    sizes = "(max-width:1000px) 100vw, 700px" if feature else "(max-width:640px) 100vw, (max-width:1000px) 50vw, 380px"
    return (f'<a class="s-card{" feature" if feature else ""}" href="{c["url"]}"><div class="ph">{img(c["img"], c["alt"], sizes, 1200, 750)}{chip}</div>'
            f'<div class="tx"><h3>{E(c["title"])}</h3><p>{E(c["desc"])}</p><span class="go">Read the guide</span></div></a>')


def hero(img_src, alt, crumb, h1, lede, btns="", meta=None, short=False):
    m = "".join(f"<li>{E(x)}</li>" for x in (meta or []))
    return (f'<section class="s-hero{" short" if short else ""}">{img(img_src, alt, eager=True)}<div class="s-wrap"><div class="s-hero-copy">'
            f'{crumb}<h1>{h1}</h1>{f"<p class=lede>{E(lede)}</p>" if lede else ""}{btns}{f"<ul class=s-meta>{m}</ul>" if m else ""}</div></div></section>')


def finds_cards():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "_tools", "guides", "*.json")), key=os.path.getmtime, reverse=True):
        d = json.load(open(f))
        n = sum(len(b["items"]) for b in d["bands"])
        out.append({"url": f'/finds/{d["slug"]}/', "img": d["hero"]["img"], "alt": d["hero"]["alt"], "chip": f"{n} picks",
                    "title": re.sub(r"\s*\((Before )?Black Friday 2026\)", "", d["title"]), "desc": d["description"]})
    return out


def build_home():
    fc = finds_cards()
    btns = ('<div class="s-btns"><a class="s-btn primary" href="/guides/">Browse AI guides</a>'
            '<a class="s-btn ghost" href="/finds/">Black Friday gift guides</a></div>')
    body = hero(U("1521185496955-15097b20c5fe"), "A laptop and notebook on a wooden desk", "",
                'Work smarter with the <span class="hl">right AI tools</span>',
                "Plain-English comparisons of AI productivity software and home-office gear, so you pick the right one the first time.",
                btns, ["Prices checked monthly", "No paid placements", "Honest downsides"])
    body += '<div class="s-wrap">'
    body += ('<section class="s-section"><div class="s-head"><h2>Latest guides</h2><p>New comparison every week</p></div>'
             f'<div class="s-grid two">{"".join(card(c) for c in AI_GUIDES)}</div></section>')
    body += ('<section class="s-strip"><div><b>We compare, you choose</b><p>Every guide ends with a 30-second way to pick the right tool for you.</p></div>'
             '<div><b>Real prices, dated</b><p>Free plans and paid prices are checked against the vendors and dated in each guide.</p></div>'
             '<div><b>The honest catch</b><p>Every pick says who should skip it, not just who should buy it.</p></div></section>')
    minis = "".join(f'<a href="{c["url"]}">{img(c["img"], c["alt"], "200px", 600, 450)}<span>{E(c["title"])}</span></a>' for c in fc[:4])
    body += ('<section class="s-band"><div><h2>Black Friday gift guides</h2><p>Our sister site Digittouch Finds rounds up the gifts people are actually buying, '
             'from under $25 to proper splurges, each with the honest catch.</p><a class="s-btn primary" href="/finds/">See all gift guides</a></div>'
             f'<div class="mini">{minis}</div></section>')
    body += "</div>"
    return page("FlowFrame: honest reviews of AI tools and home-office gear",
                "Plain-English comparisons of AI productivity tools and home-office gear, so you pick the right one the first time.",
                "/", "ff", body, U("1521185496955-15097b20c5fe") + "?w=1200&h=630&fit=crop")


def build_guides_index():
    body = hero(U("1596443019365-eb263a588404"), "A dark desk with a monitor", '<p class="s-crumb"><a href="/">FlowFrame</a> / Guides</p>',
                "All guides", "Side-by-side comparisons of the AI tools worth paying for, with free options first.", short=True)
    body += f'<div class="s-wrap"><section class="s-section"><div class="s-grid two">{"".join(card(c) for c in AI_GUIDES)}</div></section></div>'
    return page("All guides", "Every FlowFrame comparison of AI productivity tools and home-office gear.", "/guides/", "ff", body)


def build_finds_index():
    fc = finds_cards()
    btns = (f'<div class="s-btns"><a class="s-btn primary" href="{fc[0]["url"]}">See the newest guide</a>'
            '<a class="s-btn ghost" href="#all-guides">All gift guides</a></div>')
    body = hero(U("1513884923967-4b182ef167ab"), "Red and white gift bags", "",
                'What people are buying, <span class="hl">found for you</span>',
                "Gift guides and weekly roundups of the things people are actually buying, sorted by budget and by who they're for, with the honest catch on each.",
                btns, [f"{len(fc)} gift guides", "Prices checked weekly", "Black Friday is 27 November"])
    first, rest = fc[0], fc[1:]
    first = dict(first, chip="Newest", pop=True)
    body += (f'<div class="s-wrap"><section class="s-section" id="all-guides"><div class="s-head"><h2>Gift guides</h2><p>Updated for Black Friday 2026</p></div>'
             f'<div class="s-grid">{card(first, True)}{"".join(card(c) for c in rest)}</div></section>'
             '<section class="s-strip"><div><b>Sorted the way you shop</b><p>By budget and by who it is for, so you can find a gift in a minute.</p></div>'
             '<div><b>The honest catch</b><p>Every pick says what to know before you buy, not just why it is great.</p></div>'
             '<div><b>Prices we check</b><p>Prices are dated, and we only call something a deal when we have seen it drop.</p></div></section></div>')
    return page("Digittouch Finds: gift guides and what's selling now",
                "Gift guides and weekly roundups of what people are actually buying, sorted by budget and by who it is for, with the honest catch on each.",
                "/finds/", "finds", body, U("1513884923967-4b182ef167ab") + "?w=1200&h=630&fit=crop")


def source(rel):
    """Original written content: archived copy in _tools/src/, else the current file (first run)."""
    arch = os.path.join(SRC, rel)
    path = arch if os.path.exists(arch) else os.path.join(ROOT, rel)
    s = open(path).read()
    if not os.path.exists(arch):
        os.makedirs(os.path.dirname(arch), exist_ok=True)
        open(arch, "w").write(s)
    return s


def build_article(slug):
    rel = f"guides/{slug}/index.html"
    s = source(rel)
    title = html.unescape(re.search(r"<h1>(.*?)</h1>", s, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    meta = re.sub(r"<[^>]+>", "", re.search(r'<p class="meta">(.*?)</p>', s, re.S).group(1))
    updated = html.unescape(meta).split("Updated")[-1].strip()
    art = re.search(r"<article>(.*)</article>", s, re.S).group(1)
    art = re.sub(r'\s*<span class="tag">.*?</span>\s*<h1>.*?</h1>\s*<p class="meta">.*?</p>', "", art, flags=re.S)
    art = art.replace("<p class=\"disclosure\">", "<p class=\"disclosure\">")
    art = re.sub(r"<p>\s*(<strong>Quick answer:</strong>)", r'<p class="a-quick">\1', art)
    art = re.sub(r"<p>\s*<strong>Choose it if</strong>(.*?)<br>\s*<strong>Skip it if</strong>(.*?)</p>",
                 r'<div class="a-verdict"><p class="a-choose"><strong>Choose it if</strong>\1</p><p class="a-skip"><strong>Skip it if</strong>\2</p></div>',
                 art, flags=re.S)
    art = re.sub(r"<p>\s*(<strong>Choose it if)", r'<p class="a-choose">\1', art)
    art = re.sub(r"<ul>((?:\s*<li><strong>[^<]{3,80}\?</strong>.*?</li>)+\s*)</ul>", r'<div class="a-picks">\1</div>', art, flags=re.S)
    art = re.sub(r'(<div class="a-picks">.*?</div>)', lambda m: m.group(1).replace("<li>", "<p>").replace("</li>", "</p>"), art, flags=re.S)
    h = ARTICLE_HERO[slug]
    body = hero(h["img"], h["alt"], f'<p class="s-crumb"><a href="/guides/">Guides</a> / {E(h["tag"])}</p>',
                E(title), "", "", [f"By FlowFrame", f"Updated {updated}", "Prices checked Nov 2026"], short=True)
    others = [c for c in AI_GUIDES if c["url"] != f"/guides/{slug}/"]
    body += f'<div class="a-body">{art}</div>'
    body += ('<section class="a-more"><div class="s-head"><h2>Keep reading</h2></div>'
             f'<div class="s-grid two">{"".join(card(c) for c in others)}{card(dict(finds_cards()[0], chip="Gift guide", pop=True))}</div></section>')
    return page(title, desc, f"/guides/{slug}/", "ff", body, h["img"] + "?w=1200&h=630&fit=crop")


def build_simple(rel, crumb_theme="ff"):
    s = source(rel)
    art = re.search(r"<article>(.*)</article>", s, re.S).group(1)
    t = html.unescape(re.search(r"<h1>(.*?)</h1>", art, re.S).group(1))
    art = re.sub(r"\s*<h1>.*?</h1>", "", art, count=1, flags=re.S)
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(m.group(1)) if m else t
    body = hero(U("1599008633840-052c7f756385"), "A notebook on a wooden desk", "", E(t), "", short=True)
    body += f'<div class="p-body">{art}</div>'
    url = "/" + rel.replace("index.html", "")
    return page(t, desc, url, crumb_theme, body)


if __name__ == "__main__":
    out = {
        "index.html": build_home(),
        "guides/index.html": build_guides_index(),
        "finds/index.html": build_finds_index(),
        "guides/gamma-vs-canva-vs-copilot/index.html": build_article("gamma-vs-canva-vs-copilot"),
        "guides/best-ai-meeting-note-takers/index.html": build_article("best-ai-meeting-note-takers"),
    }
    for rel in ["about/index.html", "contact/index.html", "disclosure/index.html", "privacy/index.html"]:
        out[rel] = build_simple(rel)
    for rel, s in out.items():
        open(os.path.join(ROOT, rel), "w").write(s)
        print("wrote", rel)
