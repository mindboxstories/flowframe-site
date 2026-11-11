"""Build a Digittouch Finds gift guide page from a JSON data file.
Usage: python3 _tools/build_guide.py _tools/guides/<slug>.json
Writes finds/<slug>/index.html using finds/guide.css and finds/guide.js."""
import json, sys, html, urllib.parse, os
sys.path.insert(0, os.path.dirname(__file__))
from art import svg

E = html.escape
SITE = "https://flowframe.shop"


def amazon(q):
    return "https://www.amazon.com/s?k=" + urllib.parse.quote_plus(q)


def card(item, people, short):
    who = " ".join(item.get("for", []))
    tags = "".join(f"<li>{E(short.get(w, people[w]))}</li>" for w in item.get("for", []))
    badge = f'<span class="g-badge">{E(item["badge"])}</span>' if item.get("badge") else ""
    note = f'<small>{E(item["price_note"])}</small>' if item.get("price_note") else ""
    return f'''<article class="g-card" id="{item["id"]}" data-who="{who}">
<div class="g-art">{badge}{svg(item["art"], item["name"])}<span class="g-tag">{E(item["price"])}{note}</span></div>
<div class="g-info"><h3>{E(item["name"])}</h3><p>{E(item["why"])}</p>
<ul class="g-for" aria-label="Good for">{tags}</ul>
<p class="g-catch"><strong>The catch:</strong> {E(item["catch"])}</p>
<a class="g-cta" href="{amazon(item["q"])}" rel="nofollow sponsored noopener" target="_blank">See today's price on Amazon</a></div></article>'''


def build(data):
    slug, url = data["slug"], f'{SITE}/finds/{data["slug"]}/'
    title, desc = data["title"], data["description"]
    pin = f'{SITE}/pins/{data["pin"]}'
    people = data["people"]
    items = {i["id"]: i for b in data["bands"] for i in b["items"]}
    n = len(items)

    stickers = "".join(f'<div class="g-sticker">{svg(items[i]["art"], items[i]["name"])}</div>'
                       for i in data["hero_stickers"])
    bar = '<a class="all" href="#top-picks">Top picks</a>' + "".join(
        f'<a data-band="{k+1}" href="#{b["id"]}">{E(b["label"])}</a>' for k, b in enumerate(data["bands"]))
    chips = "".join(f'<button class="g-chip" type="button" aria-pressed="false" data-who="{k}">{E(v)}</button>'
                    for k, v in people.items())
    top = "".join(f'<li><span class="why">{E(t["why"])}</span><b>{E(items[t["id"]]["name"])}</b>'
                  f'<a href="#{t["id"]}">{E(items[t["id"]]["price"])}, see the details</a></li>'
                  for t in data["top_picks"])
    import datetime
    days_left = max(0, (datetime.date.fromisoformat(data["deal_date"]) - datetime.date.today()).days)
    ticker = "".join(f"<span>{E(t)}</span>" for t in data["ticker"])
    bands = ""
    for k, b in enumerate(data["bands"]):
        col = "".join(f'<div class="g-sticker">{svg(i["art"], i["name"])}</div>' for i in b["items"][:3])
        bands += (f'<section class="g-band" id="{b["id"]}" data-band="{k+1}"><header class="g-band-poster"><div>'
                  f'<h2 class="stamp">{E(b["label"])}</h2><p>{E(b["blurb"])}</p><span class="count">{len(b["items"])} picks</span></div>'
                  f'<div class="g-collage" aria-hidden="true">{col}</div></header>'
                  f'<div class="g-grid">{"".join(card(i, people, data.get("people_short", {})) for i in b["items"])}</div></section>')
    rows = "".join(f'<tr><td><a href="#{i["id"]}">{E(i["name"])}</a></td><td class="p">{E(i["price"])}</td>'
                   f'<td>{E(", ".join(people[w] for w in i.get("for", [])[:1]))}</td></tr>'
                   for b in data["bands"] for i in b["items"])
    pin_url = ("https://www.pinterest.com/pin/create/button/?" + urllib.parse.urlencode(
        {"url": url, "media": pin, "description": title}))
    updates = "".join(f"<li>{E(u)}</li>" for u in data["updates"])
    sources = "".join(f'<li><a href="{s["url"]}" rel="noopener">{E(s["name"])}</a></li>' for s in data["sources"])

    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} | Digittouch Finds</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="article"><meta property="og:url" content="{url}"><meta property="og:image" content="{pin}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#1D1B20">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:opsz,wght@9..40,400;9..40,600;9..40,700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/finds/guide.css">
