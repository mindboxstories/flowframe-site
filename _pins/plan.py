"""Builds _pins/specs.json (designs) and _pins/schedule.json (posting plan) from the guide JSONs.
Every pin carries test tags (layout, angle) so the Strategy Study can learn which designs win."""
import json, glob, os, datetime as dt
ROOT=os.path.dirname(os.path.abspath(__file__)); REPO=os.path.dirname(ROOT)
G={json.load(open(f))['slug']:json.load(open(f)) for f in glob.glob(os.path.join(REPO,'_tools/guides/*.json'))}
BOARD={'gifts-under-25':'250372129223694909','gifts-for-her-under-60':'250372129223699805','hair-styler-gifts':'250372129223699805',
 'kitchen-gifts-home-cook':'250372129223710899','work-from-home-gifts':'250372129223710900','pet-lover-gifts-under-55':'250372129223710901'}
TAGS={'gifts-under-25':'#giftideas #giftsunder25 #secretsanta','gifts-for-her-under-60':'#giftsforher #giftideas #christmasgifts',
 'hair-styler-gifts':'#hairtools #giftsforher #beautygifts','kitchen-gifts-home-cook':'#kitchengifts #giftsforcooks #giftideas',
 'work-from-home-gifts':'#wfhgifts #desksetup #giftideas','pet-lover-gifts-under-55':'#doggifts #catgifts #petlovers'}
