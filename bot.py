import os
import discord
from dotenv import load_dotenv
import utils


def run_discord_bot():

    load_dotenv()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)

    @tree.command(
        name='help',
        description='Displays a list of commands'
    )
    async def help(ctx):
        commands = tree.get_commands()
        help_text = ""
        for command in commands:
            help_text += f"> **{command.name}:** {command.description}\n"
        await ctx.response.send_message(help_text)

    @tree.command(
        name='userinfo',
        description='Get user information in codeforces.'
    )
    @discord.app_commands.describe(handle='User\'s handle in codeforces.')
    async def userinfo(ctx, handle: str):
        user = utils.get_user(handle)
        if (user == 0):
            await ctx.response.send_message(f"User '{handle}'"
                                            " not found!")
        CR = f":bar_chart: **Contest rating**: {user['rating']} \
        (max, {user['maxRank']}, {user['maxRating']})"
        CNT = f":star2: **Contribution**: {user['contribution']}"
        FRND = f":star: **Friend of**: {user['friendOfCount']}"
        embed = discord.Embed(
            title=user["handle"] + "\n\n",
            url="https://codeforces.com/profile/" + user["handle"],
            description=f"ㅤ\n{CR}\n\n{CNT}\n\n{FRND}",
            color=0xFF5733
        )
        embed.set_author(name=user['rank'])
        embed.set_thumbnail(url=user["titlePhoto"])
        await ctx.response.send_message(embed=embed)

    @tree.command(
        name='contests',
        description='Displays a list of upcoming contests'
    )
    async def contests(ctx):
        try:
            await ctx.response.send_message(utils.contests_list())
        except Exception as e:
            print(e)

    @client.event
    async def on_ready():
        await tree.sync()
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} said: '{user_message}' ({channel})")

    client.run(TOKEN)
