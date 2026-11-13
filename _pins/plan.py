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
 dict(link='/guides/best-ai-meeting-note-takers/',layout='E',img='1612831455359-970e23a1e4e9',num='4',head='AI note-takers, <em>honestly compared</em>',chip='Free plans included',sub='Which one fits how you work.',angle='number',title='4 AI Note-Takers Compared: Which Is Worth It?'),
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
    if slug not in SHORT: continue
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
            if sp['id']=='p-wfh-mxmaster': sp['img']='1511467687858-23d96c32e4ae'
            specs.append(sp)
            finds.append(dict(id=sp['id'],slug=slug,layout=lay,angle=angle,kind='product',item=it['name'],price=it['price'],why=it['why'],title=f"{strip(head)} | {it['name']}"[:100],hook=strip(head)))
for k,f in enumerate(FF):
    sp=dict(id=f'f-{k+1:02d}',theme='ff',**{x:y for x,y in f.items() if x not in('link','angle','title')}); specs.append(sp)
    ff.append(dict(id=sp['id'],link=f['link'],layout=f['layout'],angle=f['angle'],kind='guide',title=f['title'],hook=strip(f['head'])))

# --- Black Friday 2026 batch (board 250372129223714487). Honest framing: "watchlist", no discount claims.
BF_BOARD='250372129223714487'
BFG=[
 ('gifts-under-25',dict(layout='E',img='1513201099705-a9746e1e201f',num='12',head='Black Friday gifts <em>under $25</em>',chip='Black Friday 2026',sub='Your Secret Santa list, done early.'),'number','12 Black Friday Gift Ideas Under $25 (2026)'),
 ('gifts-for-her-under-60',dict(layout='A',img='1602521163308-23e552671e38',chip='Black Friday · Gifts for her',head='Shop for her <em>before the rush</em>',sub='11 gifts from $16 worth watching this Black Friday.'),'urgency','Black Friday Gifts for Her Under $60 (2026)'),
 ('kitchen-gifts-home-cook',dict(layout='C',imgs=['1598103442097-8b74394b95c6','1622001545761-9bd12a4b465b','1590794056226-79ef3a8147e1'],chip='Black Friday watchlist',head='Kitchen gifts to <em>watch this Black Friday</em>',sub='8 picks, from a $16 zester to a splurge'),'watchlist','Black Friday Kitchen Gift Ideas for the Home Cook'),
 ('work-from-home-gifts',dict(layout='B',img='1511467687858-23d96c32e4ae',plabel='From',price='$20',chip='Black Friday 2026',head='Desk upgrades for your <em>Black Friday list</em>',tags=['MX Master 4','Ember Mug','ScreenBar','Kindle']),'watchlist','Black Friday Work-From-Home Gift Ideas (2026)'),
 ('hair-styler-gifts',dict(layout='D',img='1785456283212-338f5bc44d50',plabel='From',price='$29',head='Hair-tool gifts on <em style="color:var(--sun)">every Black Friday list</em>',size=92),'aspiration','Black Friday Hair Tool Gifts: Dyson, Shark, Laifen and More'),
 ('pet-lover-gifts-under-55',dict(layout='A',img='1672355422293-a912bc3a1d90',chip='Black Friday · Pet lovers',head='Don’t forget <em>the pets</em> this Black Friday',sub='9 gifts for dog and cat people, all under $55.'),'humour','Black Friday Gifts for Pet Lovers Under $55'),
]
BFP=[  # (slug,item id,layout,head,angle)
 ('gifts-under-25','airtag','B','The stocking stuffer <em>they’ll actually use</em>','daily-use'),
 ('kitchen-gifts-home-cook','instantpot','D','Put this on your <em style="color:var(--sun)">Black Friday list</em>','watchlist'),
 ('work-from-home-gifts','kindle','A','The Black Friday gift for <em>every reader</em>','sentimental'),
 ('work-from-home-gifts','ember','B','Coffee that <em>stays hot</em> through every call','relatable'),
 ('work-from-home-gifts','mxmaster','D','Black Friday desk upgrade: <em style="color:var(--sun)">this mouse</em>','watchlist'),
 ('hair-styler-gifts','laifen','A','The fast dryer to <em>watch this Black Friday</em>','watchlist'),
 ('hair-styler-gifts','flexfusion','B','The Airwrap rival <em>to watch</em>','deal'),
 ('hair-styler-gifts','airwrap','D','The splurge on <em style="color:var(--sun)">every</em> Black Friday list','aspiration'),
 ('kitchen-gifts-home-cook','dutchoven','A','The pot they’ll use <em>for decades</em>','sentimental'),
 ('kitchen-gifts-home-cook','allclad','B','Pro pans to <em>watch</em> this Black Friday','watchlist'),
 ('gifts-for-her-under-60','owala','A','The tumbler she’ll <em>carry everywhere</em>','daily-use'),
 ('kitchen-gifts-home-cook','skillet','D','The pan they’ll <em style="color:var(--sun)">pass down</em>','sentimental'),
]
ITEMS={(slug,it['id']):it for slug,g in G.items() for b in g['bands'] for it in b['items']}
bfg=[]; bfp=[]
for k,(slug,gp,angle,title) in enumerate(BFG):
    sp=dict(id=f'bf-g-{SHORT[slug]}',theme='finds',**gp); specs.append(sp)
    bfg.append(dict(id=sp['id'],slug=slug,layout=gp['layout'],angle=angle,kind='guide',title=title,hook=strip(gp['head'])))