SHORT={'gifts-under-25':'u25','gifts-for-her-under-60':'her','hair-styler-gifts':'hair','kitchen-gifts-home-cook':'kit','work-from-home-gifts':'wfh','pet-lover-gifts-under-55':'pets'}
# product hooks: (headline with <em>, angle)
H={
'gifts-for-her-under-60':{'slippers':('Cold toes? <em>Not this winter.</em>','comfort'),'lamp':('The cosy glow, <em>minus the flame</em>','comfort'),
 'candle':('Her whole home will smell like <em>a winter forest</em>','sensory'),'mask':('For the woman who <em>never gets a lie-in</em>','care'),
 'owala':('The tumbler she’ll <em>carry everywhere</em>','daily-use'),'summer':('Her carry-on, <em>upgraded</em>','travel'),
 'saltstone':('Little luxury. <em>Every single shower.</em>','care'),'cuff':('The gold cuff <em>everyone’s pinning</em>','trend'),
 'lego':('Plants she <em>can’t</em> kill','fun'),'bala':('Workout gear that <em>looks like jewellery</em>','style'),'tilbury':('A beauty treat she <em>won’t buy herself</em>','care')},
'gifts-under-25':{'airtag':('For the one who <em>always</em> loses their keys','relatable'),'earbuds':('Their commute just got <em>quieter</em>','daily-use'),
 'speaker':('Shower concerts, <em>sorted</em>','fun'),'warmers':('For the one who’s <em>always</em> cold','relatable'),'blanket':('The hug they can <em>wear</em>','comfort'),
 'candle':('The easy win for <em>Secret Santa</em>','occasion'),'popcorn':('Movie night, <em>upgraded</em>','fun'),'board':('The kitchen upgrade they’ll <em>use daily</em>','daily-use'),
 'press':('Café coffee, <em>no machine</em>','daily-use'),'laneige':('The cult lip mask, <em>gift-sized</em>','trend'),'bagsmart':('For the friend who <em>overpacks</em>','relatable')},
'hair-styler-gifts':{'hottools':('Salon blowout. <em>$29.</em>','value'),'tymo':('Sleek hair <em>in minutes</em>','daily-use'),'revlon':('The blowout brush <em>everyone asks for</em>','trend'),
 'knotdr':('Goodbye, <em>morning tangles</em>','relatable'),'laifen':('The fast dryer <em>without the big price</em>','value'),'t3duo':('Volume or sleek? <em>Both.</em>','style'),
 'flexfusion':('The Airwrap rival, <em>now $299</em>','deal'),'airwrap':('The one on <em>every</em> wish list','aspiration')},
'kitchen-gifts-home-cook':{'skillet':('The pan they’ll <em>pass down</em>','sentimental'),'microplane':('The tool chefs <em>can’t live without</em>','daily-use'),
 'thermopop':('No more <em>guessing</em> if it’s done','relatable'),'spinner':('Crisp salad, <em>one hand</em>','daily-use'),'instantpot':('Weeknight dinners, <em>handled</em>','relief'),
 'dutchoven':('Sunday stew, <em>every Sunday</em>','sentimental'),'allclad':('Pro pans, <em>home-cook price</em>','value'),'crispi':('Air fryer meets <em>serving dish</em>','novelty')},
'pet-lover-gifts-under-55':{'kong':('The toy every dog <em>goes wild for</em>','joy'),'snuffle':('Dinner becomes a <em>treasure hunt</em>','joy'),'slowbowl':('For the dog who <em>inhales</em> dinner','relatable'),
 'harness':('Calmer walks, <em>happier humans</em>','relief'),'fountain':('For the cat who <em>only drinks from the tap</em>','relatable'),'hotpursuit':('Hours of <em>pounce</em>','joy'),
 'tracks':('Solo playtime for <em>$9</em>','value'),'chomchom':('Goodbye, <em>pet hair on the sofa</em>','relief'),'furminator':('Less fur <em>everywhere</em>','relief')},
'work-from-home-gifts':{'mat':('The desk upgrade they’ll <em>feel every day</em>','daily-use'),'stand':('Screen at eye level, <em>finally</em>','relief'),'cable':('Goodbye, <em>cable chaos</em>','relief'),
 'charger':('One spot. <em>Everything charged.</em>','daily-use'),'mxmaster':('The mouse power users <em>swear by</em>','aspiration'),'mxkeys':('Quiet keys. <em>Calm mornings.</em>','daily-use'),
 'screenbar':('Late-night work, <em>easier on the eyes</em>','relief'),'ember':('Coffee that <em>stays hot</em> through every call','relatable'),'kindle':('For the one who reads <em>every night</em>','sentimental'),
 'mv7':('Sound like a <em>pro</em> on every call','aspiration')},
}
# guide-level pins: (layout, extra)
GP={
'gifts-under-25':[dict(layout='A',img='1601804590276-e19ce20343da',chip='Gift guide · Under $25',head='Small gifts.<br><em>Big “you get me”</em> energy.',sub='12 under-$25 gifts they’ll actually use, with the honest catch on each.',angle='emotional'),
 dict(layout='E',img='1513201099705-a9746e1e201f',num='12',head='gifts under $25 that <em>don’t feel cheap</em>',chip='Secret Santa, sorted',sub='Tech, cosy, kitchen and beauty picks.',angle='number'),
 dict(layout='C',imgs=['1612373914372-79a8a0311f78','1603508102977-02688e3265fd','1613536844480-ac5d7b1b6ed1'],chip='All under $25',head='Secret Santa, <em>sorted.</em>',sub='12 gifts, one honest catch each',angle='occasion'),
 dict(layout='D',img='1607900177462-ac553f1f5d97',plabel='All under',price='$25',head='Gifts they’ll <em style="color:var(--sun)">actually use</em>',angle='practical')],
'gifts-for-her-under-60':[dict(layout='B',img='1513885535751-8b9238bd345a',plabel='All under',price='$60',chip='Gifts for her',head='For the woman who <em>has everything</em>',tags=['Silk eye mask','Owala tumbler','Gold cuff','LEGO plants'],angle='emotional'),
 dict(layout='A',img='1602521163308-23e552671e38',chip='Gifts for her · Under $60',head='Gifts she’ll <em>keep</em>, not regift',sub='11 thoughtful picks from $16, sorted by budget.',angle='emotional'),
 dict(layout='C',imgs=['1687435703153-88f6bc0cdcff','1611591437281-460bfbe1220a','1668112037360-900ff60ef6f7'],chip='Under $60',head='Little luxuries she <em>won’t buy herself</em>',sub='11 gifts for her, honest catch on each',angle='care'),
 dict(layout='E',img='1650307535558-fa2b39ed16eb',num='11',head='gifts for her <em>under $60</em>',chip='From $16',sub='Cosy, beauty, jewellery and more.',angle='number')],
'hair-styler-gifts':[dict(layout='E',img='1712481846916-8f73ffc2067a',num='8',head='hair tool gifts on <em>every wish list</em>',chip='From $29 to a splurge',sub='Salon-style hair at home, sorted by budget.',angle='number'),
 dict(layout='A',img='1734111719430-fe4a3973f8af',chip='Gifts for her · Hair tools',head='Good hair days, <em>gift-wrapped</em>',sub='8 hair tools from $29, each with the honest catch.',angle='emotional'),
 dict(layout='D',img='1785456283212-338f5bc44d50',plabel='From',price='$29',head='For the friend who <em style="color:var(--sun)">always</em> has great hair',angle='relatable'),
 dict(layout='B',img='1769029270594-26ce033ca6fc',plabel='From',price='$29',chip='Hair tool gifts',head='Salon hair <em>at home</em>',tags=['Revlon','Laifen','T3','Shark FlexFusion'],angle='aspiration')],
'kitchen-gifts-home-cook':[dict(layout='D',img='1518291344630-4857135fb581',plabel='From',price='$16',head='For the one who<br><em style="color:var(--sun)">cooks for everyone</em>',angle='emotional'),
 dict(layout='A',img='1603185730021-ddc0c8097059',chip='Gift guide · Kitchen',head='Make their <em>Sunday dinner</em> better',sub='8 kitchen gifts from $16 to a splurge.',angle='sentimental'),
 dict(layout='C',imgs=['1598103442097-8b74394b95c6','1622001545761-9bd12a4b465b','1590794056226-79ef3a8147e1'],chip='From $16',head='Kitchen tools they’ll <em>reach for daily</em>',sub='8 gifts for the home cook',angle='practical'),
 dict(layout='E',img='1586208958839-06c17cacdf08',num='8',head='gifts for the <em>home cook</em>',chip='Black Friday 2026',sub='From a $16 zester to the Ninja Crispi Pro.',angle='number')],
'pet-lover-gifts-under-55':[dict(layout='C',imgs=['1675543999462-3b3157b044c2','1571131116858-2295ade82a72','1591946614720-90a587da4a36'],chip='Under $55',head='Their pet is family. <em>Gift like it.</em>',sub='9 gifts for dog and cat people',angle='emotional'),
 dict(layout='A',img='1672355422293-a912bc3a1d90',chip='Gift guide · Cat lovers',head='Gifts for cat people <em>(the cat gets one too)</em>',sub='Toys, a water fountain and a fur roller, all under $55.',angle='humour'),
 dict(layout='D',img='1774440865482-81a8c9b92e76',plabel='All under',price='$55',head='For the friend whose dog is <em style="color:var(--sun)">their whole world</em>',angle='emotional'),
 dict(layout='E',img='1591946614720-90a587da4a36',num='9',head='gifts for <em>pet lovers</em> under $55',chip='Dogs, cats and the home',sub='Each with the honest catch.',angle='number')],
'work-from-home-gifts':[dict(layout='A',img='1518976024611-28bf4b48222e',chip='Gift guide · Home office',head='Make their Monday desk <em>feel like a treat</em>',sub='10 work-from-home gifts, from a $20 desk mat to a splurge.',angle='emotional'),
 dict(layout='B',img='1511467687858-23d96c32e4ae',plabel='From',price='$20',chip='Work-from-home gifts',head='For the one who works from the <em>kitchen table</em>',tags=['Desk mat','Laptop stand','MX Master 4','Ember Mug'],angle='relatable'),
 dict(layout='E',img='1765030999960-8cc726c281ad',num='10',head='desk upgrades they’ll <em>thank you for</em>',chip='From $20',sub='Every Monday, for years.',angle='number'),
 dict(layout='C',imgs=['1500989145603-8e7ef71d639e','1527864550417-7fd91fc51a46','1618133030686-e1186525ebcc'],chip='Home office gifts',head='The 9-to-5, <em>but nicer</em>',sub='10 gifts for remote workers',angle='aspiration')],
}
SKIP={('gifts-under-25','patches')}  # skin product: no-claims rule
ROT=['B','D','A']
FF=[
 # note-takers
 dict(link='/guides/best-ai-meeting-note-takers/',layout='A',img='1588196749597-9ff075ee6b5b',chip='AI note-takers compared',head='Never type <em>meeting notes</em> by hand again',sub='Fathom, Granola, Otter or Fireflies: free plans, prices and the catch on each.',angle='relief',title='Best AI Meeting Note-Takers 2026 (Free Plans Compared)'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='E',img='1616587226960-4a03badbe8bf',num='4',head='AI note-takers, <em>honestly compared</em>',chip='Free plans included',sub='Which one fits how you work.',angle='number',title='4 AI Note-Takers Compared: Which Is Worth It?'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='B',img='1612831455359-970e23a1e4e9',plabel='Free',price='$0',chip='AI note-takers',head='Hate meeting <em>bots</em>? Read this.',sub='Bot-free options compared, with free plans.',angle='relatable',title='AI Note-Takers Without a Bot Joining Your Call'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='D',img='1668605335684-c97ce92cbd76',plabel='Start',price='Free',head='Be <em style="color:var(--sun)">present</em> in the meeting, not typing',angle='emotional',title='Let AI Take Your Meeting Notes (Free Options)'),
 # slides
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='A',img='1517245386807-bb43f82c33c4',chip='AI presentation makers',head='A full deck from <em>one prompt</em>',sub='Gamma vs Canva vs Copilot: which fits how you work.',angle='relief',title='Gamma vs Canva vs Copilot: Best AI Presentation Maker 2026'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='E',img='1552664730-d307ca884978',num='3',head='AI slide makers, <em>one winner for you</em>',chip='Gamma · Canva · Copilot',sub='Free options, prices and exports.',angle='number',title='3 AI Presentation Makers Compared (2026)'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='B',img='1531403009284-440f080d1e12',plabel='Free',price='$0',chip='AI presentations',head='Stop <em>fighting</em> PowerPoint',sub='Let AI draft the deck; you make it yours.',angle='relatable',title='Make Presentations Faster With AI (Free Tools)'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='D',img='1557804506-669a67965ba0',plabel='Draft in',price='mins',head='Your next deck, <em style="color:var(--sun)">done by lunch</em>',angle='emotional',title='AI Presentation Makers: Draft a Deck in Minutes'),
 # planning
 dict(link='/guides/ai-tools-for-planning-2027/',layout='B',img='1513128034602-7814ccaddd4e',plabel='AI tools',price='7',chip='AI planning tools',head='Plan all of 2027 in <em>one afternoon</em>',tags=['Reclaim.ai','MeetGeek','ClickUp','Gamma'],angle='aspiration',title='7 AI Tools to Plan 2027 (Free Plans + Prices)'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='A',img='1535981767287-35259dbf7d0e',chip='Plan 2027',head='A calendar that <em>protects your focus</em>',sub='7 AI planning tools with free plans, compared.',angle='relief',title='AI Tools That Protect Your Focus Time'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='E',img='1676287566973-7e25f18f12a9',num='7',head='AI tools for a <em>calmer 2027</em>',chip='All have free plans',sub='Plan, meet, present and create.',angle='number',title='7 AI Tools for a Calmer, Better-Planned 2027'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='C',imgs=['1580934174026-8142803ebb5b','1542271484-f163235efa6d','1453928582365-b6ad33cbcf64'],chip='Free plans',head='New year, <em>new system</em>',sub='The 7-tool stack for planning 2027',angle='aspiration',title='Build Your 2027 Planning System With AI'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='D',img='1501504905252-473c47e087f8',plabel='Cost',price='$0',head='Build your 2027 plan <em style="color:var(--sun)">for free</em>',angle='value',title='Plan 2027 With Free AI Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='A',img='1496181133206-80ce9b88a853',chip='Plan 2027',head='Less busywork. <em>More of your year.</em>',sub='Reclaim.ai, ClickUp, Gamma and 4 more, with free plans.',angle='emotional',title='Less Busywork in 2027: 7 AI Tools Worth Trying'),
]
def plain(h): return h.replace('<br>',' ').replace('<em>','').replace('</em>','').split('<em')[0] if '<em ' not in h else __import__('re').sub('<[^>]+>','',h.replace('<br>',' '))
import re
def strip(h): return re.sub(r'<[^>]+>','',h.replace('<br>',' ')).replace('  ',' ').strip()
specs=[]; finds=[]; ff=[]
for slug,g in G.items():
    s=SHORT[slug]
    for k,gp in enumerate(GP[slug]):
        sp=dict(id=f'g-{s}-{k+1}',theme='finds',**{x:y for x,y in gp.items() if x!='angle'}); specs.append(sp)
        finds.append(dict(id=sp['id'],slug=slug,layout=gp['layout'],angle=gp['angle'],kind='guide',title=f"{g['title'].split(' (')[0]} | Digittouch Finds"[:100],hook=strip(gp['head'])))
    n=0
    for b in g['bands']:
        for it in b['items']:
            if (slug,it['id']) in SKIP: continue
            head,angle=H[slug][it['id']]; lay=ROT[n%3]; n+=1
            price=it['price'].replace('$','').replace('-','–')
            sp=dict(id=f'p-{s}-{it["id"]}',theme='finds',layout=lay,img=it['img'].split('photo-')[1].split('?')[0],head=head)
            rng=('–' in price); lab='From' if rng else 'About'
            if lay=='B': sp.update(plabel=lab,price='$'+price.split('–')[0],chip=b['label'],sub=f"{it['name']}. {it['why'].split('.')[0]}.")
            if lay=='D': sp.update(plabel=lab,price='$'+price.split('–')[0],head=head.replace('<em>','<em style="color:var(--sun)">'))
            if lay=='A': sp.update(chip=f"{it['name'][:34]} · ${price}",sub=it['why'].split('.')[0]+'.')
            if len(sp['price' if 'price' in sp else 'head'])>4 and lay in 'BD': sp['price']=sp['price'][:4]
            specs.append(sp)
            finds.append(dict(id=sp['id'],slug=slug,layout=lay,angle=angle,kind='product',item=it['name'],price=it['price'],why=it['why'],title=f"{strip(head)} | {it['name']}"[:100],hook=strip(head)))
