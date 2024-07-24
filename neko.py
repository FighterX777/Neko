import os
import discord # type: ignore
from discord.ext import commands # type: ignore
import requests # type: ignore
import random
import gdown # type: ignore

from flask import Flask, render_template

DEVELOPMENT_ENV = True

app = Flask(__name__)

app_data = {
    "name": "Peter's Starter Template for a Flask Web App",
    "description": "A basic Flask app using bootstrap for layout",
    "author": "Peter Simeth",
    "html_title": "Peter's Starter Template for a Flask Web App",
    "project_name": "Starter Template",
    "keywords": "flask, webapp, template, basic",
}


@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=DEVELOPMENT_ENV)

url = 'https://drive.google.com/u/0/uc?id=1RZa_EFxsk7OmzipsD01CuwWLJvf_oxcE'
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
        facts = [
            "Cats have five toes on their front paws, but only four toes on their back paws.",
            "Cats sleep for 70% of their lives.",
            "A group of cats is called a clowder.",
            "Cats can rotate their ears 180 degrees.",
            "A cat’s nose is as unique as a human's fingerprint.",
        ]
        random_fact = random.choice(facts)
        await message.channel.send(random_fact)

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