for slug,iid,lay,head,angle in BFP:
    it=ITEMS[(slug,iid)]; price=it['price'].replace('$','').replace('-','–'); lab='From' if '–' in price else 'About'
    sp=dict(id=f'bf-p-{iid}',theme='finds',layout=lay,img=it['img'].split('photo-')[1].split('?')[0],head=head)
    if iid=='mxmaster': sp['img']='1511467687858-23d96c32e4ae'
    if lay=='B': sp.update(plabel=lab,price='$'+price.split('–')[0],chip='Black Friday watchlist',sub=f"{it['name']}. {it['why'].split('.')[0]}.")
    if lay=='D': sp.update(plabel=lab,price='$'+price.split('–')[0],size=92)
    if lay=='A': sp.update(chip='Black Friday watchlist',sub=f"{it['name']}. {it['why'].split('.')[0]}.")
    specs.append(sp)
    bfp.append(dict(id=sp['id'],slug=slug,layout=lay,angle=angle,kind='product',item=it['name'],price=it['price'],why=it['why'],title=f"Black Friday 2026: {it['name']}"[:100],hook=strip(head)))

# --- Batch 2 (13 Nov): watchlist page pins, FlowFrame round 2, Cyber Monday, Christmas
WL=[  # links to /finds/black-friday-2026/
 dict(layout='E',img='1513884923967-4b182ef167ab',num='28',head='gifts worth <em>watching</em> this Black Friday',chip='Black Friday 2026',sub='One list, under $25 to the splurge.',angle='number',title='Black Friday 2026 Watchlist: 28 Gifts Worth Watching'),
 dict(layout='A',img='1513884923967-4b182ef167ab',chip='Black Friday watchlist',head='Your whole gift list, <em>in one place</em>',sub='28 picks across tech, kitchen, hair tools and pets.',angle='relief',title='Black Friday Gift List 2026: Tech, Kitchen, Hair and Pets'),
 dict(layout='C',imgs=['1603508102977-02688e3265fd','1544233726-9f1d2b27be8b','1580618672591-eb180b1a973f'],chip='Black Friday 2026',head='Shop smarter <em>this Black Friday</em>',sub='28 picks, the honest catch on each',angle='practical',title='How to Shop Black Friday 2026: 28 Picks With the Honest Catch'),
 dict(layout='B',img='1607082348824-0a96f2a4b9da',plabel='From',price='$12',chip='Black Friday watchlist',head='Know what to buy <em>before</em> the rush',tags=['AirTag','Instant Pot','Kindle','Shark FlexFusion'],angle='urgency',title='Black Friday 2026: Decide What to Buy Before the Rush'),
 dict(layout='D',img='1513201099705-a9746e1e201f',plabel='Picks',price='28',head='Black Friday, <em style="color:var(--sun)">without the stress</em>',angle='emotional',title='Stress-Free Black Friday: 28 Gifts Already Picked for You'),
 dict(layout='A',img='1612373914372-79a8a0311f78',chip='Black Friday · Gift list',head='Done with gift shopping <em>by December</em>',sub='The 28 picks worth watching, sorted by who you are buying for.',angle='aspiration',title='Finish Christmas Shopping on Black Friday: 28 Picks'),
 dict(layout='E',img='1590794056226-79ef3a8147e1',num='6',head='gift lists, <em>one Black Friday watchlist</em>',chip='Under $25 to splurge',sub='For her, kitchen, desk, hair and pets.',angle='number',title='Black Friday 2026 Watchlist: 6 Gift Lists in One'),
 dict(layout='C',imgs=['1500989145603-8e7ef71d639e','1734111719430-fe4a3973f8af','1571131116858-2295ade82a72'],chip='Black Friday weekend',head='Still deciding? <em>Start here.</em>',sub='28 gifts worth watching, honest catch on each',angle='relief',title='Black Friday Weekend: 28 Gifts Worth Watching'),
]
FF2=[
 dict(link='/guides/best-ai-meeting-note-takers/',layout='C',imgs=['1588196749597-9ff075ee6b5b','1612831455359-970e23a1e4e9','1668605335684-c97ce92cbd76'],chip='AI note-takers',head='Your meetings, <em>summarised for you</em>',sub='Fathom, Granola, Otter, Fireflies compared',angle='relief',title='AI Meeting Summaries: 4 Note-Takers Compared (2026)'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='A',img='1668605335684-c97ce92cbd76',chip='Free plans compared',head='The free AI note-taker <em>worth trying first</em>',sub='Which free plan fits how you meet, and the catch on each.',angle='value',title='Best Free AI Note-Taker 2026: Which to Try First'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='D',img='1758521541657-fd70465a5c54',plabel='Notes',price='Auto',head='Stop taking <em style="color:var(--sun)">meeting notes</em>',angle='relief',title='Stop Taking Meeting Notes: Let AI Do It'),
 dict(link='/guides/best-ai-meeting-note-takers/',layout='A',img='1612831455359-970e23a1e4e9',chip='Bot or no bot?',head='Ask this <em>before</em> you pick an AI note-taker',sub='The one difference that matters most, and which tools get it right.',angle='curiosity',title='Choosing an AI Note-Taker: The One Question That Matters'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='C',imgs=['1517245386807-bb43f82c33c4','1552664730-d307ca884978','1557804506-669a67965ba0'],chip='Gamma · Canva · Copilot',head='Which AI slide maker <em>is right for you?</em>',sub='Free options, prices and exports',angle='practical',title='Gamma vs Canva vs Copilot: Which AI Slide Maker Fits You?'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='A',img='1531403009284-440f080d1e12',chip='AI presentations',head='From blank page to deck <em>in minutes</em>',sub='How Gamma, Canva and Copilot compare for real work.',angle='relief',title='AI Presentation Makers: From Blank Page to Deck in Minutes'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='B',img='1552664730-d307ca884978',plabel='Tools',price='3',chip='Slides with AI',head='The <em>best</em> AI presentation maker?',tags=['Gamma','Canva','Copilot'],angle='curiosity',title='The Best AI Presentation Maker in 2026? 3 Compared'),
 dict(link='/guides/gamma-vs-canva-vs-copilot/',layout='D',img='1517245386807-bb43f82c33c4',plabel='Start',price='Free',head='Make slides <em style="color:var(--sun)">people remember</em>',angle='aspiration',title='Make Better Slides With Free AI Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='E',img='1513128034602-7814ccaddd4e',num='2027',head='planned with <em>7 free AI tools</em>',chip='Plan your year',sub='Calendar, meetings, tasks and slides.',angle='number',size=96,title='Plan 2027 With 7 Free AI Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='C',imgs=['1535981767287-35259dbf7d0e','1496181133206-80ce9b88a853','1501504905252-473c47e087f8'],chip='Plan 2027',head='Start 2027 <em>already organised</em>',sub='7 AI planning tools with free plans',angle='aspiration',title='Start 2027 Organised: 7 AI Planning Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='B',img='1501504905252-473c47e087f8',plabel='Cost',price='$0',chip='AI planning tools',head='Your 2027 plan, <em>on autopilot</em>',tags=['Reclaim.ai','MeetGeek','ClickUp','Gamma'],angle='relief',title='Put Your 2027 Planning on Autopilot With AI'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='D',img='1580934174026-8142803ebb5b',plabel='Tools',price='7',head='New year, <em style="color:var(--sun)">less busywork</em>',angle='emotional',title='Less Busywork in 2027: 7 AI Planning Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='A',img='1542271484-f163235efa6d',chip='Plan 2027',head='Protect your <em>focus time</em> next year',sub='AI calendars and planners with free plans, compared.',angle='relief',title='Protect Your Focus Time in 2027 With AI Tools'),
 dict(link='/guides/ai-tools-for-planning-2027/',layout='E',img='1453928582365-b6ad33cbcf64',num='7',head='AI tools worth <em>starting 2027 with</em>',chip='All have free plans',sub='Plan, meet, present and create.',angle='number',title='7 AI Planning Tools Worth Starting 2027 With'),
]
CM=[  # Cyber Monday 30 Nov; (slug, spec, angle, title)
 ('gifts-under-25',dict(layout='A',img='1601804590276-e19ce20343da',chip='Cyber Monday',head='Missed Black Friday? <em>Start here.</em>',sub='12 gifts under $25, with the honest catch on each.'),'relief','Cyber Monday 2026: 12 Gift Ideas Under $25'),
 ('kitchen-gifts-home-cook',dict(layout='D',img='1518291344630-4857135fb581',plabel='From',price='$16',head='Cyber Monday <em style="color:var(--sun)">kitchen gifts</em>',size=96),'occasion','Cyber Monday 2026: Kitchen Gifts for the Home Cook'),
 ('work-from-home-gifts',dict(layout='E',img='1518976024611-28bf4b48222e',num='10',head='Cyber Monday <em>desk upgrades</em>',chip='From $20',sub='For anyone who works from home.'),'number','Cyber Monday 2026: 10 Work-From-Home Gift Ideas'),
 ('hair-styler-gifts',dict(layout='B',img='1769029270594-26ce033ca6fc',plabel='From',price='$29',chip='Cyber Monday',head='Hair-tool gifts <em>worth checking today</em>',tags=['Revlon','Laifen','Shark','Dyson']),'urgency','Cyber Monday 2026: Hair Tool Gifts Worth Checking'),
 ('gifts-for-her-under-60',dict(layout='C',imgs=['1687435703153-88f6bc0cdcff','1611591437281-460bfbe1220a','1668112037360-900ff60ef6f7'],chip='Cyber Monday',head='Gifts for her, <em>one last look</em>',sub='11 picks from $16, honest catch on each'),'urgency','Cyber Monday 2026: Gifts for Her Under $60'),
 ('pet-lover-gifts-under-55',dict(layout='A',img='1672355422293-a912bc3a1d90',chip='Cyber Monday · Pets',head='The pets deserve <em>a gift too</em>',sub='9 gifts for dog and cat people, all under $55.'),'humour','Cyber Monday 2026: Gifts for Pet Lovers Under $55'),
]
XM=[  # Christmas 1-6 Dec
 ('gifts-under-25',dict(layout='E',img='1513201099705-a9746e1e201f',num='12',head='stocking stuffers <em>under $25</em>',chip='Christmas 2026',sub='Small gifts they will actually use.'),'number','12 Stocking Stuffers Under $25 (Christmas 2026)'),
 ('gifts-under-25',dict(layout='D',img='1607900177462-ac553f1f5d97',plabel='All under',price='$25',head='Secret Santa <em style="color:var(--sun)">sorted</em>',size=104),'occasion','Secret Santa Gift Ideas Under $25 (2026)'),
 ('gifts-for-her-under-60',dict(layout='A',img='1602521163308-23e552671e38',chip='Christmas · For her',head='The gift she’ll <em>actually keep</em>',sub='11 thoughtful picks from $16, sorted by budget.'),'emotional','Christmas Gifts for Her Under $60 (2026)'),
 ('gifts-for-her-under-60',dict(layout='B',img='1513885535751-8b9238bd345a',plabel='From',price='$16',chip='Christmas gifts for her',head='For mum, sister or <em>best friend</em>',tags=['Silk eye mask','Owala','Gold cuff','LEGO plants']),'relatable','Christmas Gift Ideas for Mum, Sister or Best Friend'),
 ('kitchen-gifts-home-cook',dict(layout='A',img='1603185730021-ddc0c8097059',chip='Christmas · Kitchen',head='For the one who <em>cooks Christmas dinner</em>',sub='8 kitchen gifts from $16 to a splurge.'),'sentimental','Christmas Gifts for the Person Who Cooks Christmas Dinner'),
 ('kitchen-gifts-home-cook',dict(layout='C',imgs=['1598103442097-8b74394b95c6','1622001545761-9bd12a4b465b','1590794056226-79ef3a8147e1'],chip='Christmas 2026',head='Kitchen gifts <em>they’ll use all year</em>',sub='8 picks for the home cook'),'practical','Kitchen Christmas Gifts They Will Use All Year'),
 ('work-from-home-gifts',dict(layout='B',img='1511467687858-23d96c32e4ae',plabel='From',price='$20',chip='Christmas · Home office',head='Make their January desk <em>a better place</em>',tags=['Desk mat','Laptop stand','Ember Mug','Kindle']),'aspiration','Christmas Gifts for People Who Work From Home'),
 ('work-from-home-gifts',dict(layout='D',img='1500989145603-8e7ef71d639e',plabel='From',price='$20',head='For the colleague who <em style="color:var(--sun)">has everything</em>',size=92),'relatable','Christmas Gifts for the Colleague Who Has Everything'),
 ('hair-styler-gifts',dict(layout='A',img='1734111719430-fe4a3973f8af',chip='Christmas · Hair tools',head='Good hair days <em>under the tree</em>',sub='8 hair tools from $29, each with the honest catch.'),'emotional','Hair Tool Christmas Gifts: From $29 to Dyson'),
 ('hair-styler-gifts',dict(layout='E',img='1712481846916-8f73ffc2067a',num='8',head='hair tools on <em>her Christmas list</em>',chip='From $29',sub='Dryers, brushes and stylers.'),'number','8 Hair Tools on Her Christmas List (2026)'),
 ('pet-lover-gifts-under-55',dict(layout='C',imgs=['1675543999462-3b3157b044c2','1571131116858-2295ade82a72','1591946614720-90a587da4a36'],chip='Christmas 2026',head='Christmas for the <em>whole family</em>, fur included',sub='9 pet gifts under $55'),'emotional','Christmas Gifts for Pets and Pet Lovers Under $55'),
 ('pet-lover-gifts-under-55',dict(layout='D',img='1774440865482-81a8c9b92e76',plabel='All under',price='$55',head='A stocking for <em style="color:var(--sun)">the dog</em>',size=104),'humour','Dog Stocking Stuffers and Pet Gifts Under $55'),
]
b2=[]
for k,w in enumerate(WL):
    sp=dict(id=f'wl-{k+1}',theme='finds',**{x:y for x,y in w.items() if x not in('angle','title')}); specs.append(sp)
    b2.append(dict(id=sp['id'],slug='black-friday-2026',layout=w['layout'],angle=w['angle'],kind='guide',title=w['title'],hook=strip(w['head']),board=BF_BOARD,batch='wl'))
