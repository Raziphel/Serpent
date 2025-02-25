import discord
from discord.ext.commands import Cog, command
import aiohttp
import asyncio


class Music(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.lavalink_ws = None
        self.node = {
            "host": "172.18.0.1",
            "port": 8197,
            "password": "youshallnotpass",
        }
        self.players = {}  # Keeps track of guild music states
        self.queues = {}  # New: Track queues for each guild

        self.bot.loop.create_task(self.initialize())

    async def initialize(self):
        """Ensures session is created and connects to Lavalink."""
        await self.bot.wait_until_ready()
        if self.session is None:
            self.session = aiohttp.ClientSession()
        await self.connect_lavalink()

    async def connect_lavalink(self):
        """Connects to the Lavalink WebSocket with auto-reconnect."""
        while True:
            try:
                self.lavalink_ws = await self.session.ws_connect(
                    f"http://{self.node['host']}:{self.node['port']}/v4/websocket",
                    headers={
                        "Authorization": self.node["password"],
                        "User-Id": str(self.bot.user.id),
                    }
                )
                print("🎶 Connected to Lavalink!")
                return
            except aiohttp.ClientError:
                print("⚠️ Failed to connect to Lavalink. Retrying in 5 seconds...")
                await asyncio.sleep(5)

    async def send_ws(self, data: dict):
        """Sends a JSON payload to Lavalink."""
        if self.lavalink_ws:
            await self.lavalink_ws.send_json(data)

    async def search_track(self, query: str):
        """Searches for a track on YouTube using Lavalink."""
        async with self.session.get(
            f"http://{self.node['host']}:{self.node['port']}/v4/loadtracks",
            params={"identifier": f"ytsearch:{query}"},
            headers={"Authorization": self.node["password"]}
        ) as response:
            try:
                data = await response.json()
            except Exception as e:
                print(f"❌ Error parsing Lavalink response: {e}")
                return None

            if "tracks" not in data or not isinstance(data["tracks"], list) or not data["tracks"]:
                print(f"❌ Lavalink returned an unexpected response: {data}")
                return None

            return data["tracks"][0]  # Return first search result

    async def join_voice(self, ctx):
        """Joins the user's voice channel if not already connected."""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return None

        channel = ctx.author.voice.channel
        if ctx.guild.voice_client:
            return ctx.guild.voice_client.channel  # Already connected

        self.players[ctx.guild.id] = {"channel": channel.id}
        self.queues[ctx.guild.id] = []  # Initialize queue

        await self.send_ws({
            "op": "voiceUpdate",
            "guildId": str(ctx.guild.id),
            "channelId": str(channel.id)
        })

        await ctx.send(f"🎶 Joined **{channel.name}**!")
        return channel

    @command()
    async def play(self, ctx, *, query: str):
        """Plays a song or adds it to the queue."""
        channel = await self.join_voice(ctx)
        if not channel:
            return

        track = await self.search_track(query)
        if not track:
            return await ctx.send("❌ No results found!")

        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []

        self.queues[ctx.guild.id].append(track)

        if len(self.queues[ctx.guild.id]) == 1:  # Start playing if queue was empty
            await self.play_next(ctx)

        await ctx.send(f"🎵 Added to queue: **{track['info']['title']}**")

    async def play_next(self, ctx):
        """Plays the next song in the queue."""
        if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
            return

        track = self.queues[ctx.guild.id].pop(0)

        await self.send_ws({
            "op": "play",
            "guildId": str(ctx.guild.id),
            "track": track["track"]
        })

        await ctx.send(f"🎵 Now playing: **{track['info']['title']}**")

    @command()
    async def queue(self, ctx):
        """Displays the queue."""
        if ctx.guild.id not in self.queues or not self.queues[ctx.guild.id]:
            return await ctx.send("📭 The queue is empty!")

        queue_list = "\n".join(
            [f"{i+1}. {track['info']['title']}" for i, track in enumerate(self.queues[ctx.guild.id])]
        )

        embed = discord.Embed(title="🎶 Music Queue", description=queue_list, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @command()
    async def stop(self, ctx):
        """Stops music and clears the queue."""
        if ctx.guild.id not in self.players:
            return await ctx.send("❌ I'm not playing anything!")

        self.queues[ctx.guild.id] = []  # Clear queue

        await self.send_ws({
            "op": "stop",
            "guildId": str(ctx.guild.id)
        })

        await ctx.send("🎵 Stopped the music and cleared the queue!")

        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            del self.players[ctx.guild.id]

    @command()
    async def skip(self, ctx):
        """Skips the current song and plays the next one."""
        if ctx.guild.id not in self.players:
            return await ctx.send("❌ I'm not playing anything!")

        await self.send_ws({
            "op": "stop",
            "guildId": str(ctx.guild.id)
        })

        await ctx.send("⏩ Skipped the song!")

        await self.play_next(ctx)  # Play next song in queue

    @command()
    async def leave(self, ctx):
        """Makes the bot leave the voice channel."""
        if ctx.guild.id not in self.players:
            return await ctx.send("❌ I'm not in a voice channel!")

        await self.send_ws({
            "op": "destroy",
            "guildId": str(ctx.guild.id)
        })

        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()

        del self.players[ctx.guild.id]
        del self.queues[ctx.guild.id]
        await ctx.send("👋 Left the voice channel!")


def setup(bot):
    """Loads the cog into the bot."""
    bot.add_cog(Music(bot))
