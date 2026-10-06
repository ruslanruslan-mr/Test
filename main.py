import os
import json
import asyncio
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont
import edge_tts
from telegram import Bot

# Fly.io Secrets orqali o'qib olinadigan aniq nomlar
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")  # Chat/Guruh ID si shunday kiritilgan

CHANNEL_HANDLE = "@PencilHub"  # Sizning nik/kanalingiz

# --- O'ZGARUVCHILARNI TEKSHIRISH ---
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("XATOLIK: TELEGRAM_BOT_TOKEN o'zgaruvchisi topilmadi!")
if not GROUP_ID:
    raise ValueError("XATOLIK: GROUP_ID o'zgaruvchisi topilmadi!")


# --- 1. GLASSMORPHISM & NEON FRAME GENERATOR ---
def create_quiz_frame(question, opt_a, opt_b, correct_highlight=None, bg_color=(15, 23, 42)):
    # 1080x1920 Vertical Shorts HD Frame
    img = Image.new("RGBA", (1080, 1920), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # Gradient Top va Bottom overlay
    for y in range(300):
        alpha = int(255 * (1 - y / 300))
        draw.line([(0, y), (1080, y)], fill=(56, 189, 248, alpha))
        draw.line([(0, 1920 - y), (1080, 1920 - y)], fill=(168, 85, 247, alpha))

    # Header - TikTok / Channel Watermark Bar
    draw.rectangle([80, 100, 1000, 180], fill=(255, 255, 255, 30), outline=(255, 255, 255, 80), width=2)
    draw.text((120, 125), f"TikTok: {CHANNEL_HANDLE} | GEOGRAFIYA QUIZ", fill="white")

    # Central Glassmorphism Card (Savol uchun)
    draw.rounded_rectangle([60, 350, 1020, 750], radius=30, fill=(30, 41, 59, 200), outline=(56, 189, 248), width=4)
    draw.text((100, 450), question, fill="white")

    # Option A Card
    color_a = (34, 197, 94) if correct_highlight == "A" else (255, 255, 255, 40)
    draw.rounded_rectangle([80, 850, 1000, 1000], radius=20, fill=color_a, outline=(255, 255, 255, 100), width=3)
    draw.text((120, 900), f"A) {opt_a}", fill="white")

    # Option B Card
    color_b = (34, 197, 94) if correct_highlight == "B" else (255, 255, 255, 40)
    draw.rounded_rectangle([80, 1050, 1000, 1200], radius=20, fill=color_b, outline=(255, 255, 255, 100), width=3)
    draw.text((120, 1100), f"B) {opt_b}", fill="white")

    # Bottom Call To Action
    draw.rounded_rectangle([80, 1600, 1000, 1750], radius=25, fill=(236, 72, 153, 180))
    draw.text((150, 1650), "QAYSINI TANLADINGIZ? IZOHDA YOZING! 💬👍", fill="white")

    filename = f"frame_{random.randint(1000, 9999)}.png"
    img.save(filename)
    return filename


# --- 2. AUDIO GENERATION (EDGE-TTS) ---
async def generate_speech(text, output_file):
    communicate = edge_tts.Communicate(text, "uz-UZ-SardorNeural")
    await communicate.save(output_file)


# --- 3. VIDEO ASSEMBLY VIA FFMPEG ---
async def build_full_video():
    print("Video tayyorlanmoqda...")
    # Frame yaratamiz
    f1 = create_quiz_frame("Dunyodagi eng katta okean qaysi?", "Atlantika", "Tinch okeani")
    f2 = create_quiz_frame("Dunyodagi eng katta okean qaysi?", "Atlantika", "Tinch okeani", correct_highlight="B")

    audio_file = "q1.mp3"
    await generate_speech("Dunyodagi eng katta okean qaysi? A - Atlantika, B - Tinch okeani.", audio_file)

    output_video = "final_quiz.mp4"

    # FFmpeg orqali MP4 yig'ish (Render)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", "5", "-i", f1,
        "-loop", "1", "-t", "2", "-i", f2,
        "-i", audio_file,
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-shortest", output_video
    ]
    
    subprocess.run(ffmpeg_cmd, check=True)
    print("Render yakunlandi!")

    # Ishlatib bo'lingan kadr va audio fayllarni o'chirib tashlaymiz
    for temp_file in [f1, f2, audio_file]:
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return output_video


# --- 4. TELEGRAM GROUP AUTO-SEND ---
async def send_to_telegram(video_path):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    with open(video_path, "rb") as video:
        await bot.send_video(
            chat_id=GROUP_ID,
            video=video,
            caption="🚀 **Yangi Shorts Video Tayyor!**\n\n📌 3 ta Savol + Hook + Glassmorphism UI\n #Shorts #Quiz #PencilHub",
            parse_mode="Markdown"
        )
    print("Telegram guruhga muvaffaqiyatli yuborildi!")


# --- MAIN PIPELINE ---
async def main():
    video_file = await build_full_video()
    await send_to_telegram(video_file)
    
    # Video faylini ham telegramga ketganidan so'ng o'chirib tashlaymiz
    if os.path.exists(video_file):
        os.remove(video_file)

if __name__ == "__main__":
    asyncio.run(main())
