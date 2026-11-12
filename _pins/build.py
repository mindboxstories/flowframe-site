"""Pin generator: specs.json -> _pins/html/<id>.html (rendered to pins/v7/<id>.jpg by render.py)."""
import json, os, html
ROOT=os.path.dirname(os.path.abspath(__file__))
U=lambda i,w=1000,h=1000: f"https://images.unsplash.com/photo-{i}?w={w}&h={h}&fit=crop&crop=entropy&q=82&auto=format"
FONTS='<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500;1,9..144,600&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=block" rel="stylesheet">'
THEMES={
 "finds":dict(ink="#1D1B22",accent="#E4572E",sun="#FFC93C",cream="#FFF5EF",deep="#22172B",brand1="Digittouch",brand2="Finds",url="flowframe.shop/finds"),
 "ff":dict(ink="#14213D",accent="#0F8B8D",sun="#F2A541",cream="#F3F6F8",deep="#0E1830",brand1="Flow",brand2="Frame",url="flowframe.shop/guides"),
}
CSS="""*{margin:0;box-sizing:border-box}html,body{width:1000px;height:1500px;overflow:hidden}
body{font-family:'Plus Jakarta Sans',sans-serif;color:var(--ink);background:var(--cream);position:relative}
.ph{background-size:cover;background-position:center;position:absolute}
.h{font-family:'Fraunces',serif;font-weight:600;letter-spacing:-.02em;line-height:1.02}
.h em{font-style:italic;font-weight:500;color:var(--hi)}
.chip{display:inline-flex;align-items:center;gap:12px;font-weight:800;font-size:26px;letter-spacing:.14em;text-transform:uppercase;padding:14px 26px;border-radius:999px}
.brand{font-family:'Fraunces',serif;font-weight:600;font-size:34px}
.brand b{color:var(--accent);font-weight:600}
.url{font-weight:700;font-size:26px;letter-spacing:.02em}
.price{position:absolute;width:250px;height:250px;border-radius:50%;background:var(--sun);color:var(--ink);display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;transform:rotate(-8deg);box-shadow:0 18px 40px rgba(0,0,0,.25)}
.price small{font-weight:800;font-size:24px;letter-spacing:.12em;text-transform:uppercase}
.price span{font-family:'Fraunces',serif;font-weight:700;font-size:92px;line-height:.95}
.tags{display:flex;flex-wrap:wrap;gap:12px}
.tags span{background:#fff;border:2px solid rgba(0,0,0,.08);border-radius:999px;padding:10px 20px;font-weight:700;font-size:25px}
"""
def page(t,body,extra=""):
    v=THEMES[t["theme"]]
    root=";".join(f"--{k}:{v[k]}" for k in ("ink","accent","sun","cream","deep"))
    return f"<!doctype html><html><head><meta charset=utf-8>{FONTS}<style>:root{{{root};--hi:{v['sun']}}}{CSS}{extra}</style></head><body>{body}</body></html>"
def brand(t,color):
    v=THEMES[t["theme"]]
    return f'<div class="brand" style="color:{color}">{v["brand1"]}<b>{v["brand2"]}</b></div>'
def head(s): return s  # headline already contains <em>
# ---- Layout A: full-bleed photo, dark gradient, headline bottom
def A(t):
    v=THEMES[t["theme"]]
    body=f'''<div class="ph" style="inset:0;background-image:url('{U(t['img'],1000,1500)}')"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,0) 30%,rgba(20,14,26,.55) 52%,{v['deep']} 80%)"></div>
<div style="position:absolute;left:70px;top:70px"><span class="chip" style="background:var(--sun);color:var(--ink)">{t['chip']}</span></div>
<div style="position:absolute;left:70px;right:70px;bottom:120px;color:#fff">
<div class="h" style="font-size:{t.get('size',112)}px">{t['head']}</div>
<p style="font-size:36px;font-weight:600;margin-top:28px;opacity:.92;line-height:1.3">{t['sub']}</p></div>
<div style="position:absolute;left:70px;right:70px;bottom:48px;display:flex;justify-content:space-between;align-items:center;color:#fff">{brand(t,'#fff')}<span class="url" style="opacity:.85">{v['url']}</span></div>'''
    return page(t,body)
# ---- Layout B: photo top, cream panel, price sticker, tags
def B(t):
    v=THEMES[t["theme"]]
    body=f'''<div class="ph" style="left:0;right:0;top:0;height:860px;border-radius:0 0 56px 56px;background-image:url('{U(t['img'],1000,860)}')"></div>
<div class="price" style="right:60px;top:700px"><small>{t['plabel']}</small><span>{t['price']}</span></div>
<div style="position:absolute;left:70px;right:70px;top:930px">
<span class="chip" style="background:var(--ink);color:#fff;font-size:22px;padding:11px 22px">{t['chip']}</span>
<div class="h" style="font-size:{t.get('size',96)}px;margin-top:26px;--hi:var(--accent)">{t['head']}</div>
{('<div class="tags" style="margin-top:30px">'+''.join(f'<span>{x}</span>' for x in t['tags'])+'</div>') if t.get('tags') else f'<p style="font-size:34px;font-weight:600;margin-top:24px;line-height:1.32;opacity:.8">{t.get("sub","")}</p>'}</div>
<div style="position:absolute;left:70px;right:70px;bottom:44px;display:flex;justify-content:space-between;align-items:center">{brand(t,v['ink'])}<span class="url">{v['url']}</span></div>'''
    return page(t,body)
