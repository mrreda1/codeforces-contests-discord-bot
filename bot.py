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
    async def help(interaction):
        commands = tree.get_commands()
        help_text = ""
        for command in commands:
            help_text += f"> **{command.name}:** {command.description}\n"
        await interaction.response.send_message(help_text)

    # @tree.command(
    #     name='ping',
    #     description='test command'
    # )
    # async def ping(interaction, handle):
    #     embed = discord.Embed(
    #         colour=discord.Colour.dark_teal(),
    #         description="this is the description",
    #         title="this is the title"
    #     )
    #     result = utils.get_user(handle)
    #     user = result["result"][0]["handle"]
    #
    #     embed.set_author(name=user, url="https://www.youtube.com")
    #     await interaction.response.send_message(embed=embed)

    @tree.command(
        name='contests',
        description='Displays a list of upcoming contests'
    )
    async def contests(interaction):
        try:
            await interaction.response.send_message(utils.contests_list())
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
