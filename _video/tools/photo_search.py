"""Search Unsplash (free licence) per query with a real browser; write contact sheets + results.json.
Usage: python _video/tools/photo_search.py queries.json out_dir"""
import json, sys, os, io, re, urllib.request, urllib.parse
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
qs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
res = {}
JS = r"""() => { const seen = new Set(), o = [];
  for (const a of document.querySelectorAll('a[href*="/photos/"]')) {
    const img = a.querySelector('img[src*="images.unsplash.com/photo-"]'); if (!img) continue;
    const m = img.src.match(/photo-[0-9a-z-]+/); if (!m || seen.has(m[0])) continue;
    if (a.closest('figure') && a.closest('figure').innerText.match(/Unsplash\+|Plus/)) continue;
    seen.add(m[0]); o.push({id: m[0].slice(6), alt: img.alt}); }
  return o; }"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1400, "height": 2400})
    for key, q in qs.items():
        try:
            pg.goto("https://unsplash.com/s/photos/" + urllib.parse.quote(q.replace(" ", "-")) + "?license=free&orientation=landscape", wait_until="domcontentloaded", timeout=60000)
            pg.wait_for_timeout(3500)
            items = pg.evaluate(JS)[:12]
            if not items: print('DEBUG', pg.title(), pg.evaluate("[...document.images].slice(0,8).map(i=>i.src.slice(0,90)).join(' | ')"))
        except Exception as e:
            print("fail", key, e); continue
        res[key] = items; thumbs = []
        for i, r in enumerate(items):
            try:
                im = Image.open(io.BytesIO(urllib.request.urlopen(f"https://images.unsplash.com/photo-{r['id']}?w=400&q=70", timeout=30).read())).convert("RGB")
                im.thumbnail((400, 300)); c = Image.new("RGB", (400, 330), "white"); c.paste(im, (0, 0))
                ImageDraw.Draw(c).text((4, 306), f"{i} {r['id']}", fill="black"); thumbs.append((i, c))
            except Exception as e: print("thumb", e)
        if thumbs:
            sheet = Image.new("RGB", (1600, 330 * ((len(thumbs) + 3) // 4)), "white")
            for k, (i, t) in enumerate(thumbs): sheet.paste(t, ((k % 4) * 400, (k // 4) * 330))
            sheet.save(f"{out}/{key}.jpg", quality=80)
        print(key, len(items))
    b.close()
json.dump(res, open(f"{out}/results.json", "w"), indent=1)
