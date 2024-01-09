import discord
from discord import app_commands
import utils


TOKEN = 'MTE5NDE1MDk5OTY4NjkxNDA3OQ.'\
        'GN0DI2.V2XTsOnvk_i8p3qOj5qINyBMdahDG3I380aaas'
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@tree.command(
    name='hello',
    description='Says hello to the user'
)
async def hello(interaction):
    await interaction.response.send_message('Hello!')


@tree.command(
    name='help',
    description='Displays a list of commands'
)
async def help(interaction):
    await interaction.response.send_message('Help!')
    await interaction.response.send_message(tree.get_commands())


@tree.command(
    name='contests',
    description='Displays a list of upcoming contests'
)
async def contests(interaction):
    await interaction.response.send_message(utils.main())


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
