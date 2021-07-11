from collections import Counter

import discord
from discord.ext import commands


class Commands(commands.Cog):
    """A discord.py cog containing useful stat commands.

    Attributes
    -----------
    bot: :class:`commands.Bot`
        Represents the bot used by the cog.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def history(self, ctx):
        if not self.bot.nitro_redeemer.cache:
            await ctx.send("No data to process!")
            return

        code_string = ""
        for code in self.bot.nitro_redeemer.cache:
            code_string += f"Code: {code}, {self.bot.nitro_redeemer.cache[code]}\n"

        list_strings = [code_string[i:i + 2000] for i in range(0, len(code_string), 2000)]
        for string in list_strings:
            await ctx.send(string)

    @commands.command()
    async def stats(self, ctx):
        if not self.bot.nitro_redeemer.data:
            await ctx.send("No data to process!")
            return

        embed = discord.Embed(
            title="Discord API Stats.",
            color=0x00ff00,
        )

        avg = sum(self.bot.nitro_redeemer.data) / len(self.bot.nitro_redeemer.data)
        ping_data = f"MIN: {min(self.bot.nitro_redeemer.data)}\n" \
                    f"MAX: {max(self.bot.nitro_redeemer.data)}\n" \
                    f"AVERAGE: {avg}"
        embed.add_field(name="Ping Data", value=ping_data, inline=False)

        response_data = '\n'.join(
            [f"{x[0].name}:"
             f" {x[1]}" for x in Counter(self.bot.nitro_redeemer.cache.values()).most_common()])
        embed.add_field(name="Response Data", value=response_data, inline=False)

        embed.add_field(name="Total API"
                             " Calls", value=str(len(self.bot.nitro_redeemer.data)), inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