<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"ItemList","name":title,"numberOfItems":n,"itemListElement":[{"@type":"ListItem","position":p+1,"name":i["name"],"url":url+"#"+i["id"]} for p,i in enumerate(items.values())]})}</script>
</head>
<body class="finds guide"><header class="site"><div class="wrap wide"><a class="logo" href="/finds/">Digittouch <span>Finds</span></a><nav><a href="/finds/">Finds</a><a href="/">FlowFrame</a><a href="/about/">About</a></nav></div></header>
<section class="g-hero g-poster"><div class="stage">
<div class="g-shelf-free" aria-hidden="true">{stickers}</div>
<div class="g-tagcard"><p class="g-crumb"><a href="/finds/">Finds</a> / Gift guides</p>
<h1>{data["hero_title_html"]}</h1>
<p class="lede">{E(data["lede"])}</p>
<ul class="g-meta"><li>{n} picks</li><li>Prices checked {E(data["checked"])}</li><li>One honest catch each</li></ul></div>
<div class="g-burst" data-countdown="{data["deal_date"]}"><b>{days_left}</b><span>{E(data["deal_label"])}</span></div>
</div></section>
<div class="g-ticker" aria-hidden="true"><div class="track">{ticker}{ticker}</div></div>
<nav class="g-bar" aria-label="Jump to a budget"><div class="in">{bar}</div></nav>
<main class="g-body">
<p class="g-disclosure">Digittouch Finds may earn a commission if you buy through links on this page, at no extra cost to you. It never changes our picks. <a href="/disclosure/">How we make money</a>.</p>
<section class="g-people" aria-labelledby="people-h"><h2 id="people-h">Who are you shopping for?</h2>
<div class="g-chips">{chips}</div><p class="g-status" role="status" aria-live="polite"></p></section>
<section class="g-top" id="top-picks"><h2>If you only buy one</h2><ol>{top}</ol></section>
{bands}
<section class="g-table"><h2>All {n} at a glance</h2><table><thead><tr><th>Gift</th><th>Price</th><th>Best for</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="g-save"><img src="/pins/{data["pin"]}" alt="Pinterest pin for this guide" width="1000" height="1500" loading="lazy">
<div><h2>Save this list for later</h2><p>Pin it to a board and come back when the Black Friday prices drop on {E(data["deal_day"])}.</p>
<a class="g-pin" href="{pin_url}" target="_blank" rel="noopener">Save to Pinterest</a></div></section>
<section class="g-notes"><h2>How we picked</h2><p>{E(data["method"])}</p>
<h2>Updates</h2><ul>{updates}</ul><h2>Where we checked</h2><ul>{sources}</ul>
<p>More gift ideas: {data["more_html"]}</p></section>
</main>
<footer class="site"><div class="wrap wide"><p><a href="/disclosure/">Affiliate disclosure</a><a href="/privacy/">Privacy</a><a href="/about/">About</a><a href="/contact/">Contact</a></p>
<p>&copy; 2026 Digittouch Finds, part of Digittouch Enterprise. As an affiliate we may earn from qualifying purchases.</p></div></footer>
<script src="/finds/guide.js" defer></script></body></html>'''


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    out = os.path.join(os.path.dirname(__file__), "..", "finds", data["slug"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(build(data))
    print("wrote", os.path.normpath(out))
