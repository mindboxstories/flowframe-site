"""Search Unsplash (free licence only) for each line in _pins/photo_queries.txt; writes _pins/photos.json.
Runs in GitHub Actions (the workspace cannot reach unsplash.com)."""
import json, os, urllib.request, urllib.parse
ROOT=os.path.dirname(os.path.abspath(__file__))
qs=[l.strip() for l in open(os.path.join(ROOT,'photo_queries.txt')) if l.strip() and not l.startswith('#')]
out={}
for q in qs:
    url='https://unsplash.com/napi/search/photos?'+urllib.parse.urlencode({'query':q,'per_page':30})
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    try: data=json.load(urllib.request.urlopen(req,timeout=30))
    except Exception as e: out[q]={'error':str(e)}; continue
    res=[]
    for r in data.get('results',[]):
        if r.get('premium') or r.get('plus'): continue
        raw=r['urls']['raw']; pid=raw.split('/photo-')[1].split('?')[0] if '/photo-' in raw else None
        if not pid: continue
        res.append(dict(id=pid,alt=(r.get('alt_description') or r.get('description') or '')[:120],w=r['width'],h=r['height'],likes=r.get('likes',0),user=r['user']['name']))
    out[q]=res
json.dump(out,open(os.path.join(ROOT,'photos.json'),'w'),indent=1,ensure_ascii=False)
print({q:len(v) if isinstance(v,list) else v for q,v in out.items()})
