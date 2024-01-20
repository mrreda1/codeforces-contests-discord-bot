import os
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import utils
import traceback
import pytz


contests_cache = []
reminders_sent = set()
reminder_channel = {}
reminder_time = timedelta(minutes=15)


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

    @tasks.loop(minutes=1)
    async def check_contests():
        global reminder_channel, contests_cache, reminders_sent

        if not reminder_channel:
            check_contests.cancel()
            return

        try:
            now = datetime.now(pytz.timezone("Africa/Cairo"))

            # Call the API only if the cache is empty
            if not contests_cache:
                print("Fetching contests")
                contests_cache = await utils.get_upcoming_contests()

            for contest in contests_cache.copy():
                contest_time = contest["start_time"]
                time_diff = contest_time - now

                for server_id, channel in reminder_channel.items():
                    if timedelta(minutes=1) >= abs(time_diff - reminder_time) and contest['id'] not in reminders_sent:
                        try:
                            await channel.send(f"@everyone **:alarm_clock: | [{contest['name']}](<{contest['event_url']}>) starts in 15 minutes**")
                        except:
                            print(traceback.format_exc())

                        reminders_sent.add(contest['id'])

                if time_diff <= timedelta(minutes=5):
                    contests_cache.remove(contest)

        except Exception as e:
            print(traceback.format_exc())

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
            contests_list = await utils.get_upcoming_contests()
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
            stats = await utils.get_user_info(handle)
            stats_embed = create_embed(handle, stats)
        except Exception as e:
            print(traceback.format_exc())

            await interaction.edit_original_response(content="Error while fetching user stats")
            return

        await interaction.edit_original_response(embed=stats_embed)

    @tree.command(
        name='set_reminder_channel',
        description='Sets the channel to send reminders in',
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_reminder_channel(interaction, channel: discord.TextChannel):
        global reminder_channel
        server_id = interaction.guild.id
        reminder_channel[server_id] = channel
        await interaction.response.send_message(f"Reminder channel set to {channel.mention}")
        check_contests.start()

    @set_reminder_channel.error
    async def on_set_reminder_channel_error(interaction, error):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

    @client.event
    async def on_ready():
        await tree.sync()
        print(f'{client.user} is now running!')

    client.run(TOKEN)
