"""Build a Digittouch Finds gift guide page (design v4, photo-led) from a JSON data file.
Usage: python3 _tools/build_guide.py _tools/guides/<slug>.json
Writes finds/<slug>/index.html using finds/guide.css and finds/guide.js.

Images: "img" fields are Unsplash photo URLs (https://images.unsplash.com/photo-...),
free for commercial use under the Unsplash licence. They are lifestyle images, not the
exact products; the page says so. Swap in Amazon product images once PA-API is available."""
import json, sys, html, urllib.parse, os, datetime

E = html.escape
SITE = "https://flowframe.shop"
TAG = "digittouch-20"


def amazon(item):
    if item.get("asin"):
        return f"https://www.amazon.com/dp/{item['asin']}?tag={TAG}"
    return "https://www.amazon.com/s?" + urllib.parse.urlencode({"k": item["q"], "tag": TAG})


def img(src, alt, sizes, ratio="4/3", eager=False, widths=(480, 800, 1200)):
    w, h = (int(x) for x in ratio.split("/"))
    def u(px):
        return f"{src}?auto=format&fit=crop&q=70&w={px}&h={round(px*h/w)}"
    srcset = ", ".join(f"{u(px)} {px}w" for px in widths)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="{u(widths[1])}" srcset="{srcset}" sizes="{sizes}" alt="{E(alt)}" '
            f'width="{widths[1]}" height="{round(widths[1]*h/w)}" {load}>')


def card(item, people, short):
    who = " ".join(item.get("for", []))
    tags = "".join(f"<li>{E(short.get(w, people[w]))}</li>" for w in item.get("for", []))
    badge = f'<span class="g-badge">{E(item["badge"])}</span>' if item.get("badge") else ""
    note = f'<small>{E(item["price_note"])}</small>' if item.get("price_note") else ""
    return f'''<article class="g-card" id="{item["id"]}" data-who="{who}">
<div class="g-photo">{img(item["img"], item["alt"], "(max-width:640px) 100vw, (max-width:1100px) 50vw, 360px")}{badge}<span class="g-tag">{E(item["price"])}{note}</span></div>
<div class="g-info"><h3>{E(item["name"])}</h3><p>{E(item["why"])}</p>
<ul class="g-for" aria-label="Good for">{tags}</ul>
<p class="g-catch"><strong>The catch:</strong> {E(item["catch"])}</p>
<a class="g-cta" href="{E(amazon(item))}" rel="nofollow sponsored noopener" target="_blank">See today's price on Amazon</a></div></article>'''


def build(data):
    slug, url = data["slug"], f'{SITE}/finds/{data["slug"]}/'
    title, desc = data["title"], data["description"]
    pin = f'{SITE}/pins/{data["pin"]}'
    people, short = data["people"], data.get("people_short", {})
    items = {i["id"]: i for b in data["bands"] for i in b["items"]}
    n = len(items)
    days_left = max(0, (datetime.date.fromisoformat(data["deal_date"]) - datetime.date.today()).days)

    bar = '<a class="all" href="#top-picks">Top picks</a>' + "".join(
        f'<a data-band="{k+1}" href="#{b["id"]}">{E(b["label"])}</a>' for k, b in enumerate(data["bands"]))
    chips = "".join(f'<button class="g-chip" type="button" aria-pressed="false" data-who="{k}">{E(v)}</button>'
                    for k, v in people.items())
    top = "".join(
        f'<li><a href="#{t["id"]}" class="g-topcard">{img(items[t["id"]]["img"], items[t["id"]]["alt"], "(max-width:860px) 100vw, 340px", ratio="5/4")}'
        f'<span class="why">{E(t["why"])}</span><b>{E(items[t["id"]]["name"])}</b><span class="p">{E(items[t["id"]]["price"])}</span></a></li>'
        for t in data["top_picks"])
    ticker = "".join(f"<span>{E(t)}</span>" for t in data["ticker"])
    bands = ""
    for k, b in enumerate(data["bands"]):
        bands += (f'<section class="g-band" id="{b["id"]}" data-band="{k+1}">'
                  f'<header class="g-banner">{img(b["img"], b["alt"], "100vw", ratio="16/7", widths=(640, 1200, 1800))}'
                  f'<div class="g-banner-copy"><h2>{E(b["label"])}</h2><p>{E(b["blurb"])}</p><span class="count">{len(b["items"])} pick{"" if len(b["items"])==1 else "s"}</span></div></header>'
                  f'<div class="g-grid n{len(b["items"])}">{"".join(card(i, people, short) for i in b["items"])}</div></section>')
    rows = "".join(f'<tr><td><a href="#{i["id"]}">{E(i["name"])}</a></td><td class="p">{E(i["price"])}</td>'
                   f'<td>{E(short.get(i["for"][0], people[i["for"][0]]))}</td></tr>'
                   for b in data["bands"] for i in b["items"])
    pin_url = ("https://www.pinterest.com/pin/create/button/?" + urllib.parse.urlencode(
        {"url": url, "media": pin, "description": title}))
    updates = "".join(f"<li>{E(u)}</li>" for u in data["updates"])
    sources = "".join(f'<li><a href="{s["url"]}" rel="noopener">{E(s["name"])}</a></li>' for s in data["sources"])
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": title, "numberOfItems": n,
          "itemListElement": [{"@type": "ListItem", "position": p + 1, "name": i["name"], "url": url + "#" + i["id"]}
                              for p, i in enumerate(items.values())]}
    hero = data["hero"]

    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} | Digittouch Finds</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{pin}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#17151A">
