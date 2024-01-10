import discord

@bot.command()
async def ping():
    embed = discord.Embed(
        colour=discord.Colour.dark_teal(),
        description="this is the description",
        title="this is the title"
    )
    embed.set_footer(text="this is the footer")
    embed.set_author(name="Richard", url="https://www.youtube.com")
    await ctx.send(embed=embed)
