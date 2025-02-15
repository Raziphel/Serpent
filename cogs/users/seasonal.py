from discord import ApplicationCommandOption, ApplicationCommandOptionType, Member, Embed, Color
from discord.ext.commands import command, cooldown, BucketType, Cog, ApplicationCommandMeta

from random import choice, randint
from datetime import datetime as dt, timedelta
import utils

class Seasonal(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.presents = [
            "🎁 Box of Chocolates",
            "🎄 Holiday Ornament",
            "🍪 Christmas Cookies",
            "☕ Warm Hot Cocoa",
            "🍫 Chocolate Coins",
            "✨ Sparkling Tinsel",
            "🧦 Cozy Socks",
            "🧸 Teddy Bear",
            "🎅 Santa Hat",
            "🕯️ Festive Candle"
        ]
        self.treats = [
            "🍬 Candy",
            "🍫 Chocolate",
            "🍭 Lollipop",
            "🍪 Cookie",
            "🍩 Donut",
            "🍰 Cake",
            "🍯 Honeycomb",
            "🍎 Candy Apple",
            "🍡 Mochi",
            "🍦 Ice Cream"
        ]
        self.tricks = [
            "👻 Spooky Ghost",
            "🕷️ Spider",
            "💀 Skeleton",
            "🎃 Evil Pumpkin",
            "🐍 Snake",
            "🦇 Bat",
            "🧟 Zombie",
            "🧛 Vampire",
            "👹 Demon",
            "🌕 Full Moon Werewolf"
        ]



    @cooldown(1, 7200, BucketType.user)  # 2-hour cooldown per user
    @command(application_command_meta=ApplicationCommandMeta())
    async def trick_or_treat(self, ctx):
        """Get a trick or get a treat!"""

        # Get user's coins record
        coins_record = utils.Coins_Record.get(ctx.author.id)

        # Decide if the user gets a treat or a trick
        outcome = choice(["treat", "trick"])

        # Check if it's October (October is month 10)
        current_month = dt.now().month
        if current_month != 10:
            await ctx.send(
                f"**🎉 {ctx.author.mention}, you can only trick or treat in October!**"
            )
            return

        if outcome == "treat":
            # User gets coins as a treat
            coins = randint(2000, 6000)  # Random amount of coins
            treat = choice(self.treats)
            await ctx.send(
                f"**🎉 {ctx.author.mention}, you went trick-or-treating and got a treat: {treat}! You earned {coins:,} coins!**"
            )
            # Update user's coins using CoinFunctions
            await utils.CoinFunctions.earn(earner=ctx.author, amount=coins)

        else:
            # User loses coins as a trick
            coins = randint(1000, 4000)  # Random amount of coins lost
            trick = choice(self.tricks)
            await ctx.send(
                f"**😈 {ctx.author.mention}, you went trick-or-treating and got a trick: {trick}! You lost {coins:,} coins!**"
            )
            # Retrieve user's currency and reduce their coins
            c = utils.Currency.get(ctx.author.id)
            c.coins -= coins

            # Update coins record for lost coins
            coins_record.lost += coins

            # Save the reduced currency to the database
            async with self.bot.database() as db:
                await c.save(db)

        # Save the coins record to the database
        async with self.bot.database() as db:
            await coins_record.save(db)

















    @cooldown(1, 7200, BucketType.user)  # 2-hour cooldown per user
    @command(
        application_command_meta=ApplicationCommandMeta(
            options=[
                ApplicationCommandOption(
                    name="recipient",
                    description="The user you want to give a gift to.",
                    type=ApplicationCommandOptionType.user,
                    required=True,
                ),
            ],
        ),
    )
    async def give_present(self, ctx, recipient: Member):
        """Give a random holiday present to your friends!"""

        # Ensure the command can only be used in November and December
        current_month = dt.now().month
        if current_month not in [11, 12]:
            await ctx.send(
                f"**🎄 {ctx.author.mention}, you can only give holiday presents in November and December!**"
            )
            return

        # Check if the member is the author or a bot
        if recipient == ctx.author:
            await ctx.send(
                f"**🚫 {ctx.author.mention}, you can't give a present to yourself!**"
            )
            return
        if recipient.bot:
            await ctx.send(
                f"**🤖 {ctx.author.mention}, you can't give a present to a bot!**"
            )
            return

        # Randomly determine coin amount and present
        coins = randint(1000, 5000)  # Random amount of coins to give
        present = choice(self.presents)

        # Message to show who gave what to whom!
        await ctx.send(
            f"**🎁 {ctx.author.mention} gave {recipient.mention} a present: {present}! {recipient.display_name} received {coins:,} coins!**"
        )

        # Update recipient's coins using CoinFunctions
        await utils.CoinFunctions.earn(earner=recipient, amount=coins, gift=True)


        # Update the seasonal record
        seasonal_record = utils.Seasonal.get(ctx.author.id)
        seasonal_record.presents_coins_given += coins
        seasonal_record.presents_given += 1

        # Save the coins record to the database
        async with self.bot.database() as db:
            await seasonal_record.save(db)


    @command(application_command_meta=ApplicationCommandMeta())
    async def present_leaderboard(self, ctx):
        """
        Show the leaderboard for the holiday gift givers!
        """
        # Get sorted leaderboard by presents
        sorted_leaderboard = utils.Seasonal.sort_presents_given()

        coin_e = self.bot.config['emojis']['coin']

        # Build the leaderboard description
        leaderboard_description = "🎁 **Top Gift Givers**\n\n"
        for idx, user in enumerate(sorted_leaderboard[:10], start=1):
            # Fetch user object using bot's cache or fallback to user_id
            member = ctx.guild.get_member(user.user_id) or f"User {user.user_id}"
            leaderboard_description += (
                f"**#{idx} {member}** - "
                f"🎁 Given: **{user.presents_given:,}** | "
                f"{coin_e} Gifted: **{user.presents_coins_given:,}**\n"
            )

        # Create embed for the leaderboard
        embed = Embed(
            title="🎉 Holiday Gift Givers Leaderboard 🎉",
            description=leaderboard_description,
            color=Color.green()
        )

        # Send the embed
        await ctx.send(embed=embed)

    @utils.is_dev()
    @command(application_command_meta=ApplicationCommandMeta())
    async def holiday_rewards(self, ctx):
        """
        Give everyone 5x the coins they gifted during the holiday season!
        """
        # Access all seasonal records
        all_records = utils.Seasonal.all_seasonal.values()

        # Track total coins distributed
        total_distributed = 0

        # Database connection for updates
        async with self.bot.database() as db:
            # Iterate through all records to calculate and distribute rewards
            for record in all_records:
                if record.presents_coins_given > 0:
                    reward = record.presents_coins_given * 5
                    total_distributed += reward

                    # Use the CoinFunctions.earn function to update the user's balance
                    user = ctx.guild.get_member(record.user_id)
                    if user:
                        await utils.CoinFunctions.earn(earner=user, amount=reward, gift=True)

                        # DM the user their reward
                        try:
                            await user.send(
                                f"🎉 **Holiday Rewards!** You've received {reward:,} coins as a reward for your generosity this season! 🎁"
                            )
                        except:
                            pass  # Handle cases where DMs are closed or fail to send

                    # Update the seasonal record
                    record.presents_coins_given += reward
                    await record.save(db)

        # Send a summary message in the channel
        await ctx.send(
            f"**🎄 The Holiday Rewards is complete! A total of {total_distributed:,} coins have been distributed to all participants. Thank you for your generosity! 🎉**"
        )














# The setup function to load the cog
def setup(bot):
    bot.add_cog(Seasonal(bot))
