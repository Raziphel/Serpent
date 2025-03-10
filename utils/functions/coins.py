# Discord
from discord import Member

# Utils
import utils


class CoinFunctions(object):
    bot = None
    tax_rate = 0.92


    @classmethod
    async def pay_user(cls, payer:Member, receiver:Member, amount:int, bet:bool=False):
        """Use for payment between users (Taxed)"""

        #! Define Variables
        cp = utils.Currency.get(payer.id)
        cr = utils.Currency.get(receiver.id)
        cp_r = utils.Coins_Record.get(payer.id)
        cr_r = utils.Coins_Record.get(receiver.id)

        new_amount = await cls.pay_tax(payer=payer, amount=amount)
        taxed = amount - new_amount

        #! Check they have enough coins to pay.
        if cp.coins >= amount:

            #+ Give them coins and record
            cp.coins -= amount
            cr.coins += amount
            cp_r.taxed += taxed

            if bet: #! Add it to their records!  Check if it was a bet!
                cp_r.lost += amount
                cr_r.won += amount
            else:
                cp_r.gifted += amount
                cr_r.given += amount

        async with cls.bot.database() as db:
            await cp.save(db)
            await cr.save(db)
            await cp_r.save(db)
            await cr_r.save(db)
        return taxed #? Returns the amount taxed



    @classmethod 
    async def pay_tax(cls, payer:Member, amount:int):
        """Use this method to pay the taxes for an amount then send the new amount back."""

        #! Define Variables
        cp = utils.Currency.get(payer.id)
        cr = utils.Currency.get(cls.bot.user.id)
        cp_r = utils.Coins_Record.get(payer.id)

        #! Determine tax amount
        new_amount = amount * cls.tax_rate  #? 8% Tax
        taxed = amount - new_amount

        cp.coins -= taxed
        cp_r.taxed += taxed
        cr.coins += taxed

        async with cls.bot.database() as db:
            await cp.save(db)
            await cr.save(db)
            await cp_r.save(db)
        return new_amount



    @classmethod 
    async def pay_for(cls, payer:Member, amount:int):
        """Use this method for purchases made!"""

        #! Define Variables
        cp = utils.Currency.get(payer.id)
        cr = utils.Currency.get(cls.bot.user.id)
        cp_r = utils.Coins_Record.get(payer.id)

        if cp.coins < amount:
            return False

        #+ Buy things with coins!
        cp.coins -= amount
        cp_r.spent += amount
        cr.coins += amount

        async with cls.bot.database() as db:
            await cp.save(db)
            await cr.save(db)
            await cp_r.save(db)
        return True



    @classmethod 
    async def earn(cls, earner:Member, amount:int, gift:bool=False):
        """Use this method for letting users earn coins"""

        #! Define Variables
        cu = utils.Currency.get(earner.id)
        cb = utils.Currency.get(cls.bot.user.id)
        cu_r = utils.Coins_Record.get(earner.id)

        #! Check if the bank's got coins!
        if cb.coins <= 100000:
            # ??? Make something happen...
            return

        #+ Just take it away from the bot!
        cu.coins += amount
        cb.coins -= amount

        if gift is False:
            cu_r.earned += amount
        else:
            cu_r.gifted += amount

        async with cls.bot.database() as db:
            await cu.save(db)
            await cb.save(db)
            await cu_r.save(db)
