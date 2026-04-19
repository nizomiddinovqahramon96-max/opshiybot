import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
import wikipedia
from deep_translator import GoogleTranslator
import yt_dlp
import os
import qrcode
import google.generativeai as genai

# =======================
# 🔑 KEYS
# =======================

BOT_TOKEN = "8622576777:AAGFd5LbFfeIkjZUuaL9eLHNalT9EfK_TpM"
GEMINI_API_KEY = "AIzaSyCY9gDuL1SjpYPljChehcZlh_ZXS9AEpIs"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_mode = {}
user_lang = {}
music_cache = {}

# =======================
# MENU
# =======================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Wikipedia"), KeyboardButton(text="Translator")],
        [KeyboardButton(text="YouTube Downloader"), KeyboardButton(text="Instagram Downloader")],
        [KeyboardButton(text="QR code generator")],
        [KeyboardButton(text="AI chat bot")],
        [KeyboardButton(text="Music Finder")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)

# =======================
# START
# =======================

@dp.message(F.text == "/start")
async def start(message: Message):
    user_mode[message.from_user.id] = None
    await message.answer("🚀 Bot ishladi", reply_markup=menu)

@dp.message(F.text == "⬅️ Orqaga")
async def back(message: Message):
    uid = message.from_user.id
    user_mode[uid] = None
    await message.answer("🏠 Menu", reply_markup=menu)

# =======================
# MODES
# =======================

@dp.message(F.text == "Wikipedia")
async def wiki_mode(message: Message):
    user_mode[message.from_user.id] = "wiki"
    await message.answer("📚 Matn yozing")

@dp.message(F.text == "Translator")
async def trans_mode(message: Message):
    user_mode[message.from_user.id] = "trans"
    await message.answer("🌍 Matn yozing")

@dp.message(F.text == "YouTube Downloader")
async def yt_mode(message: Message):
    user_mode[message.from_user.id] = "yt"
    await message.answer("📥 Link yuboring")

@dp.message(F.text == "Instagram Downloader")
async def insta_mode(message: Message):
    user_mode[message.from_user.id] = "insta"
    await message.answer("📥 Link yuboring")

@dp.message(F.text == "QR code generator")
async def qr_mode(message: Message):
    user_mode[message.from_user.id] = "qr"
    await message.answer("📌 Matn yozing")

@dp.message(F.text == "AI chat bot")
async def ai_mode(message: Message):
    user_mode[message.from_user.id] = "ai"
    await message.answer("🤖 Savol yozing")

@dp.message(F.text == "Music Finder")
async def music_mode(message: Message):
    user_mode[message.from_user.id] = "music"
    await message.answer("🎵 Misol: Munisa Rizayeva")

# =======================
# MUSIC SEARCH (FIXED)
# =======================

@dp.message(F.text)
async def handler(message: Message):
    uid = message.from_user.id
    mode = user_mode.get(uid)
    text = message.text

    # ---------------- MUSIC ----------------
    if mode == "music":
        msg = await message.answer("🔎 Qidirilmoqda...")

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch5:{text}", download=False)

            entries = info.get("entries", [])

            music_cache[uid] = {}
            buttons = []

            for i, entry in enumerate(entries):
                if not entry:
                    continue

                title = entry.get("title", "Unknown")
                url = entry.get("webpage_url")

                music_cache[uid][str(i)] = url

                buttons.append([
                    InlineKeyboardButton(
                        text=f"🎵 {title[:35]}",
                        callback_data=f"music_{i}"
                    )
                ])

            kb = InlineKeyboardMarkup(inline_keyboard=buttons)

            await message.answer("🎧 Tanlang:", reply_markup=kb)
            await msg.delete()

        except Exception as e:
            await msg.edit_text(f"❌ Xatolik: {e}")
        return

    # ---------------- OTHER MODES ----------------

    elif mode == "wiki":
        try:
            wikipedia.set_lang("uz")
            res = wikipedia.summary(text, sentences=2)
            await message.answer(res)
        except:
            await message.answer("❌ Wiki topilmadi")

    elif mode == "trans":
        try:
            res = GoogleTranslator(source='auto', target='ru').translate(text)
            await message.answer(res)
        except:
            await message.answer("❌ Error")

    elif mode == "qr":
        img = qrcode.make(text)
        img.save("qr.png")
        await message.answer_photo(FSInputFile("qr.png"))
        os.remove("qr.png")

    elif mode == "ai":
        try:
            res = model.generate_content(text)
            await message.answer(res.text)
        except:
            await message.answer("❌ AI error")

# =======================
# MUSIC DOWNLOAD BUTTON
# =======================

@dp.callback_query(F.data.startswith("music_"))
async def download_music(callback: CallbackQuery):
    uid = callback.from_user.id
    index = callback.data.split("_")[1]

    url = music_cache.get(uid, {}).get(index)

    if not url:
        await callback.answer("❌ Topilmadi")
        return

    msg = await callback.message.answer("🎧 Yuklanmoqda...")

    file_path = f"{uid}.mp3"

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path,
            'quiet': True,
            'noplaylist': True,
            'ffmpeg_location': r'C:\Users\quettabyte\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await callback.message.answer_audio(FSInputFile(file_path))

    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

        await msg.delete()

# =======================
# RUN
# =======================

async def main():
    print("🚀 BOT READY")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())