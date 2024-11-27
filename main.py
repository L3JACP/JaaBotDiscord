import discord
import os
import requests
import json
from discord.ext import commands

# Token dan API
DISCORD_TOKEN = os.getenv('Discord_Bot')
GEMINI_API_KEY = "AIzaSyBE4u8hB7ib0Cmozd3d-jneWeFbz2L_gSM"
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
    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }
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
    """
    Event ketika bot berhasil login.
    """
    print(f"{bot.user} sudah online!")
    await bot.change_presence(activity=discord.Game(name="Jaa.gg | /help/!help"))

@bot.event
async def on_message(message):
    """
    Event ketika bot menerima pesan.
    """
    if message.author == bot.user:
        return

    # Batasi interaksi berdasarkan channel
    if message.channel.name == "⚙》commands-talk":
        # Hanya untuk fitur Gemini
        response = get_gemini_response(message.content)
        if response:
            try:
                await message.reply(response)
            except discord.errors.HTTPException as e:
                print(f"Error saat mengirim balasan: {e}")
                await message.reply("Maaf, saya tidak bisa menjawab itu sekarang.")
        else:
            await message.reply("Maaf, saya tidak bisa menjawab itu sekarang.")

    elif message.channel.name == "⚙》commands-game":
        # Hanya untuk fitur ekonomi
        await bot.process_commands(message)

    # Abaikan pesan dari channel lain
    else:
        return

# Command: Lihat saldo
@bot.command()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0}
        save_data(data)

    user_data = data[user_id]
    await ctx.send(f"Saldo Anda:\n💵 Uang Tunai: ${user_data['cash']}\n🏦 ATM: ${user_data['bank']}")

# Command: Kerja
@bot.command()
async def kerja(ctx):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0}

    import random
    gaji = random.randint(50, 200)
    data[user_id]["cash"] += gaji
    save_data(data)

    await ctx.send(f"Kerja selesai! Anda mendapatkan ${gaji} 💵.\nSaldo tunai Anda sekarang: ${data[user_id]['cash']}")

# Command: Simpan uang ke ATM
@bot.command()
async def atm(ctx, jumlah: int = None):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0}

    user_data = data[user_id]

    if jumlah is None:
        await ctx.send(f"Saldo ATM Anda: ${user_data['bank']}\nGunakan `!atm <jumlah>` untuk menyetor uang ke ATM.")
        return

    if jumlah <= 0 or jumlah > user_data["cash"]:
        await ctx.send("Jumlah tidak valid atau saldo tunai tidak cukup.")
        return

    user_data["cash"] -= jumlah
    user_data["bank"] += jumlah
    save_data(data)

    await ctx.send(f"Berhasil menyetor ${jumlah} ke ATM. Saldo ATM Anda sekarang: ${user_data['bank']}")

# Command: Ambil uang dari ATM
@bot.command()
async def ambil(ctx, jumlah: int):
    user_id = str(ctx.author.id)
    if ctx.channel.name != "⚙》commands-game":
        await ctx.send("Perintah ini hanya dapat digunakan di channel ⚙》commands-game.")
        return

    data = load_data()
    if user_id not in data:
        data[user_id] = {"cash": 0, "bank": 0}

    user_data = data[user_id]

    if jumlah <= 0 or jumlah > user_data["bank"]:
        await ctx.send("Jumlah tidak valid atau saldo ATM tidak cukup.")
        return

    user_data["bank"] -= jumlah
    user_data["cash"] += jumlah
    save_data(data)

    await ctx.send(f"Berhasil menarik ${jumlah} dari ATM. Saldo tunai Anda sekarang: ${user_data['cash']}")

# Jalankan bot
bot.run(DISCORD_TOKEN)
