"""Build the v6 hub pages, FlowFrame articles and simple pages.
Usage: python3 _tools/build_site.py
- Hubs (/, /guides/, /finds/) are generated from the data below and from _tools/guides/*.json.
- Articles (/guides/<slug>/) and simple pages keep their written content: the script reads the
  <article> body from the current file (or from _tools/src/ once archived) and re-wraps it."""
import html, json, os, re, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chrome import head, top, footer, mosaic, split_hero, promise, ARROW, MARK_FF, days_left

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
    {"url": "/guides/ai-tools-for-planning-2027/", "tag": "AI planning tools", "img": U("1513128034602-7814ccaddd4e"),
     "alt": "Hands holding a notepad and pen on a desk",
     "title": "7 AI tools for planning 2027, and what each one costs",
     "desc": "Reclaim.ai, MeetGeek, monday.com, ClickUp, Gamma, Canva and ElevenLabs: free plans, real prices and who each suits."},
    {"url": "/guides/best-webcams-for-video-calls/", "tag": "Home-office gear", "img": U("1758521541657-fd70465a5c54"),
     "alt": "A smiling woman waving hello on a video call", "chip": "New", "pop": True,
     "title": "Best webcams for video calls in 2026: 7 picks from $25 to $199",
     "desc": "From a $25 fix for a grainy laptop camera to 4K: what each webcam costs, who it suits and the catch.", "go": "See the 7 picks"},
]
ARTICLE_HERO = {
    "gamma-vs-canva-vs-copilot": AI_GUIDES[0],
    "best-ai-meeting-note-takers": AI_GUIDES[1],
    "ai-tools-for-planning-2027": AI_GUIDES[2],
    "best-webcams-for-video-calls": AI_GUIDES[3],
}


def ff_grid():
    """Newest FlowFrame guide as a full-width feature card, the rest below."""
    return card(AI_GUIDES[-1], True) + "".join(card(c) for c in AI_GUIDES[:-1])


def img(src, alt, sizes="100vw", w=1600, h=900, eager=False):
    def u(px):
        return f"{src}?auto=format&fit=crop&q=70&w={px}&h={round(px*h/w)}"
    ws = (640, 1200, 2000) if w >= 1200 else (480, 800, 1200)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="{u(ws[1])}" srcset="{", ".join(f"{u(x)} {x}w" for x in ws)}" sizes="{sizes}" '
            f'alt="{E(alt)}" width="{ws[1]}" height="{round(ws[1]*h/w)}" {load}>')


def page(title, desc, url, theme, body, og=None, active=None):
    brand = "Digittouch Finds" if theme == "finds" else "FlowFrame"
    full = title if brand in title else f"{title} | {brand}"
    return (head(full, desc, url, theme, og) + f'</head><body class="v6 {theme}">' + top(theme, active or url)
            + f"<main>{body}</main>" + footer(theme) + "</body></html>")


def card(c, feature=False):
    chip = f'<span class="chip{" pop" if c.get("pop") else ""}">{E(c["chip"])}</span>' if c.get("chip") else ""
    cat = f'<p class="cat">{E(c["tag"])}</p>' if c.get("tag") else ""
    sizes = "(max-width:860px) 100vw, 700px" if feature else "(max-width:640px) 100vw, (max-width:1000px) 50vw, 400px"
    return (f'<a class="card{" feature" if feature else ""}" href="{c["url"]}"><div class="ph">{img(c["img"], c["alt"], sizes, 1200, 750)}{chip}</div>'
            f'<div class="tx">{cat}<h3>{E(c["title"])}</h3><p>{E(c["desc"])}</p><span class="go">{c.get("go", "Read the guide")} {ARROW}</span></div></a>')


def tile(src, alt, ratio, sizes):
    w, h = ratio
    return img(src, alt, sizes, w * 100, h * 100, eager=True)


def finds_cards():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "_tools", "guides", "*.json")), key=os.path.getmtime, reverse=True):
        d = json.load(open(f))
        n = sum(len(b["items"]) for b in d["bands"])
        out.append({"url": f'/finds/{d["slug"]}/', "img": d["hero"]["img"], "alt": d["hero"]["alt"], "chip": f"{n} picks",
                    "tag": "Gift guide", "go": "See the gifts",
                    "title": re.sub(r"\s*\((Before )?Black Friday 2026\)", "", d["title"]), "desc": d["description"]})
    return out


DESK = U("1596443019365-eb263a588404")


