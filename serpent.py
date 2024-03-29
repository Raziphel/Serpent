import toml
import logging

from discord.ext import commands
from discord import AllowedMentions

import utils
from utils.database import DatabaseConnection


# ! ------------------------- Serpent Main Class
class Serpent(commands.AutoShardedBot):
    def __init__(self, config_filename: str, *args, logger: logging.Logger = None, **kwargs):
        super().__init__(*args, fetch_offline_members=True, guild_subscriptions=True, allowed_mentions = AllowedMentions(roles=True, users=True, everyone=True), **kwargs)

        self.logger = logger or logging.getLogger("Serpent")
        self.config_filename = config_filename
        self.config = None
        with open(self.config_filename) as z:
            self.config = toml.load(z)

        # ! Adds all embeds to the Serpent Bot.
        utils.DefaultEmbed.bot = self
        utils.SpecialEmbed.bot = self
        utils.LogEmbed.bot = self
        utils.DevEmbed.bot = self
        utils.ProfileEmbed.bot = self
        utils.ErrorEmbed.bot = self
        utils.MailEmbed.bot = self
        utils.WarningEmbed.bot = self
        utils.QuestEmbed.bot = self

        # ! Load Functions
        utils.UserFunction.bot = self
        utils.CoinFunctions.bot = self

        self.database = DatabaseConnection
        self.database.config = self.config['database']
        self.startup_method = None
        self.connected = False

        # ! Supporters
        self.donators = ["🔥 Supporter II 🔥", "🔱 Supporter  III🔱"]

    def run(self):

        self.startup_method = self.loop.create_task(self.startup())
        super().run(self.config['token'])

    async def startup(self):
        """Load database"""

        try:  # ? Try this to prevent reseting the database on accident!
            # ! Clear cache
            utils.Moderation.all_moderation.clear()
            utils.Levels.all_levels.clear()
            utils.Currency.all_currency.clear()
            utils.Timers.all_timers.clear()
            utils.Tracking.all_tracking.clear()
            utils.Staff_Track.all_staff_track.clear()
            utils.Daily.all_dailys.clear()
            utils.Sticky.all_stickys.clear()
            utils.Items.all_items.clear()
            utils.Lottery.all_lotterys.clear()
            utils.Quests.all_quests.clear()

            # !   Collect from Database
            async with self.database() as db:
                moderation = await db('SELECT * FROM moderation')
                levels = await db('SELECT * FROM levels')
                currency = await db('SELECT * FROM currency')
                timers = await db('SELECT * FROM timers')
                tracking = await db('SELECT * FROM tracking')
                staff_track = await db('SELECT * FROM staff_track')
                daily = await db('SELECT * FROM daily')
                sticky = await db('SELECT * FROM sticky')
                items = await db('SELECT * FROM items')
                lottery = await db('SELECT * FROM lottery')
                quests = await db('SELECT * FROM quests')

            # !   Cache all into local objects
            for i in moderation:
                utils.Moderation(**i)
            for i in levels:
                utils.Levels(**i)
            for i in currency:
                utils.Currency(**i)
            for i in timers:
                utils.Timers(**i)
            for i in tracking:
                utils.Tracking(**i)
            for i in staff_track:
                utils.Staff_Track(**i)
            for i in daily:
                utils.Daily(**i)
            for i in sticky:
                utils.Sticky(**i)
            for i in items:
                utils.Items(**i)
            for i in lottery:
                utils.Lottery(**i)
            for i in quests:
                utils.Quests(**i)


        except Exception as e:
            print(f'Couldn\'t connect to the database... :: {e}')

        # ! If Razi ain't got coins the DB ain't connected correctly... lmfao
        lvl = utils.Levels.get(159516156728836097)
        if lvl.level == 0:
            self.connected = False
            print('Bot database is NOT connected!')
        else:
            self.connected = True
            print('Bot database is connected!')

        # Register slash commands
        await self.register_application_commands()
