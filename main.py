import os
import discord # type: ignore
from discord import app_commands # type: ignore
from discord.ext import commands # type: ignore
from discord.ext.commands import has_permissions # type: ignore
from discord.utils import get # type: ignore
import requests # type: ignore
import random # type: ignore
import yt_dlp # type: ignore
import gdown # type: ignore
import ffmpeg # type: ignore
import asyncio # type: ignore
import logging
from async_timeout import timeout
from youtubesearchpython import VideosSearch # type: ignore
import os # type: ignore
import re # type: ignore

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
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

#Music commands
# Add these global variables at the top of your file
songs = asyncio.Queue()
play_next_song = asyncio.Event()

# Update ytdl_format_options
ytdl_format_options = {
    'verbose': True,
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'force-ipv4': True,
    'preferredcodec': 'mp3',
    'buffersize': 64*1024,  # Increase buffer size
}
# Update ffmpeg_options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 64k'  # Add buffer size option
}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG for more detailed logs

# Define the YTDLSource class
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# ... (keep the rest of your existing code)

# Update play_next function
async def safe_disconnect(voice_client):
    try:
        await voice_client.disconnect()
    except Exception as e:
        print(f"Error disconnecting: {e}")

# ... existing code ...

async def play_next(guild):
    global current_song
    if songs.empty():
        current_song = None
        if guild.voice_client:
            await safe_disconnect(guild.voice_client)
        return


    current_song, channel = await songs.get()
    voice_client = guild.voice_client
    if voice_client and voice_client.is_connected():
        def after_playing(error):
            if error:
                logging.error(f"Error in playback: {error}")
            bot.loop.call_soon_threadsafe(play_next_song.set)

        try:
            voice_client.play(current_song, after=after_playing)
            logging.info(f'Now playing: {current_song.title}')
            await channel.send(f'Now playing: {current_song.title}')

            # Wait for the song to finish or for an error
            try:
                with timeout(int(current_song.data.get('duration', 300)) + 10):  # Add 10 seconds buffer
                    await play_next_song.wait()
            except asyncio.TimeoutError:
                logging.warning("Song playback timed out. Moving to next song.")
            
            play_next_song.clear()
        except discord.errors.ClientException as e:
            logging.error(f"ClientException in play_next: {e}")
            await channel.send("An error occurred while playing the song. Skipping to the next one.")
    else:
        logging.warning("Voice client is not connected. Clearing queue.")
        while not songs.empty():
            await songs.get()
        return

    await play_next(guild)

# Update play command
@bot.tree.command(name="play", description="Play music from a YouTube URL or search term")
@app_commands.describe(query="The YouTube URL or search term")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer(thinking=True)
    
    # Check if the user is in a voice channel
    if not interaction.user.voice:
        await interaction.followup.send("You need to be in a voice channel to use this command.")
        return

    # Check if the bot has permission to join and speak in the voice channel
    permissions = interaction.user.voice.channel.permissions_for(interaction.guild.me)
    if not permissions.connect or not permissions.speak:
        await interaction.followup.send("I don't have permission to join or speak in your voice channel.")
        return

    # Join the user's voice channel if not already in one
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()

    try:
        if not query.startswith('http'):
            results = VideosSearch(query, limit=1).result()
            if not results['result']:
                await interaction.followup.send("No results found.")
                return
            url = f"https://www.youtube.com/watch?v={results['result'][0]['id']}"
        else:
            url = query

        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        await songs.put((player, interaction.channel))

        if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
            await play_next(interaction.guild)
            await interaction.followup.send(f'Now playing: {player.title}')
        else:
            await interaction.followup.send(f'Added to queue: {player.title}')
    except Exception as e:
        logging.error(f"Error in play command: {e}")
        await interaction.followup.send(f"An error occurred: {str(e)}")

# ... (keep the rest of your code)


@bot.command(help="Stop playing music and clear the queue",
             description="(prefix)stop to stop the music and clear the queue",
             brief="Stop music and clear queue")
async def stop(ctx):
    global current_song
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        while not songs.empty():
            await songs.get()
        current_song = None
        await ctx.send("Stopped the music and cleared the queue.")
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(help="Display the current song queue",
             description="(prefix)queue to see the current song queue",
             brief="Show song queue")
async def queue(ctx):
    if songs.empty() and not current_song:
        await ctx.send("The queue is empty.")
    else:
        queue_list = []
        if current_song:
            queue_list.append(f"Currently playing: {current_song.title}")
        queue_copy = songs._queue.copy()
        for i, (song, _) in enumerate(queue_copy, start=1):
            queue_list.append(f"{i}. {song.title}")
        await ctx.send("\n".join(queue_list))

@bot.command(help="Change the volume of the music",
             description="(prefix)volume [0-100] to change the music volume",
             brief="Change music volume")
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to a voice channel.")
    
    if 0 <= volume <= 100:
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")
    else:
        await ctx.send("Volume must be between 0 and 100.")

# Modify the play_next function to update current_song
# Modify play_next function to work with Interactions
async def play_next(guild):
    global current_song
    if songs.empty():
        current_song = None
        return

    current_song, channel = await songs.get()
    voice_client = guild.voice_client
    if voice_client:
        def after_playing(error):
            bot.loop.call_soon_threadsafe(play_next_song.set)
            if error:
                asyncio.run_coroutine_threadsafe(channel.send(f"An error occurred: {error}"), bot.loop)

        voice_client.play(current_song, after=after_playing)
        await channel.send(f'Now playing: {current_song.title}')

    await play_next_song.wait()
    play_next_song.clear()

    await play_next(guild)

#Cat commands

@bot.command()
async def ping(ctx):
    ''' 
    It shows Ping
    ''' 
    # Get the latency of the bot 
    latency = bot.latency  # Included in the Discord.py library 
    # Send it to the user 
    await ctx.send(f"Pong! {latency:.2f}ms")

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
