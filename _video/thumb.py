"""YouTube thumbnails (1280x720) for a guide video, two designs to compare.
Usage: python _video/thumb.py _video/<slug>/script.json  -> _video/out/<slug>/thumb-a.jpg, thumb-b.jpg
Photos are the guide's Unsplash images (free commercial licence); fonts match the site."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_tools"))
from chrome import MARK_DF
from playwright.sync_api import sync_playwright

spec = json.load(open(sys.argv[1]))
t = spec["thumb"]
OUT = os.path.join(os.path.dirname(__file__), "out", spec["slug"])
os.makedirs(OUT, exist_ok=True)
U = lambda u, w, h: f"{u}?auto=format&fit=crop&q=80&w={w}&h={h}"
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,700;0,9..144,800;1,9..144,700'
         '&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">')
BASE = """*{box-sizing:border-box;margin:0}body{width:1280px;height:720px;overflow:hidden;font-family:'Plus Jakarta Sans',sans-serif}
.brand{position:absolute;display:flex;align-items:center;gap:10px;font:700 22px/1 'Fraunces',serif;letter-spacing:-.01em}
.brand svg{width:34px;height:34px}
.brand em{font-style:normal;color:#E4572E}"""

ph = t["photos"]

# A: dark plum panel left with the promise, three tilted photo cards right
A = f"""<!doctype html><html><head>{FONTS}<style>{BASE}
body{{background:#22172B;position:relative}}
.glow{{position:absolute;right:-120px;top:-160px;width:820px;height:820px;border-radius:50%;background:radial-gradient(closest-side,rgba(228,87,46,.55),transparent)}}
.copy{{position:absolute;left:64px;top:92px;width:600px;color:#fff}}
.k{{display:inline-block;background:#FFC93C;color:#1D1B22;font-weight:800;font-size:24px;letter-spacing:.06em;padding:10px 18px;border-radius:12px;text-transform:uppercase}}
h1{{font:800 104px/0.94 'Fraunces',serif;letter-spacing:-.035em;margin:26px 0 0}}
h1 em{{font-style:italic;font-weight:700;color:#FF8A65}}
.sub{{margin-top:26px;font-size:30px;font-weight:700;color:rgba(255,255,255,.82)}}
.card{{position:absolute;border-radius:26px;overflow:hidden;border:8px solid #fff;box-shadow:0 30px 60px -20px rgba(0,0,0,.7)}}
.card img{{display:block;width:100%;height:100%;object-fit:cover}}
.c1{{width:330px;height:410px;right:250px;top:70px;transform:rotate(-6deg)}}
.c2{{width:300px;height:370px;right:40px;top:150px;transform:rotate(5deg)}}
.c3{{width:250px;height:250px;right:300px;top:420px;transform:rotate(3deg)}}
.price{{position:absolute;right:52px;top:46px;width:170px;height:170px;border-radius:50%;background:#E4572E;color:#fff;display:grid;place-content:center;text-align:center;transform:rotate(10deg);box-shadow:0 18px 36px -12px rgba(0,0,0,.6);z-index:3}}
.price small{{font-size:22px;font-weight:800;letter-spacing:.04em}}.price b{{font:800 64px/0.9 'Fraunces',serif}}
.brand{{left:64px;bottom:44px;color:#fff}}
</style></head><body><div class="glow"></div>
<div class="copy"><span class="k">{t['kicker']}</span><h1>{t['headline_html']}</h1><p class="sub">{t['sub']}</p></div>
<div class="card c1"><img src="{U(ph[0],660,820)}"></div><div class="card c2"><img src="{U(ph[1],600,740)}"></div>
<div class="card c3"><img src="{U(ph[2],500,500)}"></div>
<div class="price"><small>UNDER</small><b>{t['price']}</b></div>
<div class="brand">{MARK_DF}<span>Digittouch <em>Finds</em></span></div></body></html>"""

# B: full photo grid, cream band with a giant number
B = f"""<!doctype html><html><head>{FONTS}<style>{BASE}
body{{background:#FFF5EF;position:relative}}
.grid{{position:absolute;right:0;top:0;width:700px;height:720px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:8px;background:#FFF5EF}}
.grid img{{width:100%;height:100%;object-fit:cover;display:block}}
.copy{{position:absolute;left:58px;top:70px;width:560px;color:#1D1B22}}
.n{{font:800 250px/0.8 'Fraunces',serif;letter-spacing:-.06em;color:#E4572E}}
h1{{font:800 78px/0.98 'Fraunces',serif;letter-spacing:-.03em;margin:14px 0 0}}
h1 em{{font-style:italic;font-weight:700;color:#E4572E}}
.tag{{display:inline-block;margin-top:26px;background:#1D1B22;color:#FFC93C;font-weight:800;font-size:30px;padding:12px 22px;border-radius:14px}}
.brand{{left:58px;bottom:40px;color:#1D1B22}}
</style></head><body>
<div class="grid">{''.join(f'<img src="{U(u,350,360)}">' for u in ph[:4])}</div>
<div class="copy"><div class="n">{t['number']}</div><h1>{t['headline_b_html']}</h1><span class="tag">{t['tag_b']}</span></div>
<div class="brand">{MARK_DF}<span>Digittouch <em>Finds</em></span></div></body></html>"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    for name, html in (("a", A), ("b", B)):
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_function("[...document.images].every(i => i.complete && i.naturalWidth > 0)", timeout=30000)
        pg.screenshot(path=f"{OUT}/thumb-{name}.jpg", type="jpeg", quality=90)
    b.close()
print("thumbs done")
