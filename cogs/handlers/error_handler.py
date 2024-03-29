
#* Discord
from discord.ext.commands import Cog
from discord.ext.commands import BadArgument, CommandNotFound, CommandOnCooldown, MissingPermissions, IsNotSlashCommand
#* Utils
import utils
#* Additions
from asyncio import sleep



class Error_Handler(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        '''Globally handles errors around the bot'''

        if isinstance(error, CommandOnCooldown):
            countdown_time = error.retry_after
            guild = self.bot.get_guild(self.bot.config['garden_id']) #? Guild

            for role in ctx.author.roles:
                if role.id == self.bot.config['roles']['supporters'] or ctx.author.id in self.bot.config['developers'].values():
                    await ctx.send("*Bypassing Cooldowns. Thanks for supporting!*")
                    await ctx.reinvoke()
                    return
            if countdown_time <= 60:
                msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Command Cooldown", desc=f"Please try again in {countdown_time:.2f} seconds!"))
            else:
                msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Command Cooldown", desc=f"Please try again in {countdown_time // 60:.0f} minutes {countdown_time % 60:.0f} seconds!"))
                pass

        elif isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingPermissions):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Ya don't have the right Server Permission!"))
            pass
        elif isinstance(error, BadArgument):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Ya gave Incorrect Command Arguments!?"))
            pass
        elif isinstance(error, utils.InDmsCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"This command can only be ran in my Dms!"))
            pass
        elif isinstance(error, utils.UserCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Only someone special can run this command!"))
            pass
        elif isinstance(error, utils.DevCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Only the Bot Developer can run this command!"))
            pass
        elif isinstance(error, utils.GuildCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"This isn't the right Discord Server for this command."))
            pass
        elif isinstance(error, utils.NSFWCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"An NSFW Error Occured."))
            pass
        elif isinstance(error, utils.ModStaffCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Only a Moderator can run this command!"))
            pass
        elif isinstance(error, utils.AdminStaffCheckError):
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Only an Administrator can run this command!"))
            pass
        else: 
            msg = await ctx.send(embed=utils.ErrorEmbed(error_msg=f"Something unexpected happened?"))
            pass

        if ctx.author.id in self.bot.config['developers'].values():
            await ctx.author.send(f"Command failed - `{error!s}`;")

        await sleep(4)
        try:
            await msg.delete()
            await ctx.message.delete()
        except: pass

def setup(bot):
    x = Error_Handler(bot)
    bot.add_cog(x)