# ---- Layout C: 3-photo collage + headline band
def C(t):
    v=THEMES[t["theme"]]
    a,b,c=t['imgs']
    body=f'''<div style="position:absolute;left:40px;right:40px;top:40px;height:900px;display:grid;grid-template-columns:1.25fr 1fr;grid-template-rows:1fr 1fr;gap:18px">
<div class="ph" style="position:relative;grid-row:1/3;border-radius:36px;background-image:url('{U(a,560,900)}')"></div>
<div class="ph" style="position:relative;border-radius:36px;background-image:url('{U(b,440,440)}')"></div>
<div class="ph" style="position:relative;border-radius:36px;background-image:url('{U(c,440,440)}')"></div></div>
<div style="position:absolute;left:40px;right:40px;top:880px;bottom:130px;background:{v['deep']};border-radius:40px;color:#fff;padding:56px 56px 0">
<span class="chip" style="background:var(--sun);color:var(--ink);font-size:22px;padding:11px 22px">{t['chip']}</span>
<div class="h" style="font-size:{t.get('size',92)}px;margin-top:24px">{t['head']}</div>
<p style="font-size:32px;font-weight:600;margin-top:20px;opacity:.85">{t['sub']}</p></div>
<div style="position:absolute;left:70px;right:70px;bottom:44px;display:flex;justify-content:space-between;align-items:center">{brand(t,v['ink'])}<span class="url">{v['url']}</span></div>'''
    return page(t,body)
# ---- Layout D: gift-tag / photo card on coloured ground
def D(t):
    v=THEMES[t["theme"]]
    bg=t.get('bg','var(--accent)')
    body=f'''<div style="position:absolute;inset:0;background:{bg}"></div>
<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.14) 2px,transparent 2px);background-size:34px 34px"></div>
<div style="position:absolute;left:70px;right:70px;top:80px;color:#fff;text-align:center">
<div class="h" style="font-size:{t.get('size',100)}px">{t['head']}</div></div>
<div style="position:absolute;left:130px;right:130px;top:{t.get('cardtop',520)}px;height:720px;background:#fff;border-radius:28px;padding:22px;transform:rotate(-3deg);box-shadow:0 30px 60px rgba(0,0,0,.3)">
<div class="ph" style="position:relative;width:100%;height:100%;border-radius:18px;background-image:url('{U(t['img'],740,700)}')"></div>
<div style="position:absolute;top:-26px;left:50%;width:180px;height:52px;margin-left:-90px;background:rgba(255,201,60,.85);transform:rotate(4deg)"></div></div>
<div class="price" style="right:70px;bottom:150px;width:230px;height:230px"><small>{t['plabel']}</small><span style="font-size:84px">{t['price']}</span></div>
<div style="position:absolute;left:70px;bottom:52px;right:70px;display:flex;justify-content:space-between;align-items:center;color:#fff">{brand(t,'#fff').replace('<b>','<b style="color:var(--sun)">')}<span class="url">{v['url']}</span></div>'''
    return page(t,body)
# ---- Layout E: giant number over photo
def E(t):
    v=THEMES[t["theme"]]
    body=f'''<div class="ph" style="inset:0;background-image:url('{U(t['img'],1000,1500)}')"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,8,14,.78) 0%,rgba(10,8,14,.25) 42%,rgba(10,8,14,.2) 60%,rgba(10,8,14,.85) 100%)"></div>
<div style="position:absolute;left:70px;right:70px;top:70px;color:#fff">
<div style="font-family:'Fraunces',serif;font-weight:700;font-size:300px;line-height:.82;color:var(--sun)">{t['num']}</div>
<div class="h" style="font-size:{t.get('size',90)}px;margin-top:10px">{t['head']}</div></div>
<div style="position:absolute;left:70px;right:70px;bottom:120px;color:#fff"><span class="chip" style="background:#fff;color:var(--ink);font-size:24px">{t['chip']}</span>
<p style="font-size:34px;font-weight:600;margin-top:22px;line-height:1.3">{t['sub']}</p></div>
<div style="position:absolute;left:70px;right:70px;bottom:44px;display:flex;justify-content:space-between;align-items:center;color:#fff">{brand(t,'#fff')}<span class="url">{v['url']}</span></div>'''
    return page(t,body)
L=dict(A=A,B=B,C=C,D=D,E=E)
if __name__=="__main__":
    specs=json.load(open(os.path.join(ROOT,"specs.json")))
    os.makedirs(os.path.join(ROOT,"html"),exist_ok=True)
    for s in specs:
        open(os.path.join(ROOT,"html",s["id"]+".html"),"w").write(L[s["layout"]](s))
    print(len(specs),"pins")
