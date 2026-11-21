import asyncio
import edge_tts
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

# Receive topic and script from Claude
topic = sys.argv[1]
script = sys.argv[2]

async def create_voice():
    voice = edge_tts.Communicate(
        script,
        "ta-IN-ValluvarNeural"
    )
    await voice.save("voice.mp3")

asyncio.run(create_voice())

# Create vertical background
img = Image.new("RGB", (1080, 1920), (15, 20, 55))
draw = ImageDraw.Draw(img)

font_path = r"C:\Windows\Fonts\Nirmala.ttc"

title_font = ImageFont.truetype(font_path, 85)
small_font = ImageFont.truetype(font_path, 48)

draw.text(
    (540, 700),
    topic,
    font=title_font,
    fill="yellow",
    anchor="mm"
)

draw.text(
    (540, 900),
    "ஆச்சரியமான உண்மைகள்",
    font=small_font,
    fill="white",
    anchor="mm"
)

img.save("background.png")

# Generate video
subprocess.run([
    "ffmpeg", "-y",
    "-loop", "1",
    "-i", "background.png",
    "-i", "voice.mp3",
    "-c:v", "libx264",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "128k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    "-vf", "scale=1080:1920",
    "Tamil_Shorts.mp4"
], check=True)

print("SUCCESS! Tamil Shorts created!")