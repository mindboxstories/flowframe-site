"""Guide video v2: motion-graphics roundup (no page capture).
Usage: python _video/v2/make2.py _video/<slug>/v2.json [--preview]   (GitHub Actions: .github/workflows/video2.yml)
1) Kokoro TTS per segment, with word timings  2) timeline + cues  3) original music + SFX, ducked under the voice
4) scenes.html rendered frame by frame (Playwright) -> ffmpeg  5) loudness pass, captions, chapters, QA frames
Outputs: _video/out/<slug>-v2/{video.mp4,captions.srt,chapters.txt,timeline.json,frames/}"""
import json, os, sys, subprocess, math, re
import numpy as np

FPS, W, H, SR = 30, 1920, 1080, 24000
HERE = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(sys.argv[1]))
PREVIEW = "--preview" in sys.argv          # fake voice timings, short render, for layout checks without TTS
# --short <item id>: vertical 1080x1920 Short/Reel/TikTok for one pick, built from the same v2.json ("shorts" list)
SHORT = sys.argv[sys.argv.index("--short") + 1] if "--short" in sys.argv else None
# --stack <stack id>: vertical multi-pick Short (5 or so picks, ~45 s) from the v2.json "stacks" list:
# emotional hook (who it's for) -> quick picks (name, price, the feeling, a one-line catch) -> share + profile CTA
STACK = sys.argv[sys.argv.index("--stack") + 1] if "--stack" in sys.argv else None
SCENES = "scenes.html"


def build_short(base, sid):
    """hook (one line + price) -> the pick (number word dropped) -> CTA to the full list on our profile."""
    cfg = next(x for x in base["shorts"] if x["id"] == sid)
    items = [s for s in base["segments"] if s["kind"] == "item"]
    it = dict(next(s for s in items if s["id"] == sid))
    it["text"] = re.sub(r"^(And )?(Number )?[A-Za-z-]+\.\s+", "", it["text"])
    it["of"] = len(items)
    labels = ["The catch", "Heads-up", "Good to know", "Before you buy", "The trade-off", "Worth knowing", "The only snag", "Fair warning"]
    it.setdefault("cue", labels[(it["n"] - 1) % len(labels)])
    hook = {"id": "shook", "kind": "shook", "text": cfg["hook"], "title": cfg["title"], "img": it["img"], "price": it["price"],
            "kicker": f"{it['n']} of {len(items)} · {base['short_label']}"}
    flash = next((s.get("flash") for s in base["segments"] if s["kind"] == "hook"), []) or [x["img"] for x in items]
    imgs = [it["img"]] + [u for u in flash if u != it["img"]][:2]
    cta = {"id": "scta", "kind": "scta", "text": base["short_cta"], "imgs": imgs, "kicker": f"{len(items)} {base['short_label']}", "hold": 1.2}
    out = {k: v for k, v in base.items() if k not in ("segments", "chapters", "thumb", "shorts")}
    out["slug"] = f"{base['slug']}-short-{sid}"; out["format"] = "short"; out["segments"] = [hook, it, cta]
    return out


def build_stack(base, sid):
    cfg = next(x for x in base["stacks"] if x["id"] == sid)
    items = {s["id"]: s for s in base["segments"] if s["kind"] == "item"}
    picks = []
    for i, p in enumerate(cfg["picks"], 1):
        it = items[p["id"]]
        picks.append({"id": p["id"], "kind": "qitem", "n": i, "of": len(cfg["picks"]), "name": p.get("name", it["name"]),
                      "price": p.get("price", it["price"]), "img": p.get("img", it["img"]), "text": p["text"],
                      "feel": p["feel"], "catch": p["catch"], **({"cue": p["cue"]} if "cue" in p else {}),
                      **({"small": p.get("small", it.get("small"))} if p.get("small", it.get("small")) else {})})
    hook = {"id": "shook", "kind": "shook", "text": cfg["hook"], "title": cfg["title"], "img": cfg.get("img", picks[0]["img"]),
            "price": "", "accent_color": cfg.get("accent_color", "sun"), "sticker": cfg.get("sticker", {"small": "picks", "big": str(len(picks))}), "kicker": cfg["kicker"]}
    cta = {"id": "scta", "kind": "scta", "text": cfg["cta"], "imgs": [x["img"] for x in picks[:3]], "kicker": cfg.get("cta_kicker", base.get("short_label", "")),
           "share": cfg.get("share", "Send this to someone who'd love one"), "hold": 1.2}
    out = {k: v for k, v in base.items() if k not in ("segments", "chapters", "thumb", "shorts", "stacks")}
    out["slug"] = f"{base['slug']}-stack-{sid}"; out["format"] = "short"; out["segments"] = [hook] + picks + [cta]
    return out


