# Discord
from discord.ext.commands import command, Cog, BucketType, cooldown, group, RoleConverter, ApplicationCommandMeta
from discord import Member, Message, User, Game, TextChannel, Role, RawReactionActionEvent, Embed

# Additions
from datetime import datetime as dt, timedelta
from asyncio import iscoroutine, gather, sleep
from math import floor 
from random import choice, randint

import utils


class Supporters(Cog):

    def __init__(self, bot):
        self.bot = bot

    @property  # ! The members logs
    def coin_logs(self):
        return self.bot.get_channel(self.bot.config['channels']['coin_logs'])  # ?Coins log channel



    @command(application_command_meta=ApplicationCommandMeta(), aliases=['Monthly', 'claim', "Claim"])
    async def monthly(self, ctx):
        '''Supporters monthly claim of rewards!'''

        #! Define some mother fuckign varibles.
        guild = self.bot.get_guild(self.bot.config['garden_id']) #? Guild
        day = utils.Daily.get(ctx.author.id)
        c = utils.Currency.get(ctx.author.id)
        nitro = utils.DiscordGet(guild.roles, id=self.bot.config['roles']['nitro'])
        t1 = utils.DiscordGet(guild.roles, id=self.bot.config['roles']['t1'])
        t2 = utils.DiscordGet(guild.roles, id=self.bot.config['roles']['t2'])
        t3 = utils.DiscordGet(guild.roles, id=self.bot.config['roles']['t3'])
        supporterroles = [nitro, t1, t2, t3]

        #? Lets check if they are a supporter...
        supporter = False
        for role in ctx.author.roles:
            if role in supporterroles:
                supporter = True
                break

        #? Fuck em if they ain't a supporter.
        if supporter == False:
            await ctx.interaction.response.send_message(f"**Only supporters can claim a monthly reward!**")
            return

        #! Check if it's first daily
        if day.monthly == None:
            day.monthly = (dt.utcnow() - timedelta(days=31))

        #! Check if already claimed
        if (day.monthly + timedelta(days=29)) >= dt.utcnow():
            tf = day.monthly + timedelta(days=29)
            t = dt(1, 1, 1) + (tf - dt.utcnow())
            await ctx.interaction.response.send_message(f"**You can claim your monthly rewards in {t.day} days and {t.hour} hours!**")
            return

        reward = 0
        #+ Determine and give rewards!
        if nitro in ctx.author.roles:
            reward = 10000
        if t1 in ctx.author.roles:
            reward = 20000
        if t2 in ctx.author.roles:
            reward = 30000
        if t3 in ctx.author.roles:
            reward = 40000
        c.coins += reward
        day.monthly = dt.utcnow()
        async with self.bot.database() as db:
            await c.save(db)
            await day.save(db)

        coin_e = self.bot.config['emotes']['coin']

        await ctx.interaction.response.send_message(
            embed=utils.SpecialEmbed(
                title=f"Monthly Reward Claim!",
                desc=f"**Thanks for being a supporter!**\n\nGranted: **{reward:,} {coin_e}**"
            ))

        await self.coin_logs.send(f"**{ctx.author}** was Granted **{reward:,} {coin_e}** for his monthly!")






def setup(bot):
    x = Supporters(bot)
    bot.add_cog(x)