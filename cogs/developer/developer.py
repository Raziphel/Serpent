
#* Discord
from discord.ext.commands import command, Cog
from discord import Member, PermissionOverwrite, Permissions, Color

#*Additions
from asyncio import sleep, iscoroutine
from time import monotonic
from datetime import datetime as dt, timedelta
from random import choice
import utils
import os
import sys
import subprocess

from asyncio import iscoroutine, gather
from traceback import format_exc


class Developer(Cog):
    def __init__(self, bot):
        self.bot = bot




    @utils.is_dev()
    @command()
    async def ev(self, ctx, *, content:str):
        """
        Runs code through Python
        """
        try:
            ans = eval(content, globals(), locals())
        except Exception:
            await ctx.send('```py\n' + format_exc() + '```')
            return
        if iscoroutine(ans):
            ans = await ans
        await ctx.send('```py\n' + str(ans) + '```')


    @utils.is_dev()
    @command(aliases=['r'])
    async def restart(self, ctx):
        """Restarts the bot"""
        msg = await ctx.send(embed=utils.Embed(title=f"Restarting..."))
        for num in range(5):
            await sleep(1)
            await msg.edit(embed=utils.Embed(title=f"Restarting in {5-num}."))
        await ctx.message.delete()
        await msg.delete()
        python = sys.executable
        os.execl(python, python, *sys.argv)


    @command()
    async def ping(self, ctx):
        """Checks bot's ping"""
        await sleep(1)
        await ctx.message.delete()
        before = monotonic()
        message = await ctx.send("Pong!")
        ping = (monotonic() - before) * 1000
        users = len(set(self.bot.get_all_members()))
        servers = len(self.bot.guilds)
        await message.edit(embed=utils.Embed(desc=f"Ping:`{int(ping)}ms`\nUsers: `{users}`\nServers: `{servers}`"))



    @utils.is_dev()
    @command()
    async def checklevels(self, ctx):
        for member in ctx.guild.members:
            await utils.UserFunctions.check_level(member)

        await ctx.send('All members have had their level roles adjusted correctly.')

    @utils.is_dev()
    @command()
    async def checkage(self, ctx):
        mod = utils.Moderation.get(ctx.author.id)
        for member in ctx.guild.members:
            for i in member.roles:
                if i.id == self.bot.config['age_roles']['adult']:
                    mod.adult = True
                    mod.child = False
                if i.id == self.bot.config['age_roles']['underage']:
                    mod.adult = False
                    mod.child = True

        await ctx.send('All members age moderation parameters have been set.')


    @utils.is_dev()
    @command()
    async def mass_verify(self, ctx):
        """Verify all users on server"""
        for member in ctx.guild.members:
            await utils.UserFunctions.verify_user(member)
            print(f'{member.name} was verified!')
        await ctx.send('All members have been verified!')





    @utils.is_dev()
    @command()
    async def sm(self, ctx):
        """send a placeholder message"""
        await ctx.message.delete()
        await ctx.send('placeholder message!')

    @utils.is_dev()
    @command()
    async def test_lottery(self, ctx):
        """Simulates a test lottery and announces a random winner without affecting real data."""
        guild = self.bot.get_guild(self.bot.config['guild_id'])

        # Get total tickets and participants (simulate this)
        total_tickets = utils.Currency.get_total_tickets()
        sorted_users = [user for user in utils.Currency.sort_tickets() if user.tickets > 0]

        # Get total tickets and participants
        sorted_users = [user for user in utils.Currency.sort_tickets() if user.tickets > 0]

        if total_tickets == 0:
            await channel.send(embed=Embed(description="No one entered the lottery this week. No winner."))
            return

        # Collect all tickets into a list for the draw
        all_tickets = []
        for user in sorted_users:
            all_tickets.extend([user.user_id] * user.tickets)

        # Select a winner
        winner_id = choice(all_tickets)
        winner = guild.get_member(winner_id)

        # Calculate winner's chance of winning
        winner_info = next(user for user in sorted_users if user.user_id == winner_id)
        win_chance = (winner_info.tickets / total_tickets) * 100

        # Announce the simulated winner with their winning chance
        embed=utils.Embed(
            title="🎉 **Simulated Lottery Winner Announcement** 🎉",
            description=(
                f"**🥳 Congratulations! To the simulated winner of this week's lottery is:**\n\n"
                f"💎 **{winner.display_name}** 💎\n\n"
                f"🎟️ **Lottery Stats:**\n"
                f"```yaml\n"
                f"- Total Tickets Purchased: {total_tickets}\n"
                f"- Total Participants: {len(sorted_users)}\n"
                f"- {winner.display_name}'s Tickets: {winner_info.tickets:,}\n"
                f"- Winning Chance: {win_chance:.2f}%\n"
                f"- Prize Amount: {lottery.coins:,} Coins\n"
                f"```\n"
                f"💰 **Enjoy your prize!** 💰"
            ),
            color=discord.Color.gold()
        )

        await ctx.send(embed=embed)



def setup(bot):
    x = Developer(bot)
    bot.add_cog(x)