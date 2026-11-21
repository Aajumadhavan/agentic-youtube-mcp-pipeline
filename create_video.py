import asyncio, edge_tts, subprocess, sys, os, re, html, urllib.parse, requests

PROJECT_DIR = r"C:\AI_MCP_Server"
os.chdir(PROJECT_DIR)

if len(sys.argv) < 3:
    print("Usage: create_video.py <topic> <script>")
    sys.exit(1)

topic = sys.argv[1].strip()
script = sys.argv[2].strip()
VOICE_NAME = "ta-IN-PallaviNeural"

EDGE_PATHS = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)
EDGE_EXE = next((p for p in EDGE_PATHS if os.path.exists(p)), None)

def get_audio_duration(audio_path):
    res = subprocess.run(
        ("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path),
        capture_output=True, text=True, check=True
    )
    return float(res.stdout.strip())

def get_particular_visual_prompt(tamil_sentence, fallback_topic, scene_idx):
    """Map Tamil keywords in each sentence to an exact, hyper-specific cinematic visual description."""
    s = tamil_sentence.lower()
    keyword_map = (
        (("வெள்ளி", "venus"), "glowing golden planet Venus covered in swirling volcanic clouds in deep space, NASA cinematic 8k"),
        (("சூரிய", "sun"), "massive blazing solar flare on the surface of the Sun, glowing plasma loops, 8k space photography"),
        (("நியூட்ரான்", "neutron"), "intense glowing blue pulsar neutron star shooting twin magnetic energy beams in dark cosmos, 8k"),
        (("செவ்வாய்", "mars"), "alien blue sunset over red rocky mountains of planet Mars, dusty horizon, cinematic sci-fi 8k"),
        (("நிலா", "moon", "கால்"), "close up of astronaut boot footprint in grey lunar dust with Earth glowing in dark sky, 8k"),
        (("கடல்", "ocean", "ஆழ"), "bioluminescent glowing deep ocean trench underwater rays of light, National Geographic 8k"),
        (("ஆக்டோபஸ்", "octopus"), "majestic glowing bioluminescent octopus swimming in deep dark blue ocean, ultra detailed 8k"),
        (("பூமி", "earth"), "planet Earth from orbit at night with glowing golden city lights and aurora borealis, 8k"),
        (("விண்வெளி", "space", "வெடிப்பு"), "colorful cosmic nebula supernova explosion with glowing stardust and galaxies, James Webb 8k"),
        (("மூளை", "brain", "தூக்க"), "glowing neural network synapses firing electric blue light inside human brain hologram, 8k"),
    )
    for keys, visual_desc in keyword_map:
        for k in keys:
            if k in s:
                return visual_desc
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', fallback_topic).strip() or "mysterious cosmos science"
    angles = (
        f"dramatic cinematic 3d visualization of {clean_topic}, volumetric god rays, dark moody background, 8k",
        f"ultra detailed macro close-up concept of {clean_topic}, glowing neon rim light, photorealistic 8k",
        f"epic futuristic holographic projection of {clean_topic}, floating particles, deep contrast, 8k"
    )
    return angles[scene_idx % len(angles)]

def download_ai_scene_image(tamil_sentence, fallback_topic, scene_idx, out_path):
    specific_subject = get_particular_visual_prompt(tamil_sentence, fallback_topic, scene_idx)
    prompt = f"{specific_subject}, vertical 9:16 composition, centered subject, no text, no watermark, no letters"
    url = f"https://pollinations.ai{urllib.parse.quote(prompt)}?width=1080&height=1920&seed={500 + scene_idx * 73}&nologo=true"
    try:
        resp = requests.get(url, timeout=45)
        if resp.status_code == 200 and len(resp.content) > 15000:
            with open(out_path, "wb") as f:
                f.write(resp.content)
            return True
    except Exception as e:
        print(f"Image fetch warning: {e}")
    return False
def render_html_frame(bg_image_path, topic_text, sentence_text, scene_idx, total_scenes, out_png):
    safe_topic = html.escape(topic_text if len(topic_text) <= 32 else topic_text[:29] + "...")
    safe_sentence = html.escape(sentence_text)
    progress_pct = int(((scene_idx + 1) / total_scenes) * 100)
    scene_num = f"{scene_idx + 1:02d}"
    accents = (("#facc15", "#f97316"), ("#38bdf8", "#6366f1"), ("#10b981", "#06b6d4"), ("#f43f5e", "#a855f7"), ("#fb923c", "#eab308"))
    c1, c2 = accents[scene_idx % len(accents)]
    if bg_image_path and os.path.exists(bg_image_path):
        abs_bg = os.path.abspath(bg_image_path).replace("\\", "/")
        bg_css = f"background-image: url('file:///{abs_bg}'); background-size: cover; background-position: center;"
    else:
        bg_css = "background: radial-gradient(circle at 50% 35%, #1e1b4b 0%, #050814 100%);"

    rot_deg = scene_idx * 37
    bars = (26, 58, 34, 74, 48, 82, 38, 66, 30, 72, 50, 32, 60, 40)
    shift = (scene_idx * 3) % len(bars)
    eq_html = "".join(f'<div class="eq-bar" style="height:{bars[(i+shift)%len(bars)]}px; background: linear-gradient(180deg, {c1}, {c2});"></div>' for i in range(len(bars)))

    html_str = f"""<!DOCTYPE html><html lang="ta"><head><meta charset="UTF-8"><style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ width: 1080px; height: 1920px; overflow: hidden; font-family: 'Nirmala UI', sans-serif; {bg_css} position: relative; color: #fff; }}
    .vignette {{ position: absolute; inset: 0; background: radial-gradient(circle at 50% 42%, rgba(0,0,0,0.12) 0%, rgba(4,7,18,0.88) 85%), linear-gradient(180deg, rgba(4,7,18,0.82) 0%, rgba(4,7,18,0.15) 38%, rgba(4,7,18,0.75) 72%, rgba(4,7,18,0.96) 100%); }}
    .hud-outer {{ position: absolute; top: 34%; left: 50%; width: 760px; height: 760px; transform: translate(-50%,-50%) rotate({rot_deg}deg); border-radius: 50%; border: 3px dashed {c1}55; z-index: 2; }}
    .hud-inner {{ position: absolute; top: 34%; left: 50%; width: 620px; height: 620px; transform: translate(-50%,-50%) rotate(-{rot_deg * 2}deg); border-radius: 50%; border: 2px solid {c2}66; box-shadow: 0 0 80px {c1}33; z-index: 2; }}
    .corner-tl, .corner-tr, .corner-bl, .corner-br {{ position: absolute; width: 70px; height: 70px; border-color: {c1}; border-style: solid; z-index: 3; opacity: 0.85; }}
    .corner-tl {{ top: 55px; left: 45px; border-width: 5px 0 0 5px; border-radius: 16px 0 0 0; }}
    .corner-tr {{ top: 55px; right: 45px; border-width: 5px 5px 0 0; border-radius: 0 16px 0 0; }}
    .corner-bl {{ bottom: 55px; left: 45px; border-width: 0 0 5px 5px; border-radius: 0 0 0 16px; }}
    .corner-br {{ bottom: 55px; right: 45px; border-width: 0 5px 5px 0; border-radius: 0 0 16px 0; }}
    .top {{ position: absolute; top: 88px; left: 60px; right: 60px; display: flex; flex-direction: column; align-items: center; gap: 16px; z-index: 4; }}
    .badge {{ background: rgba(8,12,26,0.88); border: 3px solid {c1}; color: {c1}; padding: 14px 38px; border-radius: 50px; font-size: 34px; font-weight: 800; letter-spacing: 0.5px; box-shadow: 0 10px 30px rgba(0,0,0,0.7); }}
    .num-wrap {{ display: flex; align-items: center; gap: 16px; margin-top: 8px; }}
    .num {{ padding: 12px 32px; border-radius: 22px; background: linear-gradient(135deg, {c1}, {c2}); color: #050814; font-size: 44px; font-weight: 900; box-shadow: 0 10px 25px rgba(0,0,0,0.75); border: 3px solid #fff; }}
    .cap-zone {{ position: absolute; bottom: 275px; left: 55px; right: 55px; z-index: 4; text-align: center; }}
    .cap-box {{ background: rgba(6, 10, 22, 0.78); border: 2px solid rgba(255,255,255,0.18); border-left: 10px solid {c1}; border-right: 10px solid {c2}; border-radius: 34px; padding: 44px 38px; box-shadow: 0 25px 60px rgba(0,0,0,0.85); }}
    .cap-txt {{ font-size: 58px; font-weight: 800; line-height: 1.46; text-shadow: 0 4px 16px rgba(0,0,0,0.98), 2px 2px 0 #000; }}
    .eq {{ display: flex; align-items: flex-end; justify-content: center; gap: 10px; height: 64px; margin-top: 26px; }}
    .eq-bar {{ width: 11px; border-radius: 8px; }}
    .bot {{ position: absolute; bottom: 115px; left: 85px; right: 85px; z-index: 4; text-align: center; }}
    .track {{ width: 100%; height: 14px; background: rgba(255,255,255,0.22); border-radius: 10px; overflow: hidden; margin-bottom: 20px; }}
    .fill {{ width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, {c1}, {c2}); border-radius: 10px; }}
    .cta {{ display: inline-block; background: linear-gradient(90deg, {c1}22, {c2}22); border: 2px solid {c1}88; padding: 10px 30px; border-radius: 30px; font-size: 32px; font-weight: 700; color: #fff; }}
    </style></head><body>
    <div class="vignette"></div>
    <div class="hud-outer"></div><div class="hud-inner"></div>
    <div class="corner-tl"></div><div class="corner-tr"></div><div class="corner-bl"></div><div class="corner-br"></div>
    <div class="top"><div class="badge">{safe_topic}</div><div class="num-wrap"><div class="num">FACT #{scene_num}</div></div></div>
    <div class="cap-zone"><div class="cap-box"><div class="cap-txt">{safe_sentence}</div><div class="eq">{eq_html}</div></div></div>
    <div class="bot"><div class="track"><div class="fill"></div></div><div class="cta">Subscribe &amp; Like for Daily Tamil Facts!</div></div>
    </body></html>"""
    html_file = os.path.abspath(f"temp_scene_{scene_idx}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_str)
    subprocess.run((EDGE_EXE, "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={os.path.abspath(out_png)}", "--window-size=1080,1920", f"file:///{html_file.replace(os.sep, '/')}"), check=True)
    if os.path.exists(html_file):
        os.remove(html_file)

async def create_voice():
    await edge_tts.Communicate(script, VOICE_NAME, rate="+5%", pitch="+1Hz").save("voice.mp3")

asyncio.run(create_voice())
total_duration = get_audio_duration("voice.mp3")
raw = [s.strip() for s in re.split(r'[.!?।\n]+', script) if s.strip()] or [script]
scenes = []
for s in raw:
    if scenes and len(scenes[-1]) < 35:
        scenes[-1] = f"{scenes[-1]}. {s}"
    else:
        scenes.append(s)
while len(scenes) > 8:
    scenes[-2] = f"{scenes[-2]}. {scenes[-1]}"
    scenes.pop()

clip_files = []
total_chars = sum(len(s) for s in scenes)
fade_dur = 0.40
for idx, sentence in enumerate(scenes):
    bg_file, frame_file, clip_file = f"ai_bg_{idx}.jpg", f"frame_{idx}.png", f"clip_{idx}.mp4"
    has_bg = download_ai_scene_image(sentence, topic, idx, bg_file)
    render_html_frame(bg_file if has_bg else None, topic, sentence, idx, len(scenes), frame_file)
    base_dur = max(2.6, (len(sentence) / max(total_chars, 1)) * total_duration)
    scene_dur = base_dur + (fade_dur if idx < len(scenes) - 1 else 0.25)
    frames = int(scene_dur * 30)
    m = idx % 4
    if m == 0:
        vf = f"scale=1280:2276,zoompan=z='min(zoom+0.0014,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    elif m == 1:
        vf = f"scale=1280:2276,zoompan=z='if(eq(on,1),1.18,max(zoom-0.0014,1.00))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    elif m == 2:
        vf = f"scale=1280:2276,zoompan=z=1.14:x='(iw-iw/zoom)*(on/{max(frames,1)})':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    else:
        vf = f"scale=1280:2276,zoompan=z=1.14:x='(iw-iw/zoom)*(1-on/{max(frames,1)})':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=30"
    subprocess.run(("ffmpeg", "-y", "-loop", "1", "-i", frame_file, "-vf", vf, "-t", f"{scene_dur:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", clip_file), check=True)
    clip_files.append((clip_file, scene_dur))

if len(clip_files) == 1:
    os.replace(clip_files[0][0], "merged_video.mp4")
else:
    inputs = []
    for cf, _ in clip_files:
        inputs.extend(("-i", cf))
    parts = []
    offset = clip_files[0][1] - fade_dur
    prev = "[0:v]"
    transitions = ("zoomin", "wipeleft", "smoothup", "circleopen", "fade")
    for i in range(1, len(clip_files)):
        out = f"[v{i}]" if i < len(clip_files) - 1 else "[vout]"
        tr = transitions[i % len(transitions)]
        parts.append(f"{prev}[{i}:v]xfade=transition={tr}:duration={fade_dur}:offset={offset:.2f}{out}")
        prev = out
        offset += clip_files[i][1] - fade_dur
    subprocess.run(("ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", "[vout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "merged_video.mp4"), check=True)

subprocess.run(("ffmpeg", "-y", "-i", "merged_video.mp4", "-i", "voice.mp3", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "Tamil_Shorts.mp4"), check=True)
for idx in range(len(scenes)):
    for temp in (f"ai_bg_{idx}.jpg", f"frame_{idx}.png", f"clip_{idx}.mp4"):
        if os.path.exists(temp):
            os.remove(temp)
if os.path.exists("merged_video.mp4"):
    os.remove("merged_video.mp4")
print("SUCCESS! Viral v5 Motion-Graphics Tamil Shorts created!")
