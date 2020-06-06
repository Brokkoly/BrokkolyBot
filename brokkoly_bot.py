# TODO In chat maintenance of the string library
# todo separate the commands by server. give yourself the ability to add commands to the master list

import random
import atexit
import re
import discord
from importlib import util
import os

TOKEN = None
IS_TEST = False
bot_database_channel_ids = {
    "test": 718850472814968905,
    "prod": 718205785888260139
}
bot_ids = {
    "test": 449815971897671690,
    "prod": 225369871393882113
}
bot_test_channel_ids = {
    "test": 718850430049714267,
    "prod": 718854497245462588
}

token_spec = util.find_spec('tokens')
if token_spec is not None:
    import tokens

    TOKEN = tokens.TOKEN_TEST
    IS_TEST = True
else:
    TOKEN = os.environ['TOKEN']

client = discord.Client()

command_map = {}
last_message_time = {}
random.seed()
brokkoly_bot_test_id = 449815971897671690
brokkoly_bot_id = 225369871393882113
my_bots = [brokkoly_bot_id, brokkoly_bot_test_id]
# ids and constants
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528
bot_database_channel_id = None
bot_ui_channel_id = None
if (IS_TEST):
    bot_database_channel_id = bot_database_channel_ids["test"]
    bot_ui_channel_id = bot_test_channel_ids["test"]
else:
    bot_database_channel_id = bot_database_channel_ids["prod"]
    bot_ui_channel_id = bot_test_channel_ids["prod"]
game_jazz_id = 639124326385188864
# TODO Check roles instead of just ids. Maybe give people in the bot server the ability
author_whitelist = [
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
    """Fires every time a user sends a message in an associated server.
    This is where everything happens.
    """
    global command_map
    # Don't reply to our own messages
    if message.author.id in my_bots:
        return
    if not message.content.startswith("!"):
        return
    if message.content.startswith("!estop") and message.author.id in author_whitelist:
        brokkoly = client.get_user(146687253370896385)
        brokkoly_dm = await brokkoly.create_dm()
        await brokkoly_dm.send("Emergency Stop Called. Send Help."
                               + "\nServer: " + message.guild.name
                               + "\nChannel: " + message.channel.name
                               + "\nTime & Date: " + message.created_at.strftime("%H:%M:%S, %m/%d/%Y")
                               + "\n" + message.jump_url
                               )
        await message.channel.send(
            "@Brokkoly#0001 Emergency Stop Called. Send Help."
            "\n<:notlikeduck:522871146694311937>\n<:Heck:651250241722515459>")
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

    if message.content.startswith("!add "):
        await handle_add(message)

    command = message.content.lower()
    command, to_search = parse_search(command)
    if command in command_map:
        msg = ""
        if to_search != None:
            msg = find_in_command_map(command, to_search)
        else:
            msg = random.choice(command_map[command])
        if msg == "": return
        if message.guild.id in last_message_time \
                and message.guild.id in timeout \
                and not (message.created_at - last_message_time[message.guild.id]).total_seconds() > timeout[
            message.guild.id]:
            await message.add_reaction("⏳")
            return
        else:
            last_message_time[message.guild.id] = message.created_at
            await message.channel.send(msg)

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
    """Fires once the discord bot is ready.
    Notify the test server that the bot has started
    """
    global command_map
    await client.get_channel(bot_ui_channel_id).send("Starting Up")
    command_map = await get_map_from_discord()
    await client.get_channel(bot_ui_channel_id).send("Online")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def handle_add(message):
    """add the value in message to the the command map"""
    global command_map
    if message.author.id in author_whitelist:
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
            if add_to_map(command_map, command, new_entry):
                await add_quote_to_discord(command, new_entry)
            await message.add_reaction(client.get_emoji(445805262880899075))
            return
        else:
            await reject_message(message, "Error! Expected \"!add !<command length at least 3> <message>\".")
            return
    else:
        await reject_message(message, "Error! Insufficient privileges to add.", True)


async def reject_message(message, error, show_message=True):
    """React with an x to the message, and provide an error message"""
    await message.add_reaction("❌")
    if show_message:
        await message.channel.send(error)


def parse_add(content):
    """parse the content to get the command and message"""
    string_to_parse = content[5:]  # Cut off the add since we've already matched
    if re.fullmatch(after_add_compiled_regex, string_to_parse):
        first_space = string_to_parse.find(" ")
        command = string_to_parse[:first_space]
        message = string_to_parse[first_space + 1:]
        return [True, command, message]
    else:
        return [False]


def parse_search(content):
    """parse the content to get the command and message"""
    # TODO reject search if it is unreasonably long
    first_space = content.find(" ")
    if first_space == -1:
        return [content, None]
    command = content[:first_space]
    to_search = content[first_space + 1:]
    return [command, to_search]


def find_in_command_map(command, to_search):
    closest = ""
    closest_number = 10000000
    for entry in command_map[command]:
        new_closest_number = entry.lower().find(to_search)
        if new_closest_number < closest_number and new_closest_number != -1:
            closest_number = new_closest_number
            closest = entry
    return closest


def add_to_map(command_map_to_add_to, command, message):
    """Add the command and message to the command map"""
    if command not in command_map_to_add_to:
        command_map_to_add_to[command] = []
    if message not in command_map_to_add_to[command]:
        command_map_to_add_to[command].append(message)
        return True
    else:
        return False


async def get_map_from_discord():
    """Load the map form the discord database channel"""
    # TODO Use an actual database
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
    """Sends a message to the discord database with the new entry"""
    save_message = command + " " + message
    channel = client.get_channel(bot_database_channel_id)
    await channel.send(save_message)
    return


@atexit.register
async def shutting_down():
    # TODO Make this work?
    await client.get_channel(bot_ui_channel_id).send("Shutting Down")


client.run(TOKEN)