if SHORT:
    spec = build_short(spec, SHORT); W, H = 1080, 1920; SCENES = "shorts.html"
if STACK:
    spec = build_stack(spec, STACK); W, H = 1080, 1920; SCENES = "shorts.html"; SHORT = STACK
OUT = os.path.join(HERE, "..", "out", spec["slug"] + ("" if SHORT else "-v2"))
os.makedirs(f"{OUT}/frames", exist_ok=True)
segs = spec["segments"]
# Varied "catch" lead-ins (Jarvis, 16 Nov: vary it so it isn't monotonous). Scripts write "The catch?";
# the pipeline swaps it per pick: (spoken lead-in, on-screen label, icon, accent colour). An item can set "cue" to pin one.
CUES = [("The catch?", "The catch", "!", "coral"), ("Heads-up:", "Heads-up", "!", "sun"),
        ("One thing to know:", "Good to know", "i", "coral"), ("Before you buy:", "Before you buy", "✓", "sun"),
        ("The trade-off?", "The trade-off", "⇄", "coral"), ("Worth knowing:", "Worth knowing", "i", "sun"),
        ("The only snag?", "The only snag", "!", "coral"), ("Fair warning:", "Fair warning", "!", "sun")]


def vary_cues():
    k = 0
    for s in segs:
        if s["kind"] not in ("item", "qitem"):
            continue
        pick = next((c for c in CUES if c[1].lower() == s.get("cue", "").lower()), CUES[k % len(CUES)])
        s["text"] = re.sub(r"The catch\?", pick[0], s["text"], count=1)
        s["cue_words"] = pick[0].rstrip("?:").split()
        s["cue_label"], s["cue_icon"], s["cue_color"] = pick[1], pick[2], pick[3]
        k += 1


PAD = {"qitem": .18, "shook": .2, "scta": 0, "hook": .25, "note": .25, "band": .22, "item": .28, "rehook": .3, "recap": .4, "outro": 0}


# ---------- 1. voice ----------
def tts():
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="a")
    for s in segs:
        audio, words, t = [], [], 0.0
        say = re.sub(r"\bcatch\b", "[catch](/kˈæʧ/)", s["text"])
        for r in pipe(say, voice=spec["voice"], speed=spec["speed"], split_pattern=r"(?<=[.?!:])\s+"):
            a = r.audio.numpy() if hasattr(r.audio, "numpy") else np.asarray(r.audio)
            toks = getattr(r, "tokens", None) or []
            got = False
            for tk in toks:
                if tk.start_ts is None or not re.search(r"\w", tk.text):
                    continue
                words.append({"w": tk.text, "s": round(t + tk.start_ts, 3), "e": round(t + (tk.end_ts or tk.start_ts + .2), 3)}); got = True
            if not got:   # fallback: spread words by length
                ws = r.graphemes.split(); tot = sum(len(x) for x in ws) or 1; c = t
                for x in ws:
                    d = len(a) / SR * len(x) / tot; words.append({"w": x, "s": round(c, 3), "e": round(c + d, 3)}); c += d
            audio.append(a); t += len(a) / SR
        a = np.concatenate(audio).astype(np.float32)
        # trim leading/trailing silence (keep 40 ms), shift word times to match
        env = np.abs(a) > 10 ** (-45 / 20)
        i0 = max(0, int(np.argmax(env)) - int(.04 * SR)); i1 = min(len(a), len(a) - int(np.argmax(env[::-1])) + int(.06 * SR))
        a = a[i0:i1]; off = i0 / SR
        for w in words: w["s"] = round(max(0, w["s"] - off), 3); w["e"] = round(max(0, w["e"] - off), 3)
        s["audio"], s["speech"], s["words"] = a, len(a) / SR, words
        print(f"tts {s['id']}: {s['speech']:.2f}s, {len(words)} words")


def fake_tts():
    for s in segs:
        ws = s["text"].split(); t = 0.0; s["words"] = []
        for w in ws:
            d = .08 + .055 * len(w); s["words"].append({"w": re.sub(r"[^\w'$-]", "", w), "s": round(t, 3), "e": round(t + d, 3)}); t += d + .04
        s["speech"] = t; s["audio"] = np.zeros(int(t * SR), np.float32)


# ---------- 2. timeline ----------
def first(s, pat, after=0.0):
    for w in s["words"]:
        if w["s"] >= after and re.search(pat, w["w"], re.I):
            return w["s"]
    return None


