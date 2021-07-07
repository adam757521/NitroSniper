from discord.ext import commands
import discord


class Commands(commands.Cog):
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
        embed.add_field(name="MIN:", value=min(self.bot.nitro_redeemer.data))
        embed.add_field(name="MAX:", value=max(self.bot.nitro_redeemer.data))
        embed.add_field(name="AVG:", value=sum(self.bot.nitro_redeemer.data) / len(self.bot.nitro_redeemer.data))

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