for k,f in enumerate(FF2):
    sp=dict(id=f'f2-{k+1:02d}',theme='ff',**{x:y for x,y in f.items() if x not in('link','angle','title')}); specs.append(sp)
    b2.append(dict(id=sp['id'],link=f['link'],layout=f['layout'],angle=f['angle'],kind='guide',title=f['title'],hook=strip(f['head']),batch='ff2'))
for pre,lst in (('cm',CM),('xm',XM)):
    for k,(slug,gp,angle,title) in enumerate(lst):
        sp=dict(id=f'{pre}-{SHORT[slug]}-{k+1}',theme='finds',**gp); specs.append(sp)
        b2.append(dict(id=sp['id'],slug=slug,layout=gp['layout'],angle=angle,kind='guide',title=title,hook=strip(gp['head']),board=BOARD[slug],batch=pre))

# --- Webcam guide pins (FlowFrame, earns via Amazon) -> board Home Office Setup Ideas
WC_BOARD='263953296849966877'
WC=[
 dict(layout='E',img='1758521541657-fd70465a5c54',num='7',head='webcams that make you <em>look better on calls</em>',chip='From $25 to $199',sub='Compared from expert reviews.',angle='number',title='7 Best Webcams for Video Calls in 2026 (From $25)'),
 dict(layout='A',img='1668605335684-c97ce92cbd76',chip='Webcams compared',head='Look clearer on <em>every video call</em>',sub='7 webcams from $25 to $199, with the catch on each.',angle='aspiration',title='Best Webcams for Zoom and Teams Calls (2026)'),
 dict(layout='B',img='1588196749597-9ff075ee6b5b',plabel='From',price='$25',chip='Webcam upgrade',head='The upgrade <em>your calls</em> are missing',tags=['Anker C200','Logitech C920s','Brio 500','Insta360'],angle='relief',title='Best Webcam Upgrade for Video Calls: 7 Picks'),
 dict(layout='D',img='1758521541657-fd70465a5c54',plabel='From',price='$25',head='Your laptop camera <em style="color:var(--sun)">is the problem</em>',angle='relatable',title='Laptop Camera Too Grainy? 7 Webcams That Fix It'),
 dict(layout='C',imgs=['1758521541657-fd70465a5c54','1612831455359-970e23a1e4e9','1668605335684-c97ce92cbd76'],chip='Webcams 2026',head='Grainy on calls? <em>Upgrade from $25</em>',sub='7 picks, from budget to 4K',angle='value',title='Grainy on Video Calls? Webcams From $25'),
 dict(layout='A',img='1612831455359-970e23a1e4e9',chip='Home office',head='Work from home? <em>Upgrade this first</em>',sub='The webcam is the cheapest way to look better on every call.',angle='practical',title='Work From Home Upgrade: The Best Webcams for Calls'),
 dict(layout='E',img='1668605335684-c97ce92cbd76',num='4K',head='webcams worth it <em>for calls</em>?',chip='Honest comparison',sub='When 4K helps, and when 1080p is plenty.',angle='curiosity',title='Is a 4K Webcam Worth It for Video Calls?'),
]
for k,w in enumerate(WC):
    sp=dict(id=f'wc-{k+1}',theme='ff',**{x:y for x,y in w.items() if x not in('angle','title')}); specs.append(sp)
    b2.append(dict(id=sp['id'],layout=w['layout'],angle=w['angle'],kind='guide',title=w['title'],hook=strip(w['head']),batch='wc'))
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

