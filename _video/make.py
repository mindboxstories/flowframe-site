"""Build a faceless guide video: our own guide page, screen-captured, with a voiceover.
Usage: python _video/make.py _video/<slug>/script.json   (runs in GitHub Actions; see .github/workflows/video.yml)
Steps: 1) Kokoro TTS per segment (Apache-2.0 model) -> audio + caption timings
       2) Playwright captures the live page: one 4K still per segment + scroll frames between them
       3) Python composes 1080p30 frames (slow push-in toward the item being discussed) piped to ffmpeg
Outputs in _video/out/<slug>/: video.mp4, captions.srt, chapters.txt, frames/*.jpg (QA), timeline.json"""
import json, os, sys, subprocess, math, re
import numpy as np

FPS, W, H = 30, 1920, 1080
VW, VH, DPR = 1280, 720, 3          # page viewport (CSS px) x DPR -> 3840x2160 stills
TRANS = 0.6                          # seconds of scroll between segments
PAD = 0.45                           # silence after each segment's speech
SR = 24000

spec = json.load(open(sys.argv[1]))
OUT = os.path.join(os.path.dirname(__file__), "out", spec["slug"])
os.makedirs(os.path.join(OUT, "frames"), exist_ok=True)
os.makedirs(os.path.join(OUT, "shots"), exist_ok=True)
segs = spec["segments"]


# ---------- 1. voiceover ----------
def tts():
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    for s in segs:
        chunks, audio = [], []
        t = 0.0
        for gs, ps, a in pipe(s["text"], voice=spec.get("voice", "af_heart"), speed=spec.get("speed", 1.0), split_pattern=r"(?<=[.?!:])\s+"):
            a = a.numpy() if hasattr(a, "numpy") else np.asarray(a)
            chunks.append({"text": gs.strip(), "start": t, "end": t + len(a) / SR})
            t += len(a) / SR
            audio.append(a)
        s["audio"] = np.concatenate(audio).astype(np.float32)
        s["dur"] = t
        s["chunks"] = chunks
        print(f"tts {s['id']}: {t:.1f}s")


# ---------- 2. capture ----------
JS_POS = """(sel) => {
  if (sel === 'top') return {y: 0, box: null};
  const el = document.querySelector(sel); if (!el) return null;
  const r = el.getBoundingClientRect(), top = r.top + scrollY, vh = innerHeight, head = 70;
  let y = r.height < vh - head - 30 ? top - head - (vh - head - r.height) / 2 : top - head - 12;
  y = Math.max(0, Math.min(y, document.documentElement.scrollHeight - vh));
  return {y, box: {x: r.left, y: top - y, w: r.width, h: r.height}};
}"""


def capture():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": VW, "height": VH}, device_scale_factor=DPR, reduced_motion="reduce")
        pg = ctx.new_page()
        pg.route(re.compile(r".*(goatcounter|zgo\.at).*"), lambda r: r.abort())
        pg.goto(spec["url"], wait_until="networkidle")
        pg.add_style_tag(content=".ann,.g-bar{display:none!important} .g-card.focus{box-shadow:0 0 0 4px var(--accent),0 24px 48px -18px rgba(0,0,0,.35)!important;border-color:transparent!important} html{scroll-behavior:auto!important} *{transition:none!important;animation:none!important}")
        # load every lazy image, then return to the top
        hgt = pg.evaluate("document.documentElement.scrollHeight")
        for y in range(0, hgt, 500):
            pg.evaluate(f"scrollTo(0,{y})"); pg.wait_for_timeout(120)
        pg.wait_for_load_state("networkidle")
        pg.wait_for_function("[...document.images].every(i => i.complete)", timeout=30000)
        pg.evaluate("document.fonts.ready")
        pos = []
        for s in segs:
            r = pg.evaluate(JS_POS, s["target"])
            if r is None:
                raise SystemExit(f"selector not found: {s['target']}")
            pos.append(r)
        prev = None
        for i, (s, r) in enumerate(zip(segs, pos)):
            if prev is not None:   # scroll frames from the previous position, eased
                n = int(TRANS * FPS)
                for k in range(1, n + 1):
                    e = 0.5 - 0.5 * math.cos(math.pi * k / n)
                    pg.evaluate(f"scrollTo(0,{prev + (r['y'] - prev) * e})"); pg.wait_for_timeout(20)
                    pg.screenshot(path=f"{OUT}/shots/{i:02d}_t{k:02d}.jpg", type="jpeg", quality=90)
            pg.evaluate(f"scrollTo(0,{r['y']})"); pg.wait_for_timeout(250)
            pg.screenshot(path=f"{OUT}/shots/{i:02d}_hold.png")
            if s.get("item"):   # second still: this card highlighted, the rest dimmed (crossfaded in compose)
                pg.evaluate("""(sel) => { const t = document.querySelector(sel);
                  document.querySelectorAll('.g-card').forEach(c => c.classList.toggle(c === t ? 'focus' : 'dim', true)); }""", s["target"])
                pg.wait_for_timeout(150)
                pg.screenshot(path=f"{OUT}/shots/{i:02d}_focus.png")
                pg.evaluate("document.querySelectorAll('.g-card').forEach(c => c.classList.remove('focus','dim'))")
            s["box"] = r["box"]
            prev = r["y"]
        b.close()