def timeline():
    t = 0.0
    for s in segs:
        s["start"] = round(t, 3)
        s["dur"] = round(s["speech"] + PAD[s["kind"]] + (s.get("hold", 0)), 3)
        s["dur"] = round(round(s["dur"] * FPS) / FPS, 4)
        if s["kind"] in ("item", "qitem"):
            price = first(s, r"dollars|^\$") or 1.6
            # the "why" starts at the sentence after the price sentence; the catch starts at "The" before "catch"
            ws = s["words"]; cw = [re.sub(r"\W", "", x).lower() for x in s.get("cue_words", ["The", "catch"])]
            ci = next((i for i in range(len(ws)) if [re.sub(r"\W", "", w["w"]).lower() for w in ws[i:i + len(cw)]] == cw), len(ws) - 6)
            catch = ws[ci]["s"] - .1
            pi = next((i for i, w in enumerate(ws) if w["s"] >= price), 0)
            why = ws[min(pi + 1, ci - 1)]["s"] - .05
            s["cues"] = {"price": round(max(.5, price - .05), 3), "why": round(min(max(price + (1.5 if SHORT else .6), why), catch - 1.5), 3), "catch": round(catch, 3)}
        sp = s["text"].split(); ws = s["words"]
        idx = [min(len(ws) - 1, int(i * len(ws) / len(sp))) for i in range(len(sp))] if len(sp) != len(ws) else list(range(len(sp)))
        s["cap"] = [{"w": sp[i], "s": ws[j]["s"], "e": ws[j]["e"]} for i, j in enumerate(idx)] if ws else []
        t += s["dur"]
    return t


# ---------- 3. audio ----------
def synth_music(total):
    """Original light groove, 112 bpm, Cmaj9-Am9-Fmaj7-G6. Fully generated here, so no licence questions."""
    sr, bpm = 48000, 112.0
    beat = 60 / bpm; n = int((total + 1) * sr); mus = np.zeros(n, np.float32); rng = np.random.default_rng(7)
    def add(x, t0, g=1.0):
        i = int(t0 * sr); j = min(n, i + len(x))
        if i < n: mus[i:j] += g * x[:j - i]
    def env(d, a=.004, dec=.25):
        tt = np.arange(int(d * sr)) / sr; return np.minimum(1, tt / a) * np.exp(-tt / dec)
    def tone(f, d, dec, harm=(1, .35, .12)):
        tt = np.arange(int(d * sr)) / sr
        return sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm)) * env(d, .003, dec)
    def lp(x, a=.15):
        y = np.empty_like(x); acc = 0.0
        for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
        return y
    kick = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-np.arange(int(.3 * sr)) / sr / .03)) / sr) * env(.3, .001, .12)
    noise = rng.standard_normal(int(.25 * sr)).astype(np.float32)
    hat = np.diff(noise[: int(.05 * sr)], prepend=0) * env(.05, .0005, .012)
    clap = lp(noise[: int(.2 * sr)], .5) - lp(noise[: int(.2 * sr)], .05); clap *= env(.2, .001, .05)
    mid = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[60, 64, 67, 71, 74], [57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [55, 59, 62, 64, 67]]
    roots = [36, 33, 29, 31]
    bar = 4 * beat; nb = int(total / bar) + 2
    for b in range(nb):
        t0 = b * bar; ch = chords[b % 4]
        for k in range(8):   # plucked arpeggio on eighths, slight swing
            tt = t0 + k * beat / 2 + (.025 if k % 2 else 0)
            add(tone(mid(ch[[0, 2, 4, 3, 1, 2, 4, 3][k]] + 12), .4, .18), tt, .11)
        add(tone(mid(ch[0]), 1.6, .9, (1, .2)) + tone(mid(ch[2]), 1.6, .9, (1, .2)) + tone(mid(ch[3]), 1.6, .9, (1, .2)), t0, .045)   # soft chord bed
        for q in range(4):
            tq = t0 + q * beat
            add(tone(mid(roots[b % 4]), beat * .95, .3, (1, .25)), tq, .32)
            if q in (0, 2): add(kick, tq, .55)
            if q == 3 and b % 2: add(kick, tq + beat / 2, .35)
            if q in (1, 3): add(clap, tq, .22)
            add(hat, tq + beat / 2 + .02, .2); add(hat, tq, .09)
    mus = np.tanh(mus * 1.3) * .8
    return mus[: int(total * sr)], sr


