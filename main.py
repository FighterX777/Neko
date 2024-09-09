import discord
from discord import app_commands
import requests
import random   
from discord.ext import commands
from discord.ext import commands
from discord.ext.commands import has_permissions
import gdown
import yt_dlp
import asyncio
from youtubesearchpython import VideosSearch
from discord.ext.commands import has_permissions

#Download Token(NekoBot)
url = 'https://drive.google.com/u/0/uc?id=1l5EZ0E41Yr0xhe2N3iMrZ3QEFsOOsMBa'
output = 'token.txt'
gdown.download(url, output, quiet=False)

with open('token.txt') as f:
    TOKEN = f.readline()

# Initialize bot with intents
intents = discord.Intents.all()
intents.messages = True
intents.guilds = True
intents.members = True
intents.voice_states = True

Bot = commands.Bot(command_prefix=".", intents=intents)

@Bot.command()
@commands.is_owner()
async def sync(ctx):
    synced = await Bot.tree.sync()
    await ctx.send(f"Synced {len(synced)} commands.")

# Or in on_ready
@Bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {Bot.user}')
    await Bot.tree.sync()
    print('Command tree synced')

# Command to respond with Pong
@Bot.command(help="Answers with pong and bot's latency",
             description="(prefix)ping to get the bot's latency",
             brief="Answers with pong and bot's latency")
async def ping(ctx):
    await ctx.send(f'Pong! , My latency is {round(Bot.latency * 1000)}ms')



"""
@Bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member.mention} has been kicked. Reason: {reason}')

@Bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for banning")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    await member.ban(reason=reason)
    await interaction.response.send_message(f'{member.mention} has been banned. Reason: {reason}')

@Bot.tree.command(name="unban", description="Unban a member from the server")
@app_commands.describe(member="The member to unban (e.g., user#1234)")
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, member: str):
    banned_users = await interaction.guild.bans()
    member_name, member_discriminator = member.split('#')
    
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f'Unbanned {user.mention}')
            return
    await interaction.response.send_message(f'User {member} not found in ban list.')
    """

@Bot.tree.command(name="mute", description="Mute a member in the server")
@app_commands.describe(member="The member to mute", reason="Reason for muting")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await interaction.guild.create_role(name="Muted")
        for channel in interaction.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    
    await member.add_roles(muted_role, reason=reason)
    await interaction.response.send_message(f'{member.mention} has been muted. Reason: {reason}')

@Bot.tree.command(name="unmute", description="Unmute a member in the server")
@app_commands.describe(member="The member to unmute")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
    await member.remove_roles(muted_role)
    await interaction.response.send_message(f'{member.mention} has been unmuted.')

@Bot.tree.command(name="clear", description="Clear a specified number of messages")
@app_commands.describe(
    amount="Number of messages to clear",
    user="Clear messages from a specific user (optional)",
    bots="Clear messages from bots (True/False, optional)",
    embeds="Clear messages with embeds (True/False, optional)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(
    interaction: discord.Interaction, 
    amount: int, 
    user: discord.Member = None, 
    bots: bool = False, 
    embeds: bool = False
):
    await interaction.response.defer(ephemeral=True)
    
    def check_message(message):
        if user and message.author != user:
            return False
        if bots and not message.author.bot:
            return False
        if embeds and not message.embeds:
            return False
        return True
    
    deleted = await interaction.channel.purge(limit=amount, check=check_message)
    
    await interaction.followup.send(
        f'Cleared {len(deleted)} messages.'
        f'{f" From user: {user.mention}" if user else ""}'
        f'{" From bots" if bots else ""}'
        f'{" With embeds" if embeds else ""}',
        ephemeral=True
    )

# Added Meow command
@Bot.command(aliases=["Meow"],
             help="Answers with Meow!",
             description="(prefix)meow to get a meow",
             brief="Answers with Meow!",
             enabled=True,
             hidden = False)
async def meow(ctx):
    await ctx.send("Meow!")

#Cat facts 
@Bot.command(aliases=["cf"],
             help="Get a cat fact",
             description="(prefix)cf to get a cat fact",
             brief="Get a cat fact")
