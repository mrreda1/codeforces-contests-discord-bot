import os
import discord
from discord import app_commands
from dotenv import load_dotenv
import utils
import traceback


def create_embed(username, stats):
    embed = discord.Embed(
        title=f'{username}:',
        color=discord.Color.blue()
    )

    for site, score in stats.items():
        embed.add_field(name=site, value=score, inline=False)

    return embed


def run_discord_bot():

    load_dotenv()
    TOKEN = os.environ.get("DISCORD_TOKEN")
    intents = discord.Intents.all()
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

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

    @tree.command(
        name='contests',
        description='Displays a list of upcoming contests'
    )
    async def contests(interaction):
        await interaction.response.defer()
        contests_list = []
        
        try:
            contests_list = await utils.contests_list()
            message = await utils.create_contests_message(contests_list)
        except Exception as e:
            print(traceback.format_exc())
            await interaction.edit_original_response(content="Error while fetching contests")
            return

        if contests_list:
            await interaction.edit_original_response(content=message)
        else:
            await interaction.edit_original_response(content="No upcoming contests found.")

    @tree.command(
        name='userstats',
        description='Shows stats about the user',
    )
    @app_commands.describe(handle='Handle of the user')
    async def userstats(interaction, handle: str):
        await interaction.response.defer()
        stats_embed = None

        try:
            stats = await utils.user_info(handle)
            stats_embed = create_embed(handle, stats)
        except Exception as e:
            print(traceback.format_exc())

            await interaction.edit_original_response(content="Error while fetching user stats")
            return

        await interaction.edit_original_response(embed=stats_embed)

    @client.event
    async def on_ready():
        await tree.sync()
        print(f'{client.user} is now running!')

    client.run(TOKEN)
