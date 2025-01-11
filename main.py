import discord
import os
import requests
import json
import random
from discord.ext import commands
from discord import Embed
from datetime import datetime, timedelta

# Token dan API
DISCORD_TOKEN = os.getenv('Discord_Bot')
GEMINI_API_KEY = "AIzaSyApY4HzKQwfX6mRcQYOm2ZsXn3dhQyc-WY"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Inisialisasi bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "/"], intents=intents)

# Nama file untuk menyimpan data ekonomi pengguna
DATA_FILE = "game_data.json"

# Memuat atau membuat file data
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    """Memuat data dari file JSON."""
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Menyimpan data ke file JSON."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_gemini_response(prompt):
    """
    Mengirim prompt ke API Gemini dan mendapatkan respons.
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload, params=params)

    if response.status_code == 200:
        try:
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "Maaf, saya tidak bisa menjawab itu sekarang."
            text = candidates[0]["content"]["parts"][0]["text"]
            return text.strip()
        except (KeyError, IndexError, ValueError):
            return "Maaf, saya tidak bisa menjawab itu sekarang."
    else:
        return "Maaf, saya tidak bisa menjawab itu sekarang."

@bot.event
async def on_ready():
    """Event ketika bot berhasil login."""
    print(f"{bot.user} sudah online!")
    await bot.change_presence(activity=discord.Game(name="Jaa.gg | /help atau !help"))

@bot.event
async def on_message(message):
    """Event ketika bot menerima pesan."""
    if message.author == bot.user:
        return

    # Fitur Gemini di channel commands-talk
    if message.channel.name == "⚙》commands-talk":
        response = get_gemini_response(message.content)
        if response:
            await message.reply(response)
        else:
            await message.reply("Maaf, saya tidak bisa menjawab itu sekarang.")

    # Fitur ekonomi di channel commands-game
    elif message.channel.name == "⚙》commands-game":
        await bot.process_commands(message)

    # Abaikan pesan dari channel lain
    else:
        return

# Command: Saldo
@bot.command()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0, "energy": 100, "last_work": None}
        save_data(data)

    user_data = data[user_id]
    embed = Embed(title=f"Saldo {ctx.author.name}", color=0x00FF00)
    embed.add_field(name="💵 Uang Tunai", value=f"${user_data['cash']}", inline=False)
    embed.add_field(name="🏦 ATM", value=f"${user_data['bank']}", inline=False)
    embed.add_field(name="⚡ Energi", value=f"{user_data['energy']}/100", inline=False)
    await ctx.send(embed=embed)

# Command: Kerja
@bot.command()
async def kerja(ctx):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0, "energy": 100, "last_work": None}
        save_data(data)

    user_data = data[user_id]
    now = datetime.now()

    if user_data["last_work"] and now - datetime.fromisoformat(user_data["last_work"]) < timedelta(minutes=5):
        remaining = timedelta(minutes=5) - (now - datetime.fromisoformat(user_data["last_work"]))
        minutes, seconds = divmod(remaining.total_seconds(), 60)
        await ctx.send(f"Anda masih lelah. Tunggu {int(minutes)} menit {int(seconds)} detik sebelum bekerja lagi.")
        return

    if user_data["energy"] < 10:
        await ctx.send("Energi Anda tidak cukup untuk bekerja. Istirahat atau makan untuk memulihkan energi.")
        return

    gaji = random.randint(50, 200)
    user_data["cash"] += gaji
    user_data["energy"] -= 10
    user_data["last_work"] = now.isoformat()
    save_data(data)

    embed = Embed(title="Kerja Selesai!", description=f"Anda mendapatkan ${gaji} 💵.", color=0x00FF00)
    embed.add_field(name="Saldo Tunai", value=f"${user_data['cash']}", inline=True)
    embed.add_field(name="Energi Tersisa", value=f"{user_data['energy']}/100", inline=True)
    await ctx.send(embed=embed)

# Command: Istirahat
@bot.command()
async def istirahat(ctx):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0, "energy": 100, "last_work": None}
        save_data(data)

    user_data = data[user_id]

    if user_data["energy"] >= 100:
        await ctx.send("Energi Anda sudah penuh!")
        return

    user_data["energy"] += 20
    if user_data["energy"] > 100:
        user_data["energy"] = 100
    save_data(data)

    await ctx.send("Anda telah beristirahat dan memulihkan energi sebesar 20 poin. ⚡")

# Jalankan bot
bot.run(DISCORD_TOKEN)