async def catfact(ctx):
    try:
        response = requests.get("https://catfact.ninja/fact")
        cat_fact = response.json().get("fact", "No fact available")
        await ctx.send(cat_fact)
    except Exception as e:
        print(f"Error fetching cat fact: {e}")
        await ctx.send("Sorry, I could not fetch a fact at this time.")

@Bot.command(aliases=["cp"],
             help="Get a cat picture",
             description="(prefix)cp to get a cat picture",
             brief="Get a cat picture")
async def nekopic(ctx):
    try:
        response = requests.get("https://api.thecatapi.com/v1/images/search")
        cat_image_url = response.json()[0].get("url", "No image available")
        await ctx.send(cat_image_url)
    except Exception as e:
        print(f"Error fetching cat image: {e}")
        await ctx.send("Sorry, I could not fetch a cat image at this time.")

#Make the bot say something
@Bot.command(aliases=["speak", "echo"],
             help="Make the bot say something",
             description="(prefix)say message",
             brief="Make the bot say something")
async def say(ctx, *, args = "WHAT??"):
    await ctx.send("".join(args))

#Roll a dice
@Bot.command(aliases=["roll"],
             help="Roll a dice",
             description="(prefix)dice to roll a dice",
             brief="Roll a dice")
async def dice(ctx):
    await ctx.send(random.randint(1, 6))

#Random choice generator
@Bot.command(aliases=["rnd", "random"],
             help="Generate a random choice",
             description="(prefix)random item1 item2 item3......",
             brief="Generate a random choice")
async def Random(ctx, *args):
    await ctx.send(random.choice(args))

#Number guessing game
@Bot.command(aliases=["number"],
             help="Guess a number between 1 and 1000",
                    description="(prefix)guess",
             brief="Guess a number between 1 and 1000")
async def guess(ctx):
    await ctx.send("Guess a number between 1 and 1000")
    await ctx.send(random.randint(1, 1000))

#Number calculator
@Bot.command(aliases=["calculator"],
             help="Calculate two numbers",
             description="(prefix)calc a_operator_b",
             brief="contains (+ - * / ^ %)")
async def calc(ctx, a: int,operation: str, b: int):
    if operation == "+":
        await ctx.send(a + b)
    elif operation == "-":
        await ctx.send(a - b)
    elif operation == "*":
        await ctx.send(a * b)
    elif operation == "/":
        await ctx.send(a / b)
    elif operation == "^":
        await ctx.send(a ** b)
    elif operation == "%":
        await ctx.send(a % b)
    else:
        await ctx.send("Invalid operation")
  
#joined server
@Bot.command(help="Join a server",
             description="(prefix)join @member",
             brief="Join a server")
async def joined(ctx, who : discord.Member):
    await ctx.send(f"{who}, joined the server on {who.joined_at}")

#Slap command
class Slapper(commands.Converter):
    use_nicknames = bool
    def __init__(self,*, use_nicknames):
        self.use_nicknames = use_nicknames
    async def convert(self, ctx, argument):
            someone = ctx.message.mentions[0].display_name
            nickname = ctx.author.display_name
            if argument:  # Check if an argument is given
                if self.use_nicknames:
                    nickname = ctx.author.display_name
                someone = ctx.message.mentions[0].display_name
                return f"{nickname} slapped {someone} with {argument}"

            else:
                if self.use_nicknames:
                    nickname = ctx.author.display_name
                    someone = ctx.message.mentions[0].display_name
                    return f"{nickname} slapped {someone}"
@Bot.command(help="Slap someone",
             description="(prefix)slap item @member",
             brief="Slap someone",
             arguments=True)
async def slap(ctx, who : Slapper(use_nicknames=True)):
    await ctx.send(who)

#music
import asyncio
import logging
from async_timeout import timeout

songs = asyncio.Queue()
play_next_song = asyncio.Event()

