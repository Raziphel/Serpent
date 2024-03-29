
#* Discord
from discord import Embed
#* Additions
from random import randint, choice

import utils

class SpecialEmbed(Embed):

    bot = None

    def __init__(self, *args, **kwargs):
        #* Gets the varibles for the embed
        title = kwargs.pop('title', None)
        desc = kwargs.pop('desc', None)
        thumbnail = kwargs.pop('thumbnail', None)
        footer = kwargs.pop('footer', None)
        guild = kwargs.pop('guild', None)
        color = kwargs.pop('color', None)
        patron = self.bot.config['patreon']


        #! Make the embed
        super().__init__(*args, **kwargs)

        #* Add Color
        if color == None:
            self.color = randint(1, 0xffffff) #? Random color
        else: self.color = color

        #* Add title
        if title:
            self.set_author(name=title, url=patron)

        #* Add description
        if desc:
            self.description = desc

        if thumbnail:
            self.set_thumbnail(url=thumbnail)

        if footer:
            self.set_footer(text=footer)
        else:
            self.set_footer(text="🍀 " + choice(utils.Tips))