def sfx(sr):
    rng = np.random.default_rng(3)
    d = .42; tt = np.arange(int(d * sr)) / sr
    nz = rng.standard_normal(len(tt)).astype(np.float32)
    # whoosh: noise through a sweeping resonant band
    out = np.zeros_like(nz); y1 = y2 = 0.0
    for i in range(len(nz)):
        f = 300 + 3500 * (i / len(nz)) ** 1.5; w = 2 * math.pi * f / sr; r = .97
        y = nz[i] * (1 - r) + 2 * r * math.cos(w) * y1 - r * r * y2; y2, y1 = y1, y; out[i] = y
    whoosh = out / (np.abs(out).max() + 1e-9) * np.sin(np.pi * tt / d) ** 2
    pt = np.arange(int(.16 * sr)) / sr
    pop = np.sin(2 * np.pi * np.cumsum(900 * np.exp(-pt / .03) + 220) / sr) * np.exp(-pt / .045)
    kt = np.arange(int(.09 * sr)) / sr
    tick = (np.sin(2 * np.pi * 1800 * kt) + .5 * np.sin(2 * np.pi * 2700 * kt)) * np.exp(-kt / .015)
    return {"whoosh": whoosh.astype(np.float32), "pop": pop.astype(np.float32), "tick": tick.astype(np.float32)}


def audio(total):
    import soundfile as sf
    sr = 48000
    # voice stem at 48 kHz
    v = np.zeros(int(total * sr) + sr, np.float32)
    speech = np.zeros_like(v, dtype=bool)
    for s in segs:
        a = s["audio"]
        if len(a):
            a48 = np.interp(np.arange(int(len(a) * sr / SR)) / sr, np.arange(len(a)) / SR, a).astype(np.float32)
            i = int(s["start"] * sr); v[i:i + len(a48)] += a48[: len(v) - i]
            for w in s["words"]:
                speech[int((s["start"] + w["s"] - .15) * sr): int((s["start"] + w["e"] + .25) * sr)] = True
    v = v[: int(total * sr)]; speech = speech[: len(v)]
    mus, _ = synth_music(total)
    # duck: music low under speech, up in gaps / band cards / end card (smoothed 120 ms)
    g = np.where(speech, .16, .55).astype(np.float32)
    k = int(.12 * sr); g = np.convolve(g, np.ones(k) / k, mode="same")
    mus = mus[: len(v)] * g
    fx = sfx(sr); fxt = np.zeros_like(v)
    def put(x, t0, gain):
        i = int(t0 * sr); j = min(len(fxt), i + len(x))
        if 0 <= i < len(fxt): fxt[i:j] += gain * x[: j - i]
    for s in segs:
        if s["start"] > 0: put(fx["whoosh"], s["start"] - .21, .32)
        if s["kind"] in ("item", "qitem"):
            c = s["cues"]; put(fx["pop"], s["start"] + c["price"], .5); put(fx["whoosh"], s["start"] + c["why"] - .05, .16); put(fx["tick"], s["start"] + c["catch"], .45)
        if s["kind"] == "hook":
            for i in range(len(s["flash"])): put(fx["tick"], s["start"] + i * .16, .3)
            p = first(s, (s.get("sticker") or {}).get("cue", r"^sixty")); put(fx["pop"], s["start"] + (p or 2.2), .5)
        if s["kind"] == "shook": put(fx["pop"], s["start"] + .45, .5)
    sf.write(f"{OUT}/voice.wav", v, sr); sf.write(f"{OUT}/bed.wav", mus + fxt, sr)
    # level voice alone to -16 LUFS, bed relative to it, then mix and do the final -14 LUFS pass
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/voice.wav", "-af", "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", "48000", f"{OUT}/voice_n.wav"], check=True)
    vn, _ = sf.read(f"{OUT}/voice_n.wav", dtype="float32")
    bed = (mus + fxt)[: len(vn)]
    vr = np.sqrt(np.mean(vn[speech[: len(vn)]] ** 2)); mr = np.sqrt(np.mean(mus[: len(vn)][speech[: len(vn)]] ** 2)) + 1e-9
    bed *= (vr / mr) * 10 ** (-23 / 20)      # music sits 23 dB under the voice while she speaks
    sf.write(f"{OUT}/mix.wav", vn + bed[: len(vn)], sr)
    # two-pass loudnorm (linear) so the file lands on -14 LUFS exactly
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f"{OUT}/mix.wav", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/mix.wav", "-af", af, "-ar", "48000", f"{OUT}/final.wav"], check=True)


