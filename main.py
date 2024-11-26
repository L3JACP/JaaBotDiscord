import discord
import os
import requests
from discord.ext import commands

# Token dan API
DISCORD_TOKEN = os.getenv('Discord_Bot')
GEMINI_API_KEY = "AIzaSyBE4u8hB7ib0Cmozd3d-jneWeFbz2L_gSM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Inisialisasi bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_gemini_response(prompt):
    """
    Mengirim prompt ke API Gemini dan mendapatkan respons.
    """
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    print(f"Mengirim payload ke API Gemini: {payload}")
    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)

    print(f"Status code dari respons API Gemini: {response.status_code}")
    print(f"Respons dari API Gemini: {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            # Ambil teks dari respons
            candidates = data.get("candidates", [])
            if not candidates:
                print("Respons tidak memiliki 'candidates'.")
                return "Maaf, saya tidak bisa menjawab itu sekarang."

            text = candidates[0]["content"]["parts"][0]["text"]
            if not text:
                print("Teks dalam respons kosong.")
                return "Maaf, respons dari API kosong."

            return text.strip()
        except (KeyError, IndexError, ValueError) as e:
            print(f"Kesalahan parsing JSON: {e}")
            return "Maaf, saya tidak bisa menjawab itu sekarang."
    else:
        print(f"Error dari API Gemini: {response.text}")
        return "Maaf, saya tidak bisa menjawab itu sekarang."

@bot.event
async def on_ready():
    """
    Event ketika bot berhasil login.
    """
    print(f"{bot.user} sudah online!")
    await bot.change_presence(activity=discord.Game(name="Jaa.gg | ?help"))

@bot.event
async def on_message(message):
    """
    Event ketika bot menerima pesan.
    """
    if message.author == bot.user:
        return

    print(f"Pesan yang diterima dari user: {message.content}")
    
    # Kirim prompt ke API Gemini
    response = get_gemini_response(message.content)
    print(f"Respons yang dikirimkan ke user: {response}")

    # Balas pesan user
    if response:
        await message.reply(response, mention_author=True)
    else:
        await message.reply("Maaf, saya tidak bisa menjawab itu sekarang.", mention_author=True)

# Jalankan bot
bot.run(DISCORD_TOKEN)
