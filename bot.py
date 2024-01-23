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
        name='synchandle',
        description='Sync codeforces handle with discord username'
    )
    @discord.app_commands.describe(handle='Your handle in codeforces.')
    async def synchandle(ctx, handle: str):
        result = utils.synchandle(ctx.user.id, handle)
        if (result):
            await ctx.response.send_message("Your account "
                                            f"synced with '{result}'")
        else:
            await ctx.response.send_message("There is no account "
                                            f"with the handle '{handle}'")

    @tree.command(
        name='gethandle',
        description='Get codeforces handle with discord id'
    )
    @discord.app_commands.describe(id='Discord account id')
    async def gethandle(ctx, id: str):
        handle = utils.gethandle(id)
        try:
            username = await client.fetch_user(id)
        except Exception:
            await ctx.response.send_message("Wrong id")
        if (handle):
            user = utils.get_user(handle)
            embed = utils.makeUserEmbed(user)
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.response.send_message(f"{username} don't have a handle")

    @tree.command(
        name='userinfo',
        description='Get user information in codeforces.'
    )
    @discord.app_commands.describe(handle='User\'s handle in codeforces.')
    async def userinfo(ctx, handle: str):
        user = utils.get_user(handle)

        if (not user):
            await ctx.response.send_message("There is no account "
                                            f"with the handle '{handle}'")
            return

        embed = utils.makeUserEmbed(user)
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