def build_home():
    fc = finds_cards()
    g0, g1 = AI_GUIDES[:2]
    btns = ('<div class="s-btns"><a class="s-btn primary" href="/guides/">Browse the AI guides</a>'
            '<a class="s-btn ghost" href="/finds/">Black Friday gift guides</a></div>')
    tiles = [tile(g0["img"], g0["alt"], (3, 4), "(max-width:960px) 60vw, 360px"),
             tile(g1["img"], g1["alt"], (1, 1), "(max-width:960px) 40vw, 280px"),
             tile(DESK, "A tidy desk with a monitor", (1, 1), "(max-width:960px) 40vw, 280px")]
    body = split_hero("", 'Pick the right AI tool the first time',
                      "Plain-English comparisons of AI productivity software and home-office gear: what is free, what it costs, and who should skip it.",
                      btns, ["Prices checked monthly", "No paid placements", "The downside of every tool"],
                      mosaic(tiles, ("Nov", "prices checked this month")))
    body += '<div class="s-wrap">'
    body += ('<section class="sec"><div class="sec-head"><div><h2>Latest comparisons</h2><p>One question per guide, answered with prices, free plans and a clear pick.</p></div>'
             '<a class="more" href="/guides/">All AI guides</a></div>'
             f'<div class="grid">{ff_grid()}</div></section>')
    body += promise([("scale", "We compare, you choose", "Every guide ends with a 30-second way to pick the right tool for how you work."),
                     ("tag", "Real prices, dated", "Free plans and paid prices are checked against the vendors and dated in each guide."),
                     ("eye", "The honest catch", "Every pick says who should skip it, not just who should buy it.")])
    minis = "".join(f'<a href="{c["url"]}">{img(c["img"], c["alt"], "(max-width:860px) 45vw, 260px", 600, 450)}<span>{E(c["title"])}</span></a>' for c in fc[:4])
    body += ('<section class="xband finds-side"><div><h2>Black Friday gift guides</h2><p>Our sister site Digittouch Finds rounds up the gifts people are actually buying, '
             'from under $25 to proper splurges, each with the honest catch.</p><a class="s-btn primary" href="/finds/">See all gift guides</a></div>'
             f'<div class="minis">{minis}</div></section>')
    body += "</div>"
    return page("FlowFrame: honest comparisons of AI tools and home-office gear",
                "Plain-English comparisons of AI productivity tools and home-office gear, so you pick the right one the first time.",
                "/", "ff", body, g0["img"] + "?w=1200&h=630&fit=crop", active="")


def build_guides_index():
    head_ = ('<section class="ph-head"><div class="s-wrap"><p class="crumb"><a href="/">FlowFrame</a><span>/</span>AI guides</p>'
             '<h1>FlowFrame guides</h1><p class="sub">Plain-English comparisons of AI tools and home-office gear, with the free and cheap options first.</p></div></section>')
    body = head_ + f'<div class="s-wrap"><section class="sec" style="padding-top:48px"><div class="grid">{ff_grid()}</div></section>'
    body += promise([("scale", "One question per guide", "Each guide answers one decision, like which AI note-taker to use, and ends with a clear pick."),
                     ("tag", "Free plans first", "We start with what you can do for free, then show exactly what paying adds."),
                     ("eye", "Who should skip it", "Every tool gets an honest downside so you can rule it out quickly.")]) + "</div>"
    return page("AI tool guides", "Every FlowFrame comparison of AI productivity tools and home-office gear.", "/guides/", "ff", body)


def build_finds_index():
    fc = finds_cards()
    btns = (f'<div class="s-btns"><a class="s-btn primary" href="#all-guides">Browse the gift guides</a>'
            f'<a class="s-btn ghost" href="{fc[0]["url"]}">Newest guide</a></div>')
    tiles = [tile(fc[0]["img"], fc[0]["alt"], (3, 4), "(max-width:960px) 60vw, 360px"),
             tile(fc[1]["img"], fc[1]["alt"], (1, 1), "(max-width:960px) 40vw, 280px"),
             tile(fc[2]["img"], fc[2]["alt"], (1, 1), "(max-width:960px) 40vw, 280px")]
    body = split_hero("", 'Gifts people are actually buying',
                      "Gift guides sorted by budget and by who they are for, with the one thing to know before you buy each.",
                      btns, [f"{len(fc)} gift guides", "Prices checked weekly", "The catch on every pick"],
                      mosaic(tiles, (str(days_left()), "days to Black Friday"), countdown=True))
    first = dict(fc[0], chip="Newest", pop=True)
    body += (f'<div class="s-wrap"><section class="sec" id="all-guides"><div class="sec-head"><div><h2>Gift guides</h2><p>Updated for Black Friday 2026. New guides every week.</p></div></div>'
             f'<div class="grid">{card(first, True)}{"".join(card(c) for c in fc[1:])}</div></section>')
    body += promise([("people", "Sorted the way you shop", "By budget and by who it is for, so you can find a gift in a minute."),
                     ("eye", "The honest catch", "Every pick says what to know before you buy, not just why it is great."),
                     ("tag", "Prices we check", "Prices are dated, and we only call something a deal when we have seen it drop.")])
    ffm = "".join(f'<a href="{c["url"]}">{img(c["img"], c["alt"], "(max-width:860px) 45vw, 260px", 600, 450)}<span>{E(c["title"].split(":")[0])}</span></a>' for c in AI_GUIDES)
    body += ('<section class="xband ff-side"><div><h2>Shopping for work tools?</h2><p>Our sister site FlowFrame compares AI tools and home-office gear in plain English, with free options first.</p>'
             f'<a class="s-btn primary" href="/guides/">See the AI guides</a></div><div class="minis">{ffm}</div></section></div>')
    return page("Digittouch Finds: gift guides and what's selling now",
                "Gift guides and weekly roundups of what people are actually buying, sorted by budget and by who it is for, with the honest catch on each.",
                "/finds/", "finds", body, fc[0]["img"] + "?w=1200&h=630&fit=crop")


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
    # contents: give every h2 an id
    toc = []
    def hid(m):
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        i = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:48]
        toc.append((i, html.unescape(t)))
        return f'<h2 id="{i}">{m.group(1)}</h2>'
    art = re.sub(r"<h2>(.*?)</h2>", hid, art, flags=re.S)
    tocl = "".join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t in toc)
    head_ = (f'<section class="ph-head"><div class="s-wrap ph-split"><div><p class="crumb"><a href="/guides/">AI guides</a><span>/</span>{E(h["tag"])}</p>'
             f'<h1>{E(title)}</h1><div class="byline"><span class="who">{MARK_FF}FlowFrame team</span><span>Updated {E(nice_date(updated))}</span><span>Prices checked Nov 2026</span></div></div>'
             f'<figure>{img(h["img"], h["alt"], "(max-width:860px) 100vw, 520px", 1200, 900, eager=True)}</figure></div></section>')
    aside = (f'<aside class="toc"><b>On this page</b><ol>{tocl}</ol><div class="tbox"><p>Shopping for gifts this Black Friday?</p>'
             '<a href="/finds/">See our gift guides</a></div>'
             '<div class="tbox"><p>Learn on the go: audiobooks and podcasts for the commute. Free trial on Amazon.</p>'
             '<a href="https://www.amazon.com/hz/audible/mlp?tag=digittouch-20" rel="nofollow sponsored noopener" target="_blank">Try Audible free</a></div></aside>')
    others = [c for c in AI_GUIDES if c["url"] != f"/guides/{slug}/"]
    body = head_ + f'<div class="s-wrap a-layout"><article class="a-body">{art}</article>{aside}</div>'
    body += ('<div class="s-wrap"><section class="sec"><div class="sec-head"><div><h2>Keep reading</h2></div></div>'
             f'<div class="grid two">{"".join(card(c) for c in others)}{card(dict(finds_cards()[0], chip="Gift guide", pop=True))}</div></section></div>')
    return page(title, desc, f"/guides/{slug}/", "ff", body, h["img"] + "?w=1200&h=630&fit=crop", active="/guides/")


