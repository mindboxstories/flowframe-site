"""One-deal vertical Short (Digittouch Finds daily deal). Usage: python make_deal.py <spec.json>
Kokoro voice per sentence -> word timings -> original music bed + SFX (from the v2 renderer) -> deal.html frames -> mp4.
Images in the spec: "unsplash:<photo id>" (fetched from images.unsplash.com at the right crop) or a path/URL.
Runs on GitHub Actions (.github/workflows/deals.yml). Output: _video/out/<slug>/ (video.mp4, cover.jpg, captions.srt, frames/)."""
import ast, json, os, re, subprocess, sys
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, W, H, SR = 30, 1080, 1920, 24000
spec = json.load(open(sys.argv[1]))
OUT = os.path.join(HERE, "..", "out", spec["slug"]); os.makedirs(f"{OUT}/frames", exist_ok=True)
segs = spec["segments"]

# reuse the approved music bed + SFX from the v2 pipeline (original, generated: no licence questions)
src = open(os.path.join(HERE, "..", "v2", "make2.py")).read()
for node in ast.parse(src).body:
    if isinstance(node, ast.FunctionDef) and node.name in ("synth_music", "sfx"):
        exec(compile(ast.Module([node], []), "make2", "exec"), globals())

SIZES = {"img": (1080, 1920), "why_img": (1080, 880), "catch_img": (1080, 1920), "imgs": (600, 760)}


def img_url(v, key):
    if v.startswith("unsplash:"):
        w, h = SIZES[key]
        return f"https://images.unsplash.com/{v.split(':', 1)[1]}?w={w}&h={h}&fit=crop&crop=entropy&q=80&auto=format"
    return v


for s in segs:
    for k in ("img", "why_img", "catch_img"):
        if k in s: s[k] = img_url(s[k], k)
    if "imgs" in s: s["imgs"] = [img_url(u, "imgs") for u in s["imgs"]]


def tts():
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    gap = np.zeros(int(.06 * SR), np.float32)
    for s in segs:
        parts, words, t = [], [], 0.0
        for sent in s["say"]:
            say = re.sub(r"\bcatch\b", "[catch](/kˈæʧ/)", sent)
            a = np.concatenate([(r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)).astype(np.float32)
                                for r in pipe(say, voice=spec["voice"], speed=spec["speed"], split_pattern=r"\n+")])
            env = np.abs(a) > 10 ** (-42 / 20)
            i0 = max(0, int(np.argmax(env)) - int(.03 * SR)); i1 = min(len(a), len(a) - int(np.argmax(env[::-1])) + int(.05 * SR)); a = a[i0:i1]
            ws = sent.split(); wt = [len(re.sub(r"\W", "", w)) + 1.5 for w in ws]; tot = sum(wt); c = t; d0 = len(a) / SR
            for w, x in zip(ws, wt):
                d = d0 * x / tot; cap = s.get("cap", {}).get(w.strip(".,:?!").lower())
                ent = {"w": w, "s": round(c, 3), "e": round(c + d, 3)}
                if cap is not None:
                    if cap == "": words[-1]["e"] = round(c + d, 3); c += d; continue
                    ent["cap"] = cap + (w[-1] if w[-1] in ".,:?!" else "")
                words.append(ent); c += d
            parts += [a, gap]; t += d0 + len(gap) / SR
        s["audio"] = np.concatenate(parts); s["speech"] = len(s["audio"]) / SR; s["words"] = words
        print(f"tts {s['id']}: {s['speech']:.2f}s")


def first(s, pat):
    r = re.compile(pat, re.I)
    return next((w["s"] for w in s["words"] if r.search(w["w"])), None)


def timeline():
    t = 0.0
    for s in segs:
        s["start"] = round(t, 3); s["dur"] = round(s["speech"] + s.get("hold", .25), 3); t += s["dur"]
        if s["kind"] == "item":
            s["cues"] = {"price": .55, "why": first(s, s["why_cue"]) - .1, "catch": first(s, s["catch_cue"]) - .1,
                         "tags": [first(s, p) - .05 for p in s["tag_cues"]]}
        if s["kind"] == "cta":
            s["follow_at"] = first(s, s["follow_cue"]) or 1.5
    return t


