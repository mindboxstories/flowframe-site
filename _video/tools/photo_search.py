"""Search Unsplash (free licence only) for each query in a JSON list and write a contact sheet.
Usage: python _video/tools/photo_search.py queries.json out_dir"""
import json, sys, os, io, urllib.request, urllib.parse
from PIL import Image, ImageDraw
qs = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept": "application/json"}
res = {}
for key, q in qs.items():
    u = "https://unsplash.com/napi/search/photos?" + urllib.parse.urlencode({"query": q, "per_page": 12, "plus": "none", "orientation": "landscape"})
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))
    except Exception as e:
        print("fail", key, e); continue
    items = [r for r in d.get("results", []) if not r.get("premium") and not r.get("plus")][:8]
    res[key] = [{"id": r["urls"]["raw"].split("/photo-")[-1].split("?")[0], "raw": r["urls"]["raw"].split("?")[0], "alt": r.get("alt_description"), "w": r["width"], "h": r["height"]} for r in items]
    thumbs = []
    for r in items:
        try:
            im = Image.open(io.BytesIO(urllib.request.urlopen(r["urls"]["small"], timeout=30).read())).convert("RGB")
            im.thumbnail((400, 300)); c = Image.new("RGB", (400, 330), "white"); c.paste(im, (0, 0))
            ImageDraw.Draw(c).text((4, 306), str(len(thumbs)), fill="black"); thumbs.append(c)
        except Exception: pass
    if thumbs:
        sheet = Image.new("RGB", (1600, 330 * ((len(thumbs) + 3) // 4)), "white")
        for i, t in enumerate(thumbs): sheet.paste(t, ((i % 4) * 400, (i // 4) * 330))
        sheet.save(f"{out}/{key}.jpg", quality=80)
    print(key, len(items))
json.dump(res, open(f"{out}/results.json", "w"), indent=1)
