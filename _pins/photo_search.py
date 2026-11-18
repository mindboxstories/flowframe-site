"""Search Unsplash (free licence only) for each line in _pins/photo_queries.txt; writes _pins/photos.json.
Runs in GitHub Actions (the workspace cannot reach unsplash.com)."""
import json, os, urllib.request, urllib.parse
ROOT=os.path.dirname(os.path.abspath(__file__))
qs=[l.strip() for l in open(os.path.join(ROOT,'photo_queries.txt')) if l.strip() and not l.startswith('#')]
out={}
import re, html as H
for q in qs:
    url='https://unsplash.com/s/photos/'+urllib.parse.quote(q.replace(' ','-'))+'?license=free'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Accept':'text/html'})
    try: t=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','ignore')
    except Exception as e: out[q]={'error':str(e)}; continue
    res=[]; seen=set()
    for tag in re.findall(r'<img[^>]+>',t):
        m=re.search(r'images\.unsplash\.com/(photo-[0-9a-f-]+)',tag); a=re.search(r'alt="([^"]*)"',tag)
        if not m or not a or not a.group(1).strip(): continue
        pid=m.group(1)[6:]
        if pid in seen: continue
        seen.add(pid); res.append(dict(id=pid,alt=H.unescape(a.group(1))[:120]))
    out[q]=res
json.dump(out,open(os.path.join(ROOT,'photos.json'),'w'),indent=1,ensure_ascii=False)
print({q:len(v) if isinstance(v,list) else v for q,v in out.items()})
