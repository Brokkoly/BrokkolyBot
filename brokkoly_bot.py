# todo In chat maintenance of the string library
# todo separate the commands by server. give yourself the ability to add commands to the master list
# todo Use a database

import random
import atexit
import re
import discord
from importlib import util
import os
import psycopg2
from brokkoly_bot_database import *

TOKEN = None
IS_TEST = False
DATABASE_URL = None
# conn = None
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
    DATABASE_URL = tokens.DATABASE_URL
else:
    TOKEN = os.environ['TOKEN']
    DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

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
madison_discord_id = 368078887361708033
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
remove_regex_string = r'(?<!.)[a-zA-z]{3,20} ([0-9]{1,10}|\*)(?!.)'
after_add_compiled_regex = re.compile(after_add_regex_string)
remove_compiled_regex = re.compile(remove_regex_string)
timeout = {
    mtg_legacy_discord_id: 60,
    brokkolys_bot_testing_zone_id: 5,
    madison_discord_id: 0
}
maintenance = {}


# class BrokkolyBot(bot_ui_channel_id=None,protected_commands=None,):


@client.event
async def on_message(message):
    """Fires every time a user sends a message in an associated server.
    This is where everything happens.
    """
    global command_map
    global maintenance
    # Don't reply to our own messages
    if message.author.id in my_bots:
        return
    if not message.content.startswith("!"):
        return

    if message.content.startswith("!maintenance") and message.guild and user_can_maintain(message.author,
                                                                                          message.guild):
        dm_channel = await message.author.create_dm()
        maintenance[dm_channel.id] = MaintenanceSession(message.guild.id, dm_channel, conn)

        await dm_channel.send("Entering maintenance mode for %s." % (message.guild.name)
                              + "\n ADD COMMANDS HERE")
        await message.add_reaction("📧")
        return

    if message.channel.id in maintenance:
        content = message.content
        if (content.startswith("!exit")):
            maintenance.pop(message.channel.id)
            print("Exited maintenance")
            return
        if (content.startswith("!role")):
            print("Role Commands")
            return
        if (content.startswith("!add")):
            await handle_add(message, maintenance[message.channel.id].server_id)
            return
        if (content.startswith("!remove")):
            await handle_remove(message, maintenance[message.channel.id])
            return
        if (content.startswith("!list")):
            await handle_list(message, maintenance[message.channel.id], show_message=True)
            return
        if (content.startswith("!timeout")):
            print("Timeout Setting")
            return
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
        return

    command = message.content.lower()[1:]
    command, to_search = parse_search(command)
    # if command in command_map:
    msg = ""
    # todo make search command
    # if to_search != None:
    #     msg = find_in_command_map(command, to_search)
    # else:
    #     msg = random.choice(command_map[command])
    msg = get_message(conn, message.guild.id, command)
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
    # global command_map
    await client.get_channel(bot_ui_channel_id).send("Starting Up")
    command_map = await get_map_from_discord()
    convert_from_map(conn, command_map, timeout)
    await client.get_channel(bot_ui_channel_id).send("Online")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def handle_add(message, server_id=None):
    """add the value in message to the the command map"""
    global command_map
    if not server_id:
        if message.guild:
            server_id = message.guild.id
        else:
            await reject_message(message, "Error! Not in Maintenance Mode. Use !maintenance from a server")
            return
    if user_can_maintain(message.author, message.guild):
        if message.mentions or message.role_mentions or message.mention_everyone:
            await reject_message(message, "Error! No mentions allowed.")
            return
        result = parse_add(message.content)
        if result:
            command = result[0]
            new_entry = result[1]
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
            # if add_to_map(command_map, command, new_entry):
            if add_command(conn, server_id, command, new_entry):
                #    await add_quote_to_discord(command, new_entry)
                await message.add_reaction(client.get_emoji(445805262880899075))
            return
        else:
            await reject_message(message, "Error! Expected \"!add !<command length at least 3> <message>\".")
            return
    else:
        await reject_message(message, "Error! Insufficient privileges to add.", True)


async def handle_remove(message, session):
    result = parse_remove(message.content)
    if not result:
        # TODO add error message
        await reject_message(message, "Error! incorrect remove format")
        return
    command = result[0]
    message_number = result[1]
    if message_number == "*":
        remove_command(session.conn, session.server_id, command)
        await message.add_reaction("🗑️")
    else:
        message_number = int(message_number)
        command_id = session.command_map[command][message_number][0]
        if (command_id >= 0):
            remove_command(session.conn, command_id=command_id)
            await message.add_reaction("🗑️")

    return


async def handle_list(message, session, show_message=False):
    search_command = parse_list(message.content)
    commands = None
    session.load_command_map()
    response_message = ""
    for command_string in session.command_map:
        response_message = response_message + "!%s responses:\n" % (command_string) \
                           + get_command_response_lines(session.command_map, command_string) + "\n"
    if show_message:
        await message.channel.send(response_message)


def get_command_response_lines(command_map, command_string):
    response_message = ""
    for count in command_map[command_string]:
        entry_value = command_map[command_string][count][1]
        response_message = response_message + "!%s %d %s\n" % (command_string, count, entry_value)
    return response_message


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
        command = string_to_parse[1:first_space]
        message = string_to_parse[first_space + 1:]
        return [command, message]
    else:
        return []


def parse_remove(content):
    string_to_parse = content[8:]
    if re.fullmatch(remove_compiled_regex, string_to_parse):
        first_space = string_to_parse.find(" ")
        command = string_to_parse[:first_space]
        message_number = string_to_parse[first_space + 1:]
        return [command, message_number]
    else:
        return []


def parse_search(content):
    """parse the content to get the command and search string.
    The Search string may be ""
    Keyword Arguments:
    content -- a string to split into a command and search string.
    """
    first_space = content.find(" ")
    if first_space == -1:
        return [content, None]
    command = content[:first_space]
    to_search = content[first_space + 1:]
    return [command, to_search]


def parse_list(content):
    string_to_parse = content[6:]
    return string_to_parse


def find_in_command_map(command, to_search):
    closest = ""
    closest_number = 10000000
    for entry in command_map[command]:
        new_closest_number = entry.lower().find(to_search)
        if len(to_search) > len(entry): continue
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


def user_can_maintain(author, server):
    return author.id in author_whitelist


@atexit.register
def shutting_down():
    # TODO Make this work?
    conn.close()
    # await client.get_channel(bot_ui_channel_id).send("Shutting Down")


class MaintenanceSession():
    command_map = {}

    def __init__(self, server_id=None, channel=None, conn=None):
        self.server_id = server_id
        self.channel_id = channel
        self.conn = conn
        self.command_map = self.load_command_map()

    def load_command_map(self):
        self.command_map = {}
        commands = get_all_commands(conn, self.server_id)
        for command in commands:
            command_id = command[0]
            command_string = command[1]
            entry_value = command[2]
            count = 0
            if command_string in self.command_map:
                count = len(self.command_map[command_string])
            else:
                self.command_map[command_string] = {}
            self.command_map[command_string][count] = [command_id, entry_value]


client.run(TOKEN)
