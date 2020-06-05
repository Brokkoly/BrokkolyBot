# TODO In chat maintenance of the string library
# todo separate the commands by server. give yourself the ability to add commands to the master list

import random
import atexit
import re
import discord
from importlib import util
import os

TOKEN = None
token_spec = util.find_spec('tokens')
if token_spec is not None:
    import tokens

    TOKEN = tokens.TOKEN
else:
    TOKEN = os.environ['TOKEN']

ready = False
client = discord.Client()

brokkoly_favicon = None
command_map = None
last_message_time = {}
random.seed()

# ids and constants
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528
bot_database_channel_id = 718205785888260139
game_jazz_id = 639124326385188864
author_whitelist = [  # TODO Check roles instead of just ids. Maybe give people in the bot server the ability
    146687253370896385  # me
    , 115626912394510343  # ori
    , 200773608094564352  # wind
    , 115602332863037443  # thaya
    , 185287142388400129  # thalia
    , 120756475768471554  # solyra
]
protected_commands = ["!help", "!add", "!estop", "!otherservers"]
after_add_regex_string = r'(?<!.)(?!![aA]dd)![A-zA-Z]{3,} .+'  # we've already stripped "!add" from the message
after_add_compiled_regex = re.compile(after_add_regex_string)
timeout = {
    mtg_legacy_discord_id: 60,
    brokkolys_bot_testing_zone_id: 5
}


@client.event
async def on_message(message):
    global brokkoly_favicon
    # Don't reply to our own messages
    if message.author == client.user:
        return
    if not message.content.startswith("!"):
        return
    if message.content.startswith("!estop") and message.author.id in author_whitelist:
        brokkoly = client.get_user(146687253370896385)
        brokkoly_dm = await brokkoly.create_dm()
        await brokkoly_dm.send("Emergency Stop Called. Send Help.")
        await message.channel.send(
            "@brokkoly#0001 Emergency Stop Called. Send Help.\n<:notlikeduck:522871146694311937>\n<:Heck:651250241722515459>")
        quit()

    if message.content.startswith("!help"):
        response = "Available Commands:\n" \
                   "!help - You obviously know this\n" \
                   "!add - Add a new command. Syntax: !add !<command> <message>\n" \
                   "!otherservers - Display the link to the other servers spreadsheet.\n" \
                   "See my code: https://github.com/Brokkoly/BrokkolyBot\n" \
                   "Plus comments about the following subjects:"
        for key in command_map:
            if key == "!otherservers":
                continue
            response = response + "\n" + key
        user_dm_channel = await message.author.create_dm()
        await user_dm_channel.send(response)
        await message.add_reaction("📧")
        return

    if (message.content.startswith("!add ")):
        await handle_add(message)

    command = message.content.lower()
    if command in command_map:
        msg = random.choice(command_map[command])
        await message.channel.send(msg)
        if message.guild.id in last_message_time and message.guild.id in timeout and \
                not (message.created_at - last_message_time[message.guild.id]).total_seconds() > timeout[
                    message.guild.id]:
            return
        else:
            last_message_time[message.guild.id] = message.created_at

    '''
    if message.guild.id == game_jazz_id and message.content.startswith("!gamejazz"):
        """If you're reading this go listen to game jazz, it's a good podcast"""
        # TODO load random game type
        # TODO load random game modifier
        # TODO send great game idea
        # TODO syntax and proper detection of plurals
        return
    '''


@client.event
async def on_ready():
    global command_map
    await client.get_channel(225374061386006528).send("Starting Up")
    command_map = await get_quotes_from_discord()
    await client.get_channel(225374061386006528).send("Online")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def handle_add(message):
    if (message.author.id in author_whitelist):
        if len(message.mentions) > 0 or len(message.role_mentions) > 0 or message.mention_everyone:
            await reject_message(message, "Error! No mentions allowed.")
            return
        result = parse_add(message.content)
        if result[0]:
            command = result[1]
            new_entry = result[2]
            if len(command) > 21:
                await reject_message(message, "Error! Command cannot be longer than 20 characters.")
                return
            if len(new_entry) > 500:
                await reject_message(message, "Error! Message cannot be longer than 500 characters.")
                return
            command = command.lower()
            if command in protected_commands:
                await reject_message(message, "Error! That is a protected command")
                return
            await add_quote_to_discord(command, new_entry)
            add_to_map(command_map, command, new_entry)
            await message.add_reaction(client.get_emoji(445805262880899075))
            return
        else:
            await reject_message(message, "Error! Expected \"!add !<command length at least 3> <message>\".")
            return
    else:
        await reject_message(message, "Error! Insufficient privileges to add.", True)


async def reject_message(message, error, show_message=True):
    await message.add_reaction("❌")
    if show_message:
        await message.channel.send(error)


def parse_add(content):
    string_to_parse = content[5:]  # Cut off the add since we've already matched
    if re.fullmatch(after_add_compiled_regex, string_to_parse):
        first_space = string_to_parse.find(" ")
        command = string_to_parse[:first_space]
        message = string_to_parse[first_space + 1:]
        return [True, command, message]
    else:
        return [False]


def add_to_map(command_map_to_add_to, command, message):
    if command not in command_map_to_add_to:
        command_map_to_add_to[command] = []
    if message not in command_map_to_add_to[command]:
        command_map_to_add_to[command].append(message)


async def get_quotes_from_discord():
    new_command_map = {}
    channel = client.get_channel(bot_database_channel_id)
    messages = await channel.history(limit=1000).flatten()
    for message in messages:
        content = message.content
        first_space = content.find(" ")
        command = content[:first_space]
        message = content[first_space + 1:]
        add_to_map(new_command_map, command, message)
    return new_command_map


async def add_quote_to_discord(command, message):
    save_message = command + " " + message
    channel = client.get_channel(bot_database_channel_id)
    await channel.send(save_message)
    return


@atexit.register
async def shutting_down():
    await client.get_channel(225374061386006528).send("Shutting Down")


client.run(TOKEN)
