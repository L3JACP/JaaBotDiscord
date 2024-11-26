import discord
from discord.ext import commands
import requests
import random
import asyncio
import os

# ==========================
# **SETUP**
# ==========================
# Mendapatkan Token dari Environment Variables
DISCORD_TOKEN = os.getenv('Discord_Bot')  # Railway environment key
GEMINI_API_KEY = "AIzaSyBE4u8hB7ib0Cmozd3d-jneWeFbz2L_gSM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"

# Channel yang membatasi pembicaraan hanya bot
MUTE_CHANNELS = ["🔊》Music", "Lofi-1"]

# Inisialisasi intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)


# ==========================
# **FUNGSI: GEMINI API**
# ==========================
def get_gemini_response(prompt):
    """
    Mengirim prompt ke API Gemini dan mendapatkan respons.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": {"text": prompt}}
    params = {"key": GEMINI_API_KEY}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
        if response.status_code == 200:
            data = response.json()
            if "candidates" in data and len(data["candidates"]) > 0:
                return data["candidates"][0].get("output", "Tidak ada respons valid.")
            return "Maaf, tidak ada respons dari API Gemini."
        else:
            return f"Error Gemini: {response.text}"
    except Exception as e:
        return f"Kesalahan Gemini: {str(e)}"


# ==========================
# **EVENTS**
# ==========================
@bot.event
async def on_ready():
    print(f'{bot.user} sudah online!')
    await bot.change_presence(activity=discord.Game(name="Jaa.gg | ?help"))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Fitur AI untuk channel tertentu
    if message.channel.name.strip() == "⚙》commands":
        if message.content.lower().startswith("gm:"):
            prompt = message.content[3:].strip()
            response = get_gemini_response(prompt)
            await message.reply(response, mention_author=True)
        elif message.content.lower() == "hai":
            await message.add_reaction("👋")
    
    # Pastikan commands tetap diproses
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    """
    Mute otomatis jika pengguna masuk ke channel tertentu.
    """
    if after.channel and after.channel.name in MUTE_CHANNELS:
        if not member.bot:
            await member.edit(mute=True)
    elif before.channel and before.channel.name in MUTE_CHANNELS:
        if not member.bot:
            await member.edit(mute=False)


# ==========================
# **KATEGORI: GENERAL**
# ==========================
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency} ms")


@bot.command(name="say")
async def say(ctx, *, message: str):
    await ctx.send(message)


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ {amount} pesan telah dihapus.", delete_after=5)


# ==========================
# **KATEGORI: HIBURAN**
# ==========================
@bot.command(name="roll")
async def roll(ctx, dice: str):
    try:
        rolls, sides = map(int, dice.split('d'))
        result = [random.randint(1, sides) for _ in range(rolls)]
        await ctx.send(f"Hasil lemparan dadu: {', '.join(map(str, result))}")
    except ValueError:
        await ctx.send("Gunakan format: `XdY` (contoh: `2d6`, `1d20`).")


@bot.command(name="choose")
async def choose(ctx, *choices: str):
    if choices:
        await ctx.send(f"Saya memilih: {random.choice(choices)}")
    else:
        await ctx.send("Berikan beberapa pilihan untuk saya pilih!")


@bot.command(name="flip")
async def flip(ctx):
    await ctx.send(f"Hasil lemparan: {random.choice(['Kepala', 'Ekor'])}")


@bot.command(name="guess")
async def guess(ctx):
    """
    Tebak angka antara 1 dan 100.
    """
    number = random.randint(1, 100)
    await ctx.send("Saya telah memilih sebuah angka antara 1 dan 100! Cobalah menebak.")

    def check(msg):
        return msg.author == ctx.author and msg.content.isdigit()

    try:
        guess_msg = await bot.wait_for('message', timeout=30.0, check=check)
        guess_number = int(guess_msg.content)

        if guess_number == number:
            await ctx.send(f"Selamat, kamu menebak angka {number} dengan benar!")
        elif guess_number < number:
            await ctx.send(f"Angka saya lebih besar dari {guess_number}. Coba lagi!")
        else:
            await ctx.send(f"Angka saya lebih kecil dari {guess_number}. Coba lagi!")
    except asyncio.TimeoutError:
        await ctx.send(f"Waktu habis! Angka saya adalah {number}.")


@bot.command(name="mathquiz")
async def mathquiz(ctx):
    """
    Quiz matematika sederhana.
    """
    num1 = random.randint(1, 20)
    num2 = random.randint(1, 20)
    correct_answer = num1 + num2

    await ctx.send(f"Berapa {num1} + {num2}?")

    def check(msg):
        return msg.author == ctx.author and msg.content.isdigit()

    try:
        answer_msg = await bot.wait_for('message', timeout=30.0, check=check)
        user_answer = int(answer_msg.content)

        if user_answer == correct_answer:
            await ctx.send(f"Selamat, jawabannya benar! {num1} + {num2} = {correct_answer}.")
        else:
            await ctx.send(f"Salah! Jawaban yang benar adalah {correct_answer}.")
    except asyncio.TimeoutError:
        await ctx.send(f"Waktu habis! Jawaban yang benar adalah {correct_answer}.")


@bot.command(name="trivia")
async def trivia(ctx):
    """
    Trivia game.
    """
    questions = [
        {"question": "Apa ibu kota Prancis?", "answer": "Paris"},
        {"question": "Siapa presiden Amerika Serikat pertama?", "answer": "George Washington"},
        {"question": "Di planet mana manusia pertama kali mendarat?", "answer": "Bumi"},
    ]
    
    question = random.choice(questions)
    await ctx.send(question["question"])

    def check(msg):
        return msg.author == ctx.author and msg.content.strip().lower() == question["answer"].lower()

    try:
        answer_msg = await bot.wait_for('message', timeout=30.0, check=check)

        await ctx.send(f"Selamat, jawaban kamu benar! {question['answer']} adalah jawabannya.")
    except asyncio.TimeoutError:
        await ctx.send(f"Waktu habis! Jawaban yang benar adalah {question['answer']}.")


# ==========================
# **KATEGORI: ADMIN**
# ==========================
@bot.command(name="muteall")
@commands.has_permissions(administrator=True)
async def muteall(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        for member in channel.members:
            if not member.bot:
                await member.edit(mute=True)
        await ctx.send(f"🔇 Semua member di {channel.name} telah di-mute.")
    else:
        await ctx.send("Kamu harus berada di voice channel untuk menggunakan command ini.")


@bot.command(name="unmuteall")
@commands.has_permissions(administrator=True)
async def unmuteall(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        for member in channel.members:
            await member.edit(mute=False)
        await ctx.send(f"🔊 Semua member di {channel.name} telah di-unmute.")
    else:
        await ctx.send("Kamu harus berada di voice channel untuk menggunakan command ini.")


# Menjalankan bot
if DISCORD_TOKEN:
    bot.run(DISCORD_TOKEN)
else:
    print("Error: Discord Token tidak ditemukan!")
