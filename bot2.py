import os
import discord
from discord.ext import commands
import requests

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est connecté et prêt !")

@bot.event
async def on_member_join(member):
    canal = discord.utils.get(member.guild.text_channels, name="général")
    if canal:
        await canal.send(f"👋 Bienvenue sur le serveur {member.mention} ! Tape `!aide` pour voir les commandes.")

@bot.command()
async def aide(ctx):
    message = """
🤖 **Commandes disponibles :**
`!bonjour` — Je te salue !
`!meteo [ville]` — Météo d'une ville
`!meteo_multi [ville1, ville2...]` — Météo de plusieurs villes
`!aide` — Affiche ce message
    """
    await ctx.send(message)

@bot.command()
async def bonjour(ctx):
    await ctx.send(f"👋 Bonjour {ctx.author.name} !")

@bot.command()
async def meteo(ctx, *, ville):
    url = f"https://wttr.in/{ville}?format=3"
    try:
        reponse = requests.get(url, timeout=5)
        await ctx.send(f"📍 {reponse.text.strip()}")
    except:
        await ctx.send("❌ Erreur lors de la récupération de la météo.")

@bot.command()
async def meteo_multi(ctx, *, saisie):
    saisie = saisie.replace(";", ",")
    villes = [v.strip() for v in saisie.split(",") if v.strip()]
    
    await ctx.send(f"🔍 Récupération de la météo pour {len(villes)} ville(s)...")
    
    resultat = ""
    for ville in villes:
        url = f"https://wttr.in/{ville}?format=3"
        try:
            reponse = requests.get(url, timeout=5)
            resultat += f"📍 {reponse.text.strip()}\n"
        except:
            resultat += f"❌ {ville} : erreur\n"
    
    await ctx.send(resultat)

bot.run(TOKEN)