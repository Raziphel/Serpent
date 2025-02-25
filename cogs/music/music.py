import discord
from discord.ext.commands import command, Cog
import aiohttp
import asyncio
import uuid  # Lavalink needs a unique session ID

class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.node = {
            "host": "172.18.0.1",
            "port": 8197,
            "password": "youshallnotpass",
        }
        self.players = {}  # Tracks active players
        self.queues = {}  # Track queues
        self.session_id = str(uuid.uuid4())  # Unique session ID for Lavalink

        bot.loop.create_task(self.initialize())

    async def initialize(self):
        """Ensures HTTP session is created."""
        await self.bot.wait_until_ready()
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def create_lavalink_session(self):
        """Creates a new Lavalink session if it doesn't exist."""

        print(f"🛠 DEBUG: `create_lavalink_session()` called for session `{self.session_id}`")

        url = f"http://{self.node['host']}:{self.node['port']}/v4/sessions/{self.session_id}"
        headers = {"Authorization": self.node["password"], "Content-Type": "application/json"}

        async with self.session.patch(url, headers=headers, json={}) as response:
            print(f"📡 DEBUG: Sent PATCH request to Lavalink, received status {response.status}")

            if response.status in (200, 204):
                print(f"✅ Lavalink session `{self.session_id}` created successfully.")
                return True
            else:
                error_text = await response.text()
                print(f"❌ Lavalink session creation failed: {response.status} - {error_text}")
                return False

    async def send_lavalink(self, guild_id: int, data: dict):
        """Sends a correctly formatted update request to Lavalink."""
        url = f"http://{self.node['host']}:{self.node['port']}/v4/sessions/{self.session_id}/players/{guild_id}"
        headers = {
            "Authorization": self.node["password"],
            "Content-Type": "application/json",
        }

        print(f"📡 Sending request to Lavalink: {data}")  # Debugging log

        async with self.session.patch(url, headers=headers, json=data) as response:
            if response.status not in (200, 204):
                error_text = await response.text()
                print(f"❌ Lavalink REST Error: {error_text}")
                return None

            print(f"✅ Lavalink response: {response.status}")  # Debugging log
            return await response.json() if response.status == 200 else None


    async def search_track(self, query: str):
        """Searches for a track on Lavalink."""
        url = f"http://{self.node['host']}:{self.node['port']}/v4/loadtracks"
        headers = {"Authorization": self.node["password"]}
        params = {"identifier": f"ytsearch:{query}"}

        async with self.session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                print(f"❌ Failed to search track: {await response.text()}")
                return None

            data = await response.json()
            return data["data"][0] if data["data"] else None

    async def join_voice(self, ctx):
        """Joins a voice channel and ensures Lavalink recognizes it."""

        print("🛠 DEBUG: `join_voice()` function started")

        if not ctx.author.voice:
            print("❌ User is not in a voice channel!")
            await ctx.send("❌ You must be in a voice channel!")
            return None

        channel = ctx.author.voice.channel
        print(f"🔊 Attempting to join {channel.name}")

        if ctx.guild.voice_client:
            print("✅ Already connected to voice")
            return ctx.guild.voice_client.channel

        print(f"🚀 Connecting to {channel.name}...")
        vc = await channel.connect()
        await asyncio.sleep(2)

        print(f"✅ Successfully connected to {channel.name}")
        return vc.channel

    @command()
    async def play(self, ctx, *, query: str):
        """Plays a song. Joins voice if not already in one."""
        print(f"🎵 Play command called by {ctx.author} in {ctx.guild.name}")

        channel = await self.join_voice(ctx)
        if not channel:
            print("❌ Bot failed to join voice!")
            return

        print(f"✅ Bot joined {channel.name}")

        # ✅ First attempt to create a session
        session_created = await self.create_lavalink_session()

        # 🔄 Retry once if it fails
        if not session_created:
            print("⚠️ Session creation failed! Retrying in 3 seconds...")
            await asyncio.sleep(3)
            session_created = await self.create_lavalink_session()

        if not session_created:
            return await ctx.send("❌ Failed to create a Lavalink session. Try again later!")

        print(f"✅ Lavalink session `{self.session_id}` is ready")

        track = await self.search_track(query)
        if not track:
            return await ctx.send("❌ No results found!")

        track_id = track.get("encoded")
        if not track_id:
            return await ctx.send("❌ Failed to retrieve track data!")

        print(f"✅ Found track: {track['info']['title']}")

        payload = {
            "track": {"encoded": track_id},
            "paused": False,
            "volume": 100
        }

        print(f"📡 Sending play request to Lavalink: {payload}")
        response = await self.send_lavalink(ctx.guild.id, payload)

        if response is None:
            print("❌ Lavalink did not accept the request!")
            return await ctx.send("❌ Something went wrong with playback!")

        print("✅ Song started playing!")
        await ctx.send(f"🎵 Now playing: **{track['info']['title']}**")

    @command()
    async def stop(self, ctx):
        """Stops music, clears queue, and destroys the player session."""
        if ctx.guild.id not in self.players:
            return await ctx.send("❌ I'm not playing anything!")

        self.queues[ctx.guild.id] = []  # Clear queue
        await self.send_lavalink(ctx.guild.id, {"track": None})  # Stop playback

        # Destroy Lavalink player session
        url = f"http://{self.node['host']}:{self.node['port']}/v4/sessions/{self.session_id}/players/{ctx.guild.id}"
        headers = {"Authorization": self.node["password"]}

        async with self.session.delete(url, headers=headers) as response:
            if response.status in (200, 204):
                del self.players[ctx.guild.id]
                await ctx.guild.voice_client.disconnect()
                await ctx.send("🎵 Stopped the music and left VC!")
            else:
                await ctx.send("❌ Failed to properly stop the player!")

    @command()
    async def skip(self, ctx):
        """Skips the current song."""
        if ctx.guild.id not in self.players:
            return await ctx.send("❌ I'm not playing anything!")

        await self.send_lavalink(ctx.guild.id, {"track": None})
        await ctx.send("⏩ Skipped the song!")

    @command()
    async def leave(self, ctx):
        """Disconnects the bot from the voice channel."""
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            del self.players[ctx.guild.id]
            await ctx.send("👋 Left the voice channel!")

def setup(bot):
    bot.add_cog(Music(bot))