def nice_date(d):
    import datetime
    try:
        x = datetime.date.fromisoformat(d.strip())
        return f"{x.day} {x.strftime('%b %Y')}"
    except ValueError:
        return d


SUBS = {"about": "Who we are and how we choose what to recommend.", "contact": "Questions, corrections or partnership ideas: here is how to reach us.",
        "disclosure": "How FlowFrame and Digittouch Finds make money, and what that does and does not change.",
        "privacy": "What we collect when you visit, and what we do with it."}


def build_simple(rel, crumb_theme="ff"):
    s = source(rel)
    art = re.search(r"<article>(.*)</article>", s, re.S).group(1)
    t = html.unescape(re.search(r"<h1>(.*?)</h1>", art, re.S).group(1))
    art = re.sub(r"\s*<h1>.*?</h1>", "", art, count=1, flags=re.S)
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(m.group(1)) if m else t
    key = rel.split("/")[0]
    body = (f'<section class="ph-head"><div class="s-wrap"><p class="crumb"><a href="/">Home</a><span>/</span>{E(t)}</p><h1>{E(t)}</h1>'
            f'<p class="sub">{E(SUBS.get(key, ""))}</p></div></section><div class="p-body">{art}</div>')
    url = "/" + rel.replace("index.html", "")
    return page(t, desc, url, crumb_theme, body)


def build_404():
    body = ('<section class="ph-head"><div class="s-wrap"><p class="crumb">Page not found</p><h1>We could not find that page</h1>'
            '<p class="sub">It may have moved when we updated the site. These are the best places to start.</p></div></section>'
            '<div class="s-wrap"><section class="sec" style="padding-top:48px"><div class="grid">'
            + card(dict(finds_cards()[0], chip="Gift guide", pop=True)) + card(AI_GUIDES[-1]) + card(AI_GUIDES[0]) + '</div></section></div>')
    return page("Page not found", "The page you were looking for could not be found.", "/404.html", "ff", body, active="")


if __name__ == "__main__":
    out = {
        "index.html": build_home(),
        "guides/index.html": build_guides_index(),
        "finds/index.html": build_finds_index(),
        "guides/gamma-vs-canva-vs-copilot/index.html": build_article("gamma-vs-canva-vs-copilot"),
        "guides/best-ai-meeting-note-takers/index.html": build_article("best-ai-meeting-note-takers"),
        "guides/ai-tools-for-planning-2027/index.html": build_article("ai-tools-for-planning-2027"),
        "guides/best-webcams-for-video-calls/index.html": build_article("best-webcams-for-video-calls"),
        "404.html": build_404(),
    }
    for rel in ["about/index.html", "contact/index.html", "disclosure/index.html", "privacy/index.html"]:
        out[rel] = build_simple(rel)
    for rel, s in out.items():
        open(os.path.join(ROOT, rel), "w").write(s)
        print("wrote", rel)