# BF schedule: 2/day at 11:00 and 22:00 UTC (no clash with existing slots), 13-21 Nov, guide and product pins interleaved
bford=[]; gi=iter(bfg); pi=iter(bfp)
for k in range(len(bfg)+len(bfp)):
    nxt=next(gi,None) if k%3==0 else None
    bford.append(nxt or next(pi,None) or next(gi))
d=dt.date(2026,11,13); i=0
for p in bford:
    t=f"{d}T{['11:00','22:00'][i%2]}:00.000Z"; i+=1
    if i%2==0: d+=dt.timedelta(days=1)
    g=G[p['slug']]
    if p['kind']=='guide': desc=f"{p['hook']}. {g['description']} Prices change daily, so check the current price before you buy. #blackfriday #blackfriday2026 {TAGS[p['slug']]} #affiliate As an Amazon Associate I earn from qualifying purchases."
    else: desc=f"{p['item']} (around {p['price']} before sales): {p['why']} Add it to your Black Friday watchlist and check the current price. More picks in our {g['title'].split(' (')[0].lower()} guide. #blackfriday #blackfriday2026 {TAGS[p['slug']]} #affiliate As an Amazon Associate I earn from qualifying purchases."
    sched.append(dict(id=p['id'],acct='6af0d3fa9849c2888c6c4d05',board=BF_BOARD,when=t,title=p['title'],content=desc[:500],
      link=f"https://flowframe.shop/finds/{p['slug']}/?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind'],batch='bf'))

# Batch 2 schedule
SPN={x['id']:x.get('num') for x in specs if x.get('layout')=='E'}
for p in b2:
    if SPN.get(p['id']) and p['hook'][:1].islower(): p['hook']=f"{SPN[p['id']]} {p['hook']}"
WLD=['2026-11-14','2026-11-15','2026-11-17','2026-11-19','2026-11-21','2026-11-23','2026-11-25','2026-11-26']
GBF=json.load(open(os.path.join(REPO,'_tools/guides/black-friday-2026.json')))
def tagsfor(slug): return TAGS.get(slug,'#blackfriday #giftideas #blackfriday2026')
wl=[p for p in b2 if p['batch']=='wl']; ffp=[p for p in b2 if p['batch']=='ff2']; cm=[p for p in b2 if p['batch']=='cm']; xm=[p for p in b2 if p['batch']=='xm']
when={}
for p,d in zip(wl,WLD): when[p['id']]=f"{d}T10:00:00.000Z"
d=dt.date(2026,11,20)
for i,p in enumerate(ffp): when[p['id']]=f"{d+dt.timedelta(days=i//2)}T{['15:00','21:00'][i%2]}:00.000Z"
CMT=['13:30','18:30']; d=dt.date(2026,11,28)
for i,p in enumerate(cm): when[p['id']]=f"{d+dt.timedelta(days=i//2)}T{CMT[i%2]}:00.000Z"
XMT=['13:30','20:00']; d=dt.date(2026,12,1)

xm2=xm[0::2]+xm[1::2]
for i,p in enumerate(xm2): when[p['id']]=f"{d+dt.timedelta(days=i//2)}T{XMT[i%2]}:00.000Z"
d=dt.date(2026,11,14)
for i,p in enumerate([q for q in b2 if q['batch']=='wc']): when[p['id']]=f"{d+dt.timedelta(days=i)}T18:00:00.000Z"
for p in b2:
    if p['batch']=='wc':
        desc=f"{p['hook']}. 7 webcams for Zoom, Teams and Meet calls, from $25 to $199, compared from expert reviews with the catch on each. #webcam #homeoffice #workfromhome #videocalls #affiliate As an Amazon Associate I earn from qualifying purchases."
        sched.append(dict(id=p['id'],acct='6af0cdc55128f5755abb20cc',board=WC_BOARD,when=when[p['id']],title=p['title'],content=desc,
          link=f"https://flowframe.shop/guides/best-webcams-for-video-calls/?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind'],batch='wc'))
        continue
    if p['batch']=='ff2':
        desc=f"{p['hook']}. Free plans, prices and the honest catch on each tool, in plain English. #AItools #productivity #worksmarter #affiliate Some links may be affiliate links; we may earn a commission at no cost to you."
        sched.append(dict(id=p['id'],acct='6af0cdc55128f5755abb20cc',board='263953296849938525',when=when[p['id']],title=p['title'],content=desc,
          link=f"https://flowframe.shop{p['link']}?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind'],batch='ff2'))
        continue
    g=GBF if p['slug']=='black-friday-2026' else G[p['slug']]
    extra={'wl':'Prices change daily, so check the current price before you buy. #blackfriday #blackfriday2026 #giftideas',
           'cm':'Prices change daily, so check the current price before you buy. #cybermonday #cybermonday2026 '+tagsfor(p['slug']),
           'xm':'#christmasgifts #christmas2026 '+tagsfor(p['slug'])}[p['batch']]
    desc=f"{p['hook']}. {g['description']} {extra} #affiliate As an Amazon Associate I earn from qualifying purchases."
    sched.append(dict(id=p['id'],acct='6af0d3fa9849c2888c6c4d05',board=p['board'],when=when[p['id']],title=p['title'][:100],content=desc[:500],
      link=f"https://flowframe.shop/finds/{p['slug']}/?utm_source=pinterest&utm_medium=social&utm_campaign={p['id']}",img=f"https://flowframe.shop/pins/v7/{p['id']}.jpg",layout=p['layout'],angle=p['angle'],kind=p['kind'],batch=p['batch']))
json.dump(sched,open(os.path.join(ROOT,'schedule.json'),'w'),indent=1,ensure_ascii=False)
print(len(specs),'specs',len(finds),'finds',len(ff),'ff; finds last slot',slots[len(order)-1])
