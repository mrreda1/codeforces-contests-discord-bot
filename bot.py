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
        rankcolor = ""

        colors = {"newbie": 0xCCCCCC, "legendary grandmaster": 0xAA0000,
                  "pupil": 0x77FF77, "international grandmaster": 0xFF3333,
                  "expert": 0xAAAAFF, "candidate master": 0xFF88FF,
                  "master": 0xFFCC88, "international master": 0xFFBB55,
                  "grandmaster": 0xFF7777, "specialist": 0x77DDBB}

        if (user == ""):
            await ctx.response.send_message("There is no account "
                                            f"with the handle '{handle}'")
            return
        try:
            CR = f":bar_chart: **Contest rating**: {user['rating']} \
            (max, {user['maxRank']}, {user['maxRating']})ㅤ"
            rankcolor = colors.get(user['rank'])
        except Exception:
            CR = ":bar_chart: **Contest rating**: 0ㅤㅤㅤ"
            rankcolor = 0

        CNT = f":star2: **Contribution**: {user['contribution']}"
        FRND = f":star: **Friend of**: {user['friendOfCount']}"
        embed = discord.Embed(
            title=user["handle"] + "\n\n",
            url="https://codeforces.com/profile/" + user["handle"],
            description=f"ㅤ\n{CR}\n\n{CNT}\n\n{FRND}",
            color=rankcolor
        )
        try:
            embed.set_author(name=user['rank'].title())
        except Exception:
            embed.set_author(name="Unrated")

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
