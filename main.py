import os
import json
import asyncio
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from telegram import Bot

# Fly.io Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

CHANNEL_HANDLE = "@PencilHub"

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("XATOLIK: TELEGRAM_BOT_TOKEN o'zgaruvchisi topilmadi!")
if not GROUP_ID:
    raise ValueError("XATOLIK: GROUP_ID o'zgaruvchisi topilmadi!")

# --- 1. ULTRA PRO MAX GLASSMORPHISM & NEON UI ---
def create_quiz_frame(question, opt_a, opt_b, correct_highlight=None, bg_phase=0):
    W, H = 1080, 1920
    # Harakatlanuvchi neon fon uchun phazaga qarab rang o'zgaradi
    bg_color = (10 + bg_phase*2, 15 + bg_phase*3, 30 + bg_phase*4)
    img = Image.new("RGBA", (W, H), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Shriftlarni yuklash (Katta va o'qishga juda qulay)
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font_head = ImageFont.truetype(font_path, 42)
        font_q = ImageFont.truetype(font_path, 52)
        font_opt = ImageFont.truetype(font_path, 46)
        font_cta = ImageFont.truetype(font_path, 38)
    except:
        font_head = font_q = font_opt = font_cta = ImageFont.load_default()

    # Dynamic Glowing Gradient Overlays
    for y in range(350):
        alpha = int(220 * (1 - y / 350))
        draw.line([(0, y), (W, y)], fill=(56, 189, 248, alpha))
        draw.line([(0, H - y), (W, H - y)], fill=(168, 85, 247, alpha))

    # Header Bar (TikTok Handle)
    draw.rounded_rectangle([60, 80, 1020, 180], radius=25, fill=(20, 30, 55, 230), outline=(56, 189, 248), width=3)
    draw.text((100, 115), f"TikTok: {CHANNEL_HANDLE}  |  QUIZ TIME ⚡", fill=(56, 189, 248), font=font_head)

    # Question Glass Box
    draw.rounded_rectangle([60, 320, 1020, 740], radius=35, fill=(23, 32, 54, 240), outline=(139, 92, 246), width=4)
    
    # Text Auto-Wrap (Matn sig'ishi uchun)
    words = question.split()
    lines, curr_line = [], ""
    for w in words:
        test = f"{curr_line} {w}".strip()
        if len(test) < 22:
            curr_line = test
        else:
            lines.append(curr_line)
            curr_line = w
    lines.append(curr_line)

    y_pos = 410
    for line in lines:
        draw.text((100, y_pos), line, fill=(255, 255, 255), font=font_q)
        y_pos += 70

    # Option A Card
    fill_a = (34, 197, 94, 240) if correct_highlight == "A" else (30, 41, 59, 230)
    border_a = (34, 197, 94) if correct_highlight == "A" else (148, 163, 184)
    draw.rounded_rectangle([60, 820, 1020, 980], radius=25, fill=fill_a, outline=border_a, width=4)
    draw.text((100, 875), f"A)  {opt_a}", fill=(255, 255, 255), font=font_opt)

    # Option B Card
    fill_b = (34, 197, 94, 240) if correct_highlight == "B" else (30, 41, 59, 230)
    border_b = (34, 197, 94) if correct_highlight == "B" else (148, 163, 184)
    draw.rounded_rectangle([60, 1020, 1020, 1180], radius=25, fill=fill_b, outline=border_b, width=4)
    draw.text((100, 1075), f"B)  {opt_b}", fill=(255, 255, 255), font=font_opt)

    # 3D Animated CTA Callout
    draw.rounded_rectangle([60, 1600, 1020, 1740], radius=30, fill=(219, 39, 119, 230), outline=(244, 114, 182), width=3)
    draw.text((110, 1645), "JAVOBINGIZNI IZOHDA YOZING! 💬👍", fill=(255, 255, 255), font=font_cta)

    filename = f"frame_{random.randint(10000, 99999)}.png"
    img.save(filename)
    return filename

# --- 2. GENERATE PROCEDURAL SOUND EFFECTS (FFmpeg Synth) ---
def generate_sfx():
    # Whoosh Sound Effect
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.3:c=pink:r=44100", "-af", "afade=t=in:ss=0:d=0.1,afade=t=out:st=0.2:d=0.1,volume=0.5", "whoosh.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Ticking Sound Effect
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=1000:d=0.05", "tick.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # Correct Answer Chime
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=800:d=0.2", "-af", "adelay=100|100", "correct.wav"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --- 3. EDGE-TTS SPEECH GENERATOR ---
async def generate_speech(text, output_file):
    communicate = edge_tts.Communicate(text, "uz-UZ-SardorNeural")
    await communicate.save(output_file)

# --- 4. ADVANCED FFMPEG RENDER ENGINE ---
async def build_full_video():
    print("Ultra Pro Max Video generatsiya qilinmoqda...")
    generate_sfx()

    # Sample Data (3 ta Savol - Monetizatsiyaga mos keladigan vaqt)
    questions_data = [
        {"q": "Dunyodagi eng katta okean qaysi?", "a": "Atlantika", "b": "Tinch okeani", "correct": "B"},
        {"q": "O'zbekiston poytaxti qaysi shahar?", "a": "Toshkent", "b": "Samarqand", "correct": "A"},
        {"q": "Quyosh tizimidagi eng katta sayyora?", "a": "Yupiter", "b": "Mars", "correct": "A"}
    ]

    temp_files = ["whoosh.wav", "tick.wav", "correct.wav"]
    segment_videos = []

    for idx, item in enumerate(questions_data):
        f_ask = create_quiz_frame(item["q"], item["a"], item["b"], bg_phase=idx)
        f_answer = create_quiz_frame(item["q"], item["a"], item["b"], correct_highlight=item["correct"], bg_phase=idx+1)
        
        speech_file = f"speech_{idx}.mp3"
        await generate_speech(f"{item['q']} A - {item['a']}, yoki B - {item['b']}?", speech_file)
        
        seg_output = f"segment_{idx}.mp4"

        # Zoom-in animatsiyasi, audio sinxronizatsiya va SFX audio mix
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-t", "5", "-i", f_ask,
            "-loop", "1", "-t", "2.5", "-i", f_answer,
            "-i", speech_file,
            "-i", "whoosh.wav",
            "-i", "correct.wav",
            "-filter_complex",
            # Smooth Zoom Pan va Dynamic Concat
            "[0:v]zoompan=z='min(zoom+0.0015,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=125:s=1080x1920[v0];"
            "[1:v]zoompan=z='1.05':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=62:s=1080x1920[v1];"
            "[v0][v1]concat=n=2:v=1:a=0[v];"
            "[3:a][2:a][4:a]concat=n=3:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
            seg_output
        ]
        
        subprocess.run(ffmpeg_cmd, check=True)
        segment_videos.append(seg_output)
        temp_files.extend([f_ask, f_answer, speech_file, seg_output])

    # Segmentlarni bitta final videoga ulash
    concat_list = "concat_list.txt"
    with open(concat_list, "w") as f:
        for v in segment_videos:
            f.write(f"file '{v}'\n")
    temp_files.append(concat_list)

    final_video = "final_quiz_pro.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-c", "copy", final_video
    ], check=True)

    # Tozalash
    for t in temp_files:
        if os.path.exists(t):
            os.remove(t)

    print("Ultra Pro Max Render Muvaffaqiyatli Yakunlandi!")
    return final_video

# --- 5. TELEGRAM AUTO-SEND ---
async def send_to_telegram(video_path):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    with open(video_path, "rb") as video:
        await bot.send_video(
            chat_id=GROUP_ID,
            video=video,
            caption="🔥 **2026 Ultra Pro Max Shorts Video Tayyor!**\n\n✨ Dynamic Zoom + Glassmorphism UI + SFX Ovozlar\n📌 #Shorts #Quiz #PencilHub",
            parse_mode="Markdown"
        )
    print("Telegram guruhga muvaffaqiyatli yuborildi!")

async def main():
    video_file = await build_full_video()
    await send_to_telegram(video_file)
    if os.path.exists(video_file):
        os.remove(video_file)

if __name__ == "__main__":
    asyncio.run(main())
