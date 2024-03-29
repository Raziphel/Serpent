
#* Discord
from discord.ext.commands import command, Cog, BucketType, cooldown, group, RoleConverter, ApplicationCommandMeta
from discord import Member, Message, User, Game, Embed, TextChannel, Role, RawReactionActionEvent, ApplicationCommandOption, ApplicationCommandOptionType

#* Additions
from datetime import datetime as dt, timedelta
from asyncio import iscoroutine, gather, sleep
from math import floor 
from random import choice, randint

import utils

class Items(Cog):

    def __init__(self, bot):
        self.bot = bot
        # self.restart_cooldown = dt.utcnow()




    @cooldown(1, 3600, BucketType.user)
    @command(        
        aliases=['yoink'],
        application_command_meta=ApplicationCommandMeta(
            options=[
                ApplicationCommandOption(
                    name="user",
                    description="The user you would like to steal from!",
                    type=ApplicationCommandOptionType.user,
                    required=False,
                ),
            ],
        ),
    )
    async def steal(self, ctx, user:Member=None):
        '''
        Use your gloves to steal from other users!!
        '''

        # if (self.restart_cooldown + timedelta(minutes=60)) >= dt.utcnow():
        #     tf = self.restart_cooldown + timedelta(minutes=60)
        #     t = dt(1, 1, 1) + (tf - dt.utcnow())
        #     await ctx.send(embed=utils.DefaultEmbed(title=f"Stealing is on cooldown for another 60 minutes!", description=f"this is due to the bot restarting recently!\n\nYou can steal again in {t.minute} minutes!"))
        #     return

        if user is None:
            await ctx.interaction.response.send_message(embed=utils.DefaultEmbed(title=f"You didn't say who your stealing from?", desc=f"**Stealing Odds:**\nSteal 5,000\nSteal 10,000\nSteal 15,000\nSteal 2%\nSteal 3%\nLose 5,000\nLose 2%"))
            self.steal.reset_cooldown(ctx)
            return

        if user.id == self.bot.user.id:
            await ctx.interaction.response.send_message(embed=utils.DefaultEmbed(title=f"You can't steal from the master of thiefs!"))
            self.steal.reset_cooldown(ctx)
            return

        if user.id == ctx.author.id:
            await ctx.interaction.response.send_message(embed=utils.DefaultEmbed(title=f"You can't steal from yourself!"))
            self.steal.reset_cooldown(ctx)
            return

        #! Define Varibles
        chance = choice(['5,000', '10,000', '15,000' '2%', '3%', '-5,000', '-2%'])
        c = utils.Currency.get(ctx.author.id)
        uc = utils.Currency.get(user.id)
        item = utils.Items.get(ctx.author.id)
        items = utils.Items.get(user.id)

        if item.thief_gloves <= 0:
            await ctx.interaction.response.send_message(embed=utils.DefaultEmbed(title=f"You don't have any gloves!"))
            self.steal.reset_cooldown(ctx)
            return

        if items.thief_gloves <= 0:
            await ctx.interaction.response.send_message(embed=utils.DefaultEmbed(title=f"They don't own gloves and can't be stolen from!"))
            self.steal.reset_cooldown(ctx)
            return

        item.thief_gloves -= 1
        coins_stole = None
        coins_lost = None

        if chance == '5,000':
            coins_stole = 5000
            if uc.coins < coins_stole:
                coins_stole = uc.coins
            else:
                uc.coins -= coins_stole
                c.coins += coins_stole

        elif chance == '10,000':
            coins_stole = 10000
            if uc.coins < coins_stole:
                coins_stole = uc.coins
            else:
                uc.coins -= coins_stole
                c.coins += coins_stole

        elif chance == '15,000':
            coins_stole = 15000
            if uc.coins < coins_stole:
                coins_stole = uc.coins
            else:
                uc.coins -= coins_stole
                c.coins += coins_stole

        elif chance == '2%':
            coins_stole = floor(uc.coins*0.02)
            uc.coins -= coins_stole
            c.coins += coins_stole


        elif chance == '3%':
            coins_stole = floor(uc.coins*0.03)
            uc.coins -= coins_stole
            c.coins += coins_stole


        elif chance == '-2%':
            coins_stole = floor(uc.coins*0.02)
            uc.coins -= coins_stole
            c.coins += coins_stole

        elif chance == '-5,000':
            coins_lost = 5000
            if c.coins < coins_lost:
                coins_lost = c.coins
            else:
                uc.coins += coins_lost
                c.coins -= coins_lost

        coin_e = self.bot.config['emotes']['coin']

        coin_logs = self.bot.get_channel(self.bot.config['channels']['coin_logs'])
        if coins_lost != None:
            await ctx.interaction.response.send_message(
                content=f"{user.mention}", embed=utils.DefaultEmbed(title=f"🧤 Coins Stolen 🧤", desc=f"**{ctx.author}** tried to steal coins from **{user.name}** but, they lost **{coins_lost:,}** {coin_e} to them instead..."))
            await coin_logs.send(f"**{ctx.author}** tried to steal coins from **{user}** but, they lost **{coins_lost:,}** {coin_e} to them instead...")

        elif coins_stole != None:
            await ctx.interaction.response.send_message(
                content=f"{user.mention}", embed=utils.DefaultEmbed(title=f"🧤 Coins Stolen 🧤", desc=f"**{ctx.author}** Stole coins from **{user.name}** and they gained **{coins_stole:,}** {coin_e}"))
            await coin_logs.send(f"**{ctx.author}** Stole coins from **{user}** and they gained **{coins_stole:,}** {coin_e}")

        

        #! Quest 5 Complete
        await self.bot.get_cog('Quests').get_quest(user=ctx.author, quest_no=5, completed=True)


        async with self.bot.database() as db:
            await item.save(db)
            await c.save(db)
            await uc.save(db)





    # @command(aliases=['se', 'party', 'event'])
    # async def start_event(self, ctx):
    #     '''Starts a random event'''
    #     channel_id = str(ctx.channel.id)
    #     item = utils.Items.get(ctx.author.id)

    #     #! Quest 6 Complete
    #     await self.bot.get_cog('Quests').get_quest(user=ctx.author, quest_no=6, completed=True)

    #     #! Check for Party Poppers
    #     if item.party_popper <= 0:
    #         #! Check if its Razi
    #         if ctx.author.id != 159516156728836097:
    #             await ctx.send(embed=utils.DefaultEmbed(title=f"You don't have any Party Poppers!"))
    #             item.party_popper += 1
    #             return


    #     await self.bot.get_cog('event_handler').create_event(user=ctx.author, channel_id=channel_id, channel=ctx.channel)





def setup(bot):
    x = Items(bot)
    bot.add_cog(x)