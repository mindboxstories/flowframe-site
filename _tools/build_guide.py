"""Build a Digittouch Finds gift guide page (design v6) from a JSON data file.
Usage: python3 _tools/build_guide.py _tools/guides/<slug>.json
Writes finds/<slug>/index.html using /site.css (shared design system) and finds/guide.js.

Images: "img" fields are Unsplash photo URLs (https://images.unsplash.com/photo-...),
free for commercial use under the Unsplash licence. They are lifestyle images, not the
exact products; the page says so. Swap in Amazon product images once PA-API is available."""
import json, sys, html, urllib.parse, os, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chrome import head, top, footer, mosaic, split_hero, ARROW

E = html.escape
SITE = "https://flowframe.shop"
TAG = "digittouch-20"
TAG_UK = "digittouch-21"

# Amazon bounty pages (fixed fee per sign-up, nothing to buy). Rates: Associates
# Standard Commission Income Statement. Keys are used by a guide's "extras" list.
EXTRAS = {
    "prime": {"k": "Free trial", "h": "New to Amazon Prime?",
              "p": "Start a free trial before you order. Prime members get free delivery on eligible items, so it can help with last-minute gifts.",
              "cta": "Try Prime free", "url": f"https://www.amazon.com/prime?tag={TAG}"},
    "audible": {"k": "Free trial", "h": "Audible for the commute or the coffee break",
                "p": "Audiobooks and podcasts to play while they cook, walk or focus. They can try it free first, and Audible gift memberships are on Amazon too.",
                "cta": "Try Audible free", "url": f"https://www.amazon.com/hz/audible/mlp?tag={TAG}"},
}


def amazon(item):
    if item.get("asin"):
        return f"https://www.amazon.com/dp/{item['asin']}?tag={TAG}"
    return "https://www.amazon.com/s?" + urllib.parse.urlencode({"k": item["q"], "tag": TAG})


def amazon_uk(item):
    return "https://www.amazon.co.uk/s?" + urllib.parse.urlencode({"k": item["q"], "tag": TAG_UK})


def extras(keys):
    if not keys:
        return ""
    cards = "".join(f'<div class="g-extra"><span class="k">{E(EXTRAS[k]["k"])}</span><h3>{E(EXTRAS[k]["h"])}</h3><p>{E(EXTRAS[k]["p"])}</p>'
                    f'<a href="{E(EXTRAS[k]["url"])}" rel="nofollow sponsored noopener" target="_blank">{E(EXTRAS[k]["cta"])} {ARROW}</a></div>'
                    for k in keys)
    return (f'<section class="g-extras s-wrap"><div class="sec-head"><div><h2>Free extras from Amazon</h2>'
            f'<p>Nothing to buy: these are free trials, and the terms are on Amazon.</p></div></div><div class="g-ex n{len(keys)}">{cards}</div></section>')


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
<div class="g-photo">{img(item["img"], item["alt"], "(max-width:640px) 100vw, (max-width:1000px) 50vw, 380px")}{badge}<span class="g-tag">{E(item["price"])}{note}</span></div>
<div class="g-info"><h3>{E(item["name"])}</h3><p>{E(item["why"])}</p>
<ul class="g-for" aria-label="Good for">{tags}</ul>
<p class="g-catch"><strong>The catch:</strong> {E(item["catch"])}</p>
<a class="g-cta" href="{E(amazon(item))}" rel="nofollow sponsored noopener" target="_blank">Check price on Amazon {ARROW}</a>
<a class="g-uk" href="{E(amazon_uk(item))}" rel="nofollow sponsored noopener" target="_blank">In the UK? Shop Amazon.co.uk</a></div></article>'''


PIN_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.6 19.3c-.1-.8-.2-2 0-2.9l1.2-5s-.3-.6-.3-1.5c0-1.4.8-2.4 1.8-2.4.9 0 1.3.6 1.3 1.4 0 .9-.5 2.1-.8 3.3-.2 1 .5 1.8 1.5 1.8 1.8 0 3.1-1.9 3.1-4.6 0-2.4-1.7-4.1-4.2-4.1-2.9 0-4.6 2.2-4.6 4.4 0 .9.3 1.8.8 2.3.1.1.1.2.1.3l-.3 1.2c0 .2-.2.3-.4.2-1.3-.6-2.1-2.5-2.1-4 0-3.3 2.4-6.3 6.9-6.3 3.6 0 6.4 2.6 6.4 6 0 3.6-2.3 6.5-5.4 6.5-1.1 0-2.1-.6-2.4-1.2l-.7 2.5c-.2.9-.9 2.1-1.3 2.8A10 10 0 1 0 12 2z"/></svg>'


def build(data):
    slug, url = data["slug"], f'{SITE}/finds/{data["slug"]}/'
    title, desc = data["title"], data["description"]
    pin = f'{SITE}/pins/{data["pin"]}'
    people, short = data["people"], data.get("people_short", {})
    items = {i["id"]: i for b in data["bands"] for i in b["items"]}
    n = len(items)

    bar = '<a class="all" href="#top-picks">Top picks</a>' + "".join(
        f'<a data-band="{k+1}" href="#{b["id"]}"><i></i>{E(b["label"])}</a>' for k, b in enumerate(data["bands"]))
    chips = "".join(f'<button class="g-chip" type="button" aria-pressed="false" data-who="{k}">{E(v)}</button>'
                    for k, v in people.items())
    tops = "".join(
        f'<li><a href="#{t["id"]}" class="g-topcard"><div class="im">{img(items[t["id"]]["img"], items[t["id"]]["alt"], "(max-width:860px) 120px, 380px", ratio="5/4")}</div>'
        f'<span class="why">{E(t["why"])}</span><b>{E(items[t["id"]]["name"])}</b><span class="p">{E(items[t["id"]]["price"])}</span></a></li>'
        for t in data["top_picks"])
    bands = ""
    for k, b in enumerate(data["bands"]):
        c = len(b["items"])
        bands += (f'<section class="g-band s-wrap" id="{b["id"]}" data-band="{k+1}">'
                  f'<header class="g-banner"><div class="g-banner-copy"><h2>{E(b["label"])}</h2><p>{E(b["blurb"])}</p>'
                  f'<span class="count">{c} pick{"" if c == 1 else "s"}</span></div>'
                  f'<div class="bi">{img(b["img"], b["alt"], "(max-width:860px) 100vw, 620px", ratio="16/10", widths=(640, 1000, 1400))}</div></header>'
                  f'<div class="g-grid n{c}">{"".join(card(i, people, short) for i in b["items"])}</div></section>')
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
    tp = [items[t["id"]] for t in data["top_picks"]]
    tiles = [img(hero["img"], hero["alt"], "(max-width:960px) 60vw, 360px", ratio="3/4", eager=True, widths=(480, 760, 1100)),
             img(tp[0]["img"], tp[0]["alt"], "(max-width:960px) 40vw, 280px", ratio="1/1", eager=True, widths=(320, 560, 800)),
             img(tp[1]["img"], tp[1]["alt"], "(max-width:960px) 40vw, 280px", ratio="1/1", eager=True, widths=(320, 560, 800))]
    btns = (f'<div class="s-btns"><a class="s-btn primary" href="#{data["bands"][0]["id"]}">{E(data.get("cta_label", "Shop by budget"))}</a>'
            f'<a class="s-btn ghost" href="#top-picks">See our top 3</a></div>')
    hero_html = split_hero(f'<p class="crumb"><a href="/finds/">Gift guides</a><span>/</span>Black Friday 2026</p>',
                           data["hero_title_html"], data["lede"], btns,
                           [f"{n} picks", f"Prices checked {data['checked']}", "The catch on every pick"],
                           mosaic(tiles, (str(n), "gifts, each with the honest catch")))

    return (head(f"{title} | Digittouch Finds", desc, f"/finds/{slug}/", "finds", pin)
            + f'<script type="application/ld+json">{json.dumps(ld)}</script></head><body class="v6 finds guide">'
            + top("finds", f"/finds/{slug}/") + "<main>" + hero_html
            + f'<nav class="g-bar" aria-label="Jump to a section"><div class="s-wrap in">{bar}</div></nav>'
            + f'''<section class="g-intro s-wrap"><div><h2 id="people-h">Who are you shopping for?</h2>