for k,f in enumerate(FF):
    sp=dict(id=f'f-{k+1:02d}',theme='ff',**{x:y for x,y in f.items() if x not in('link','angle','title')}); specs.append(sp)
    ff.append(dict(id=sp['id'],link=f['link'],layout=f['layout'],angle=f['angle'],kind='guide',title=f['title'],hook=strip(f['head'])))
json.dump(specs,open(os.path.join(ROOT,'specs.json'),'w'),indent=1,ensure_ascii=False)
# --- schedule: interleave guides; product pins and guide pins mixed
from itertools import zip_longest
by={}
for p in finds: by.setdefault(p['slug'],[]).append(p)
for v in by.values(): v.sort(key=lambda p:(p['kind']!='guide'))  # guide pins first per slug
order=[p for grp in zip_longest(*by.values()) for p in grp if p]
FT5=['13:30','16:00','18:30','20:00','23:30']; FT8=['12:30','14:30','16:00','17:30','19:00','20:30','22:00','23:30']
slots=[]; d=dt.date(2026,11,13)
while len(slots)<len(order):
    times=FT5 if d<dt.date(2026,11,24) else FT8
    slots+= [f"{d}T{t}:00.000Z" for t in times]; d+=dt.timedelta(days=1)
sched=[]
for p,t in zip(order,slots):
    g=G[p['slug']]
    if p['kind']=='guide': desc=f"{g['description']} {TAGS[p['slug']]} #affiliate As an Amazon Associate I earn from qualifying purchases."
    else: desc=f"{p['item']} ({p['price']}): {p['why']} More picks in our {g['title'].split(' (')[0].lower()} guide. {TAGS[p['slug']]} #affiliate As an Amazon Associate I earn from qualifying purchases."
    sched.append(dict(id=p['id'],acct='6af0d3fa9849c2888c6c4d05',board=BOARD[p['slug']],when=t,title=p['title'],content=desc[:500],
      link=f"https://flowframe.shop/finds/{p['slug']}/?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind']))
FFT=['15:00','21:00']; d=dt.date(2026,11,13); i=0
for p in ff:
    t=f"{d}T{FFT[i%2]}:00.000Z"; i+=1
    if i%2==0: d+=dt.timedelta(days=1)
    desc=f"{p['hook']}. Free plans, prices and the honest catch on each tool, in plain English. #AItools #productivity #worksmarter #affiliate Some links may be affiliate links; we may earn a commission at no cost to you."
    sched.append(dict(id=p['id'],acct='6af0cdc55128f5755abb20cc',board='263953296849938525',when=t,title=p['title'],content=desc,
      link=f"https://flowframe.shop{p['link']}?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind']))
json.dump(sched,open(os.path.join(ROOT,'schedule.json'),'w'),indent=1,ensure_ascii=False)
print(len(specs),'specs',len(finds),'finds',len(ff),'ff; finds last slot',slots[len(order)-1])