<link rel="preconnect" href="https://images.unsplash.com"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,600..700,50&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/finds/guide.css?v=13">
<script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body class="finds guide"><header class="site"><div class="wrap wide"><a class="logo" href="/finds/">Digittouch <span>Finds</span></a><nav><a href="/finds/">Finds</a><a href="/">FlowFrame</a><a href="/about/">About</a></nav></div></header>
<section class="g-hero">{img(hero["img"], hero["alt"], "100vw", ratio="16/9", eager=True, widths=(800, 1600, 2400))}
<div class="g-hero-in"><div class="g-hero-copy">
<p class="g-crumb"><a href="/finds/">Finds</a> / Gift guides</p>
<h1>{data["hero_title_html"]}</h1>
<p class="lede">{E(data["lede"])}</p>
<div class="g-hero-ctas"><a class="g-btn primary" href="#{data["bands"][0]["id"]}">{E(data.get("cta_label","Shop by budget"))}</a><a class="g-btn ghost" href="#top-picks">If you only buy one</a></div>
<ul class="g-meta"><li>{n} picks</li><li>Prices checked {E(data["checked"])}</li><li>One honest catch each</li></ul>
</div>
<div class="g-burst" data-countdown="{data["deal_date"]}"><b>{days_left}</b><span>{E(data["deal_label"])}</span></div>
</div></section>
<div class="g-ticker" aria-hidden="true"><div class="track">{ticker}{ticker}</div></div>
<nav class="g-bar" aria-label="Jump to a budget"><div class="in">{bar}</div></nav>
<main class="g-body">
<p class="g-disclosure">As an Amazon Associate, Digittouch Finds earns from qualifying purchases. Buying through our links costs you nothing extra and never changes our picks. <a href="/disclosure/">How we make money</a>.</p>
<section class="g-people" aria-labelledby="people-h"><h2 id="people-h">Who are you shopping for?</h2>
<div class="g-chips">{chips}</div><p class="g-status" role="status" aria-live="polite"></p></section>
<section class="g-top" id="top-picks"><h2>If you only buy one</h2><ol>{top}</ol></section>
{bands}
<section class="g-table"><h2>All {n} at a glance</h2><table><thead><tr><th>Gift</th><th>Price</th><th>Best for</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="g-save"><img src="/pins/{data["pin"]}" alt="Pinterest pin for this guide" width="1000" height="1500" loading="lazy">
<div><h2>Save this list for later</h2><p>Pin it to a board and come back when the Black Friday prices drop on {E(data["deal_day"])}.</p>
<a class="g-pin" href="{E(pin_url)}" target="_blank" rel="noopener">Save to Pinterest</a></div></section>
<section class="g-notes"><h2>How we picked</h2><p>{E(data["method"])}</p>
<p>Photos are lifestyle images from Unsplash and may not show the exact product; tap through to Amazon to see it.</p>
<h2>Updates</h2><ul>{updates}</ul><h2>Where we checked</h2><ul>{sources}</ul>
<p>More gift ideas: {data["more_html"]}</p></section>
</main>
<footer class="site"><div class="wrap wide"><p><a href="/disclosure/">Affiliate disclosure</a><a href="/privacy/">Privacy</a><a href="/about/">About</a><a href="/contact/">Contact</a></p>
<p>&copy; 2026 Digittouch Finds, part of Digittouch Enterprise. As an Amazon Associate we earn from qualifying purchases.</p></div></footer>
<script src="/finds/guide.js?v=13" defer></script></body></html>'''


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    out = os.path.join(os.path.dirname(__file__), "..", "finds", data["slug"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(build(data))
    print("wrote", os.path.normpath(out))