# ---------- 3. compose ----------
def compose():
    from PIL import Image
    full = (VW * DPR, VH * DPR)

    def frame_at(img, cx, cy, z):
        cw, ch = full[0] / z, full[1] / z
        x0 = min(max(cx - cw / 2, 0), full[0] - cw)
        y0 = min(max(cy - ch / 2, 0), full[1] - ch)
        return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch), reducing_gap=2.0)

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-i", f"{OUT}/voice.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/video.mp4"], stdin=subprocess.PIPE)
    t, timeline = 0.0, []
    for i, s in enumerate(segs):
        if i:
            n = int(TRANS * FPS)
            for k in range(1, n + 1):
                im = Image.open(f"{OUT}/shots/{i:02d}_t{k:02d}.jpg").convert("RGB")
                ff.stdin.write(np.asarray(im.resize((W, H), Image.BILINEAR, reducing_gap=2.0)).tobytes())
            t += n / FPS
        im = Image.open(f"{OUT}/shots/{i:02d}_hold.png").convert("RGB")
        fo = Image.open(f"{OUT}/shots/{i:02d}_focus.png").convert("RGB") if s.get("item") else None
        dur = s["dur"] + PAD
        nf = int(round(dur * FPS))
        dur = nf / FPS
        c0 = (full[0] / 2, full[1] / 2)
        if s.get("item") and s["box"]:
            bx = s["box"]
            c1 = ((bx["x"] + bx["w"] / 2) * DPR, (bx["y"] + bx["h"] / 2) * DPR)
            c1 = (c0[0] + (c1[0] - c0[0]) * 0.4, c0[1] + (c1[1] - c0[1]) * 0.4)
            zmax = 1.06
        else:
            c1, zmax = c0, 1.05
        for f in range(nf):
            tt = f / FPS
            a = min(tt / 1.4, 1.0); a = 0.5 - 0.5 * math.cos(math.pi * a)            # ease in over 1.4s
            back = max(0.0, (tt - (dur - 0.55)) / 0.55); back = 0.5 - 0.5 * math.cos(math.pi * min(back, 1))  # ease out in last 0.55s
            drift = 1 + 0.02 * (tt / dur)
            m = a * (1 - back)
            z = 1 + (zmax * drift - 1) * m
            cx, cy = c0[0] + (c1[0] - c0[0]) * m, c0[1] + (c1[1] - c0[1]) * m
            fr = frame_at(im, cx, cy, z)
            if fo is not None:
                fr = Image.blend(fr, frame_at(fo, cx, cy, z), m)
            ff.stdin.write(np.asarray(fr).tobytes())
            if f == int(min(2.0, dur / 2) * FPS):
                fr.resize((960, 540)).save(f"{OUT}/frames/{i:02d}_{s['id']}.jpg", quality=82)
        timeline.append({"id": s["id"], "start": round(t, 2), "speech": round(s["dur"], 2), "chunks": [dict(c, start=c["start"] + t, end=c["end"] + t) for c in s["chunks"]]})
        t += dur
    ff.stdin.close(); ff.wait()
    json.dump(timeline, open(f"{OUT}/timeline.json", "w"), indent=1)
    return timeline


def write_audio():
    import soundfile as sf
    n = int(TRANS * FPS)
    parts = []
    for i, s in enumerate(segs):
        if i:
            parts.append(np.zeros(n * SR // FPS, np.float32))
        nf = int(round((s["dur"] + PAD) * FPS))
        parts.append(s["audio"]); parts.append(np.zeros(max(0, nf * SR // FPS - len(s["audio"])), np.float32))
    a = np.concatenate(parts)
    a = a / max(1e-6, np.abs(a).max()) * 0.89   # peak normalise to about -1 dBFS
    sf.write(f"{OUT}/voice.wav", a, SR)


def srt(timeline):
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"
    cues = []
    for seg in timeline:
        for c in seg["chunks"]:
            words = c["text"].split()
            parts, cur = [], []
            for w in words:   # split long sentences into readable cues of <= ~70 chars
                if cur and len(" ".join(cur + [w])) > 70:
                    parts.append(cur); cur = []
                cur.append(w)
            if cur: parts.append(cur)
            total = sum(len(" ".join(p)) for p in parts)
            st = c["start"]
            for p in parts:
                d = (c["end"] - c["start"]) * len(" ".join(p)) / total
                cues.append((st, st + d, " ".join(p))); st += d
    with open(f"{OUT}/captions.srt", "w") as f:
        for k, (a, b, txt) in enumerate(cues, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    names = spec.get("chapters", {})
    with open(f"{OUT}/chapters.txt", "w") as f:
        for seg in timeline:
            if seg["id"] in names:
                m, s_ = divmod(int(seg["start"]), 60)
                f.write(f"{m}:{s_:02d} {names[seg['id']]}\n")


if __name__ == "__main__":
    tts()
    capture()
    write_audio()
    tl = compose()
    srt(tl)
    print("done", os.path.getsize(f"{OUT}/video.mp4") // 1_000_000, "MB")