# ---------- 4. frames ----------
def render(total, limit=None):
    from playwright.sync_api import sync_playwright
    tl = {"guide": spec["guide"], "segments": [{k: v for k, v in s.items() if k != "audio"} for s in segs]}
    json.dump(tl, open(f"{OUT}/timeline.json", "w"), indent=1)
    nf = int(round(total * FPS)) if limit is None else int(limit * FPS)
    exe = os.environ.get("CHROME")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p", "-r", str(FPS), f"{OUT}/silent.mp4"], stdin=subprocess.PIPE)
    qa = set()
    for s in segs:
        if s["kind"] in ("item", "qitem"):
            c = s["cues"]; qa |= {int((s["start"] + c["price"] + .8) * FPS), int((s["start"] + (c["why"] + c["catch"]) / 2 + .3) * FPS), int((s["start"] + s["dur"] - .25) * FPS)}
        else:
            qa.add(int((s["start"] + s["dur"] * .7) * FPS))
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + os.path.join(HERE, SCENES), wait_until="networkidle")
        n = pg.evaluate("tl => window.setup(tl)", tl); print("images", n)
        for f in range(nf):
            pg.evaluate(f"window.render({f / FPS:.4f})")
            jpg = pg.screenshot(type="jpeg", quality=95)
            ff.stdin.write(jpg)
            if f in qa:
                open(f"{OUT}/frames/{f:05d}.jpg", "wb").write(jpg)
            if f % 600 == 0: print("frame", f, "/", nf, flush=True)
        b.close()
    ff.stdin.close(); ff.wait()


def mux():
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{OUT}/silent.mp4", "-i", f"{OUT}/final.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", f"{OUT}/video.mp4"], check=True)


def captions_and_chapters():
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s_, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s_:02d},{ms:03d}"
    # caption cues from the spoken text (not the token text) so spelling matches the script
    cues = []
    for s in segs:
        ws = s["words"]; spoken = s["text"].split()
        if len(spoken) == len(ws):
            pairs = list(zip(spoken, ws))
        else:   # token count differs (numbers, hyphens): map proportionally
            pairs = [(spoken[i], ws[min(len(ws) - 1, int(i * len(ws) / len(spoken)))]) for i in range(len(spoken))]
        cur = []
        for txt, w in pairs:
            cur.append((txt, w))
            if len(cur) >= 7 or re.search(r"[.?!:]$", txt) or (len(cur) >= 4 and txt.endswith(",")):
                cues.append((s["start"] + cur[0][1]["s"], s["start"] + cur[-1][1]["e"] + .15, " ".join(x for x, _ in cur))); cur = []
        if cur: cues.append((s["start"] + cur[0][1]["s"], s["start"] + cur[-1][1]["e"] + .15, " ".join(x for x, _ in cur)))
    with open(f"{OUT}/captions.srt", "w") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            b = min(b, cues[i][0] - .01) if i < len(cues) else b
            f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
    if "chapters" not in spec:
        return
    names = spec["chapters"]; out, prev_band = [], None
    for s in segs:
        st = s["start"]
        if s["kind"] == "band": prev_band = st; continue
        if s["id"] in names:
            if prev_band is not None: st = prev_band
            out.append((st, names[s["id"]]))
        prev_band = None
    out[0] = (0.0, out[0][1])
    with open(f"{OUT}/chapters.txt", "w") as f:
        for st, nm in out:
            m, s_ = divmod(int(st), 60); f.write(f"{m}:{s_:02d} {nm}\n")


def thumb():
    """Render the 1280x720 thumbnail from spec["thumb"] (Finds design: headline + italic accent, 3 tilted photo cards, coral sticker)."""
    t = spec.get("thumb")
    if not t:
        return
    from playwright.sync_api import sync_playwright
    exe = os.environ.get("CHROME")
    with sync_playwright() as p:
        b = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto("file://" + os.path.join(HERE, "thumb.html"), wait_until="networkidle")
        pg.evaluate("t => window.setThumb(t)", t); pg.wait_for_timeout(500)
        pg.screenshot(path=f"{OUT}/thumb.jpg", type="jpeg", quality=92)
        b.close()


if __name__ == "__main__":
    vary_cues()
    (fake_tts if PREVIEW else tts)()
    total = timeline(); print(f"total {total:.1f}s")
    if PREVIEW:
        render(total, limit=float(os.environ.get("PREVIEW_SECONDS", "6"))); captions_and_chapters()
    else:
        audio(total); render(total); mux(); captions_and_chapters(); thumb()
        print("done", os.path.getsize(f"{OUT}/video.mp4") // 1_000_000, "MB")
