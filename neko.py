import os
import discord # type: ignore
from discord.ext import commands # type: ignore
import requests # type: ignore
import random
import gdown # type: ignore

url = 'https://drive.google.com/u/0/uc?id=12oT7SQi_c2b9ugLsvzTgwEk9Huna5lKg'
output = 'token.txt'
gdown.download(url, output, quiet=False)

with open('token.txt') as f:
    TOKEN = f.readline()

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Cat Bot is online!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!meow":
        await message.channel.send("Meow! ")

    if message.content == "!catfact":
        try:
            response = requests.get("https://catfact.ninja/fact")
            cat_fact = response.json()["fact"]
            await message.channel.send(cat_fact)
        except Exception as e:
            print(f"Error fetching cat fact: {e}")
            await message.channel.send("Sorry, I could not fetch a fact at this time.")

    if message.content == "!nekopic":
        try:
            response = requests.get("https://api.thecatapi.com/v1/images/search")
            cat_image_url = response.json()[0]["url"]
            await message.channel.send(cat_image_url)
        except Exception as e:
            print(f"Error fetching cat image: {e}")
            await message.channel.send("Sorry, I could not fetch a cat image at this time.")

    await bot.process_commands(message)

bot.run(TOKEN)
