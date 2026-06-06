import os
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté et prêt !")

@bot.command()
async def meteo(ctx, *, ville):
    url = f"https://wttr.in/{ville}?format=3"
    try:
        reponse = requests.get(url, timeout=5)
        await ctx.send(f"📍 {reponse.text.strip()}")
    except:
        await ctx.send("❌ Erreur lors de la récupération de la météo.")

@bot.command()
async def bonjour(ctx):
    await ctx.send(f"👋 Bonjour {ctx.author.name} !")

bot.run(TOKEN)