<div class="g-chips" role="group" aria-labelledby="people-h">{chips}</div><p class="g-status" role="status" aria-live="polite"></p></div>
<p class="g-disclosure">As an Amazon Associate, Digittouch Finds earns from qualifying purchases. Buying through our links costs you nothing extra and never changes our picks. <a href="/disclosure/">How we make money</a>.</p></section>
<section class="g-top s-wrap" id="top-picks"><div class="sec-head"><div><h2>If you only buy one</h2><p>Our three favourites from the list, for three different kinds of people.</p></div></div><ol>{tops}</ol></section>
{bands}
{extras(data.get("extras", ["prime"]))}
<section class="g-table s-wrap"><div class="sec-head"><div><h2>All {n} at a glance</h2><p>Tap a name to jump to it.</p></div></div><div class="tw"><table><thead><tr><th>Gift</th><th>Price</th><th>Best for</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<div class="s-wrap"><section class="g-save"><img src="/pins/{data["pin"]}" alt="Pinterest pin for this guide" width="1000" height="1500" loading="lazy">
<div><h2>Save this list for later</h2><p>Pin it to a board and come back when the Black Friday prices drop on {E(data["deal_day"])}.</p>
<a class="g-pin" href="{E(pin_url)}" target="_blank" rel="noopener">{PIN_SVG}Save to Pinterest</a></div></section></div>
<section class="g-notes s-wrap"><div><h2>How we picked</h2><p>{E(data["method"])}</p>
<p>Photos are lifestyle images from Unsplash and may not show the exact product; tap through to Amazon to see it.</p></div>
<div><h2>Updates</h2><ul>{updates}</ul></div><div><h2>Where we checked</h2><ul>{sources}</ul></div>
<p class="more">More gift ideas: {data["more_html"]}</p></section>
</main>''' + footer("finds") + '<script src="/finds/guide.js?v=14" defer></script></body></html>')


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    out = os.path.join(os.path.dirname(__file__), "..", "finds", data["slug"], "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(build(data))
    print("wrote", os.path.normpath(out))
