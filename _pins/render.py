import asyncio,glob,os,sys
from playwright.async_api import async_playwright
ROOT=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(ROOT,"..","pins","v7")
async def main():
    os.makedirs(OUT,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":1000,"height":1500})
        for f in sorted(glob.glob(os.path.join(ROOT,"html","*.html"))):
            await pg.goto("file://"+f,wait_until="networkidle",timeout=60000)
            await pg.evaluate("document.fonts.ready")
            await pg.wait_for_timeout(600)
            out=os.path.join(OUT,os.path.basename(f)[:-5]+".jpg")
            await pg.screenshot(path=out,type="jpeg",quality=88)
            print("rendered",out)
        await b.close()
asyncio.run(main())