def audio(total):
    sr = 48000
    v = np.zeros(int(total * sr) + sr, np.float32); speech = np.zeros_like(v, dtype=bool)
    for s in segs:
        a = s["audio"]; a48 = np.interp(np.arange(int(len(a) * sr / SR)) / sr, np.arange(len(a)) / SR, a).astype(np.float32)
        i = int(s["start"] * sr); v[i:i + len(a48)] += a48[: len(v) - i]
        for w in s["words"]: speech[max(0, int((s["start"] + w["s"] - .15) * sr)): int((s["start"] + w["e"] + .25) * sr)] = True
    v = v[: int(total * sr)]; speech = speech[: len(v)]
    mus, _ = synth_music(total)
    g = np.where(speech, .16, .55).astype(np.float32); kk = int(.12 * sr); g = np.convolve(g, np.ones(kk) / kk, mode="same")
    mus = mus[: len(v)] * g
    fx = sfx(sr); fxt = np.zeros_like(v)
    def put(x, t0, gain):
        i = int(t0 * sr); j = min(len(fxt), i + len(x))
        if 0 <= i < len(fxt): fxt[i:j] += gain * x[: j - i]
    put(fx["pop"], .05, .5)
    for s in segs:
        if s["start"] > 0: put(fx["whoosh"], s["start"] - .21, .32)
        if s["kind"] == "item":
            c = s["cues"]; put(fx["pop"], s["start"] + c["price"], .5); put(fx["whoosh"], s["start"] + c["why"] - .05, .16); put(fx["tick"], s["start"] + c["catch"], .45)
            for tc in c["tags"]: put(fx["tick"], s["start"] + tc, .25)
    sf.write(f"{OUT}/voice.wav", v, sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/voice.wav", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000", f"{OUT}/voice_n.wav"], check=True)
    vn, _ = sf.read(f"{OUT}/voice_n.wav", dtype="float32"); n = min(len(vn), len(mus))
    vr = np.sqrt(np.mean(vn[:n][speech[:n]] ** 2)); mr = np.sqrt(np.mean(mus[:n][speech[:n]] ** 2)) + 1e-9
    bed = (mus[:n] * (vr / mr) * 10 ** (-23 / 20)) + fxt[:n] * (vr / mr) * 10 ** (-23 / 20) * 3
    sf.write(f"{OUT}/mix.wav", vn[:n] + bed, sr)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f"{OUT}/mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/mix.wav", "-af", af, "-ar", "48000", f"{OUT}/final.wav"], check=True)


def render(total):
    from playwright.sync_api import sync_playwright
    tl = {"segments": [{k: v for k, v in s.items() if k != "audio"} for s in segs]}
    json.dump(tl, open(f"{OUT}/timeline.json", "w"), indent=1)
    nf = int(round(total * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-r", str(FPS), f"{OUT}/silent.mp4"], stdin=subprocess.PIPE)
    qa = {0}
    for s in segs:
        if s["kind"] == "item":
            c = s["cues"]; qa |= {int((s["start"] + c["why"] - .3) * FPS), int((s["start"] + c["catch"] - .2) * FPS), int((s["start"] + c["tags"][-1] + .6) * FPS), int((s["start"] + s["dur"] - .2) * FPS)}
        else:
            qa |= {int((s["start"] + s["dur"] * .4) * FPS), int((s["start"] + s["dur"] - .1) * FPS)}
    with sync_playwright() as p:
        exe = os.environ.get("CHROME")
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.join(HERE, "deal.html")); info = pg.evaluate("tl => window.setup(tl)", tl); print("setup", info)
        assert not info["bad"] and info["fonts"] >= 4, info
        for f in range(nf):
            pg.evaluate(f"window.render({f / FPS:.4f})"); jpg = pg.screenshot(type="jpeg", quality=93); ff.stdin.write(jpg)
            if f in qa: open(f"{OUT}/frames/{f:05d}.jpg", "wb").write(jpg)
            if f == 0: open(f"{OUT}/cover.jpg", "wb").write(pg.screenshot(type="jpeg", quality=95))
        b.close()
    ff.stdin.close(); ff.wait()


def captions():
    def ts(x): h, r = divmod(x, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    lines, n = [], 1
    for s in segs:
        cur = []
        for w in s["words"]:
            cur.append(w)
            if re.search(r"[.?!:]$", w["w"]) or (len(cur) >= 6 and w["w"].endswith(",")) or len(cur) >= 10:
                lines.append(f"{n}\n{ts(s['start'] + cur[0]['s'])} --> {ts(s['start'] + cur[-1]['e'])}\n{' '.join(x.get('cap', x['w']) for x in cur)}\n"); n += 1; cur = []
        if cur: lines.append(f"{n}\n{ts(s['start'] + cur[0]['s'])} --> {ts(s['start'] + cur[-1]['e'])}\n{' '.join(x.get('cap', x['w']) for x in cur)}\n"); n += 1
    open(f"{OUT}/captions.srt", "w").write("\n".join(lines))


tts(); total = timeline(); print("total", round(total, 2)); audio(total); render(total); captions()
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/silent.mp4", "-i", f"{OUT}/final.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", f"{OUT}/video.mp4"], check=True)
print("done", OUT)