# Update ytdl_format_options
ytdl_format_options = {
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
    'buffersize': 256*1024,  # Increase buffer size
}
# Update ffmpeg_options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 256k'  # Add buffer size option
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
            await guild.voice_client.disconnect()
        return

    current_song, channel = await songs.get()
    voice_client = guild.voice_client
    if voice_client and voice_client.is_connected():
        def after_playing(error):
            if error:
                logging.error(f"Error in playback: {error}")
            Bot.loop.call_soon_threadsafe(play_next_song.set)

        try:
            voice_client.play(current_song, after=after_playing)
            logging.info(f'Now playing: {current_song.title}')
            await channel.send(f'Now playing: {current_song.title}')

            # Wait for the song to finish or for an error
            await play_next_song.wait()
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
@Bot.tree.command(name="play", description="Play music from a YouTube URL or search term")
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
        voice_client = await interaction.user.voice.channel.connect()
        await interaction.guild.change_voice_state(channel=voice_client.channel, self_deaf=True)
    else:
        voice_client = interaction.guild.voice_client
        if not interaction.guild.me.voice.self_deaf:
            await interaction.guild.change_voice_state(channel=voice_client.channel, self_deaf=True)

    try:
        if not query.startswith('http'):
            results = VideosSearch(query, limit=1).result()
            if not results['result']:
                await interaction.followup.send("No results found.")
                return
            url = f"https://www.youtube.com/watch?v={results['result'][0]['id']}"
        else:
            url = query

        player = await YTDLSource.from_url(url, loop=Bot.loop, stream=True)
        await songs.put((player, interaction.channel))

        if not voice_client.is_playing():
            await play_next(interaction.guild)
            await interaction.followup.send(f'Now playing: {player.title}')
        else:
            await interaction.followup.send(f'Added to queue: {player.title}')
    except Exception as e:
        logging.error(f"Error in play command: {e}")
        await interaction.followup.send(f"An error occurred: {str(e)}")

# ... (keep the rest of your code)


@Bot.command(help="Stop playing music and clear the queue",
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

@Bot.command(help="Display the current song queue",
             description="(prefix)queue to see the current song queue",
             brief="Show song queue")
async def queue(ctx):
    if songs.empty() and not current_song:
        await ctx.send("The queue is empty.")
    else:
        queue_list = []
        if current_song:
            queue_list.append(f"Currently playing: {current_song.title}")
        queue_copy = list(songs._queue)
        for i, (song, _) in enumerate(queue_copy, start=1):
            queue_list.append(f"{i}. {song.title}")
        await ctx.send("\n".join(queue_list))

@Bot.command(help="Change the volume of the music",
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
            Bot.loop.call_soon_threadsafe(play_next_song.set)
            if error:
                asyncio.run_coroutine_threadsafe(channel.send(f"An error occurred: {error}"), Bot.loop)

        voice_client.play(current_song, after=after_playing)
        await channel.send(f'Now playing: {current_song.title}')

    await play_next_song.wait()
    play_next_song.clear()

    await play_next(guild)
      
@Bot.tree.command(name="resume", description="Resume the paused music")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("Resumed the music.")
    else:
        await interaction.response.send_message("There's no paused music to resume.")

@Bot.tree.command(name="remove", description="Remove a song from the queue")
@app_commands.describe(index="The position of the song in the queue (starting from 1)")
async def remove(interaction: discord.Interaction, index: int):
    await interaction.response.defer(thinking=True)
    
    if songs.empty():
        await interaction.followup.send("The queue is empty.")
        return

    if index < 1 or index > songs.qsize():
        await interaction.followup.send("Invalid song index.")
        return

    # Convert queue to list, remove the song, then recreate the queue
    queue_list = list(songs._queue)
    removed_song, _ = queue_list.pop(index - 1)
    
    # Clear the current queue and add back the songs
    songs._queue.clear()
    for song in queue_list:
        await songs.put(song)

    await interaction.followup.send(f"Removed '{removed_song.title}' from the queue.")

# Don't forget to add a pause command if you haven't already
@Bot.tree.command(name="pause", description="Pause the currently playing music")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("Paused the music.")
    else:
        await interaction.response.send_message("There's no music playing to pause.")

@Bot.tree.command(name="skip", description="Skip the currently playing song")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
        await interaction.followup.send("There's no song playing to skip.")
        return

    # Stop the current song
    interaction.guild.voice_client.stop()

    # Check if there are more songs in the queue
    if songs.empty():
        await interaction.followup.send("Skipped the current song. The queue is now empty.")
    else:
        # The play_next function will automatically play the next song
        await interaction.followup.send("Skipped the current song. Playing the next song in the queue.")

    # Trigger play_next
    Bot.loop.call_soon_threadsafe(play_next_song.set)

Bot.run(TOKEN)
