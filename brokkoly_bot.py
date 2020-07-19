# todo In chat maintenance of the string library
# todo separate the commands by server. give yourself the ability to add commands to the master list
# todo Use a database

import random
import atexit
import re
import discord
from importlib import util
from brokkoly_bot_database import *
import sched
from datetime import datetime, timedelta
from discord.ext import tasks
import time

TOKEN = None
IS_TEST = False
DATABASE_URL = None
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

# client = discord.Client(status="Started Up")
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
# bot_database_channel_id = None
bot_ui_channel_id = None
if (IS_TEST):
    # bot_database_channel_id = bot_database_channel_ids["test"]
    bot_ui_channel_id = bot_test_channel_ids["test"]
else:
    # bot_database_channel_id = bot_database_channel_ids["prod"]
    bot_ui_channel_id = bot_test_channel_ids["prod"]
game_jazz_id = 639124326385188864


# TODO Check roles instead of just ids. Maybe give people in the bot server the ability

# protected_commands = ["!help", "!add", "!estop", "!otherservers", "!cooldown", "!timeout", "!removetimeout"]

# timeout = {
#     mtg_legacy_discord_id: 60,
#     brokkolys_bot_testing_zone_id: 5,
#     madison_discord_id: 0
# }
# maintenance = {}


class BrokkolyBot(discord.Client):
    protected_commands = ["!help", "!add", "!estop", "!otherservers", "!cooldown", "!timeout", "!removetimeout"]
    author_whitelist = [
        146687253370896385  # me
        , 115626912394510343  # ori
        , 200773608094564352  # wind
        , 115602332863037443  # thaya
        , 185287142388400129  # thalia
        , 120756475768471554  # solyra
    ]

    def __init__(self, is_test=False, token=None, database_url=None):
        self.token = token
        self.is_test = is_test
        self.timeout = {}
        self.maintenance = {}
        self.initialize_regex()
        discord.Client.__init__(self)
        self.bot_database = BrokkolyBotDatabase(database_url)
        self.run(token)

    # region events
    @client.event
    async def on_message(self, message):
        """Fires every time a user sends a message in an associated server.
        This is where everything happens.
        """
        # global command_map
        # global maintenance
        # Don't reply to our own messages
        if message.author.id in my_bots:
            return
        if not message.content.startswith("!"):
            return

        if message.content.startswith("!maintenance") and message.guild and self.user_can_maintain(message.author,
                                                                                                   message.guild):
            dm_channel = await message.author.create_dm()
            self.maintenance[dm_channel.id] = MaintenanceSession(message.guild.id, dm_channel, self.bot_database)

            await dm_channel.send("Entering maintenance mode for %s." % (message.guild.name)
                                  + "\n!list <search param coming soon>: List out the commands for the server and their ids"
                                  + "\n!remove <command (no !)> <command # from !list or * to remove all>"
                                  + "\n!roles Coming Soon!"
                                  + "\n!timeout Coming Soon!"
                                  + "\n!add !<command> <message>: Add a new command."
                                  + "\n!exit: Leave the maintenance session. You should do this when you're done."
                                  )
            await message.add_reaction("📧")
            return

        # todo loop through commands as keys to a map of functions

        if message.channel.id in self.maintenance:
            content = message.content
            if (content.startswith("!exit")):
                await message.add_reaction("🛑")
                self.maintenance.pop(message.channel.id)
                print("Exited maintenance")
                return
            if (content.startswith("!role")):
                print("Role Commands")
                return
            if (content.startswith("!add")):
                await self.handle_add(message, self.maintenance[message.channel.id].server_id)
                return
            if (content.startswith("!remove")):
                await self.handle_remove(message, self.maintenance[message.channel.id])
                return
            if (content.startswith("!list")):
                await self.handle_list(message, self.maintenance[message.channel.id], show_message=True)
                return
            if (content.startswith("!cooldown")):
                print("Cooldown Setting")
                return
            return

        if message.content.startswith("!timeout") and self.user_can_maintain(message.author, message.guild):
            timeout_until = message.created_at + timedelta(
                seconds=int(round(self.parse_timeout(message.content) * 3600)))
            timeout_time = int(round(self.parse_timeout(message.content)))
            timeout_role_id = await self.bot_database.get_timeout_role(message.guild)

            for user in message.mentions:
                await self.add_user_timeout(user, timeout_time, message.guild, timeout_role_id)
            return

        if message.content.startswith("!removetimeout") and self.user_can_maintain(message.author, message.guild):
            timeout_role_id = await self.get_timeout_role(message.guild)
            for user in message.mentions:
                await self.remove_user_timeout(user, message.guild, timeout_role_id)
            return

        # store_user_timeout

        if message.content.startswith("!estop") and message.author.id in self.author_whitelist:
            brokkoly = self.get_user(146687253370896385)
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

        if message.channel.type == discord.ChannelType.private:
            return

        if message.content.startswith("!add "):
            await self.handle_add(message)
            return

        command = message.content.lower()[1:]
        command, to_search = self.parse_search(command)
        msg = self.bot_database.get_message(message.guild.id, command, to_search)
        if msg == "": return
        if message.guild.id in last_message_time \
                and message.guild.id in self.timeout \
                and not (message.created_at - last_message_time[message.guild.id]).total_seconds() > self.timeout[
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
    async def on_ready(self):
        """Fires once the discord bot is ready.
        Notify the test server that the bot has started
        """
        # add_timed_out_users_table(conn)
        # add_timeout_role_column(conn)
        await self.get_channel(bot_ui_channel_id).send("Starting Up")
        await self.get_channel(bot_ui_channel_id).send("Online")
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        check_users_to_remove.start()

    @client.event
    async def on_guild_join(self, guild):
        self.bot_database.add_server(guild.id, 30)
        return

    @client.event
    async def on_guild_remove(self, guild):
        # remove_server(conn, guild.id)
        return

    # endregion events
    # region initializers
    def initialize_regex(self):
        after_add_regex_string = r'(?<!.)(?!![aA]dd)![A-zA-Z]{3,} .+'  # we've already stripped "!add" from the message
        remove_regex_string = r'(?<!.)[a-zA-z]{3,20} ([0-9]{1,10}|\*)(?!.)'
        self.after_add_compiled_regex = re.compile(after_add_regex_string)
        self.remove_compiled_regex = re.compile(remove_regex_string)

    # endregion initializers

    async def handle_add(self, message, server_id=None):
        """add the value in message to the the command map"""
        global command_map
        if not server_id:
            if message.guild:
                server_id = message.guild.id
            else:
                await self.reject_message(message, "Error! Not in Maintenance Mode. Use !maintenance from a server")
                return
        if self.user_can_maintain(message.author, message.guild):
            if message.mentions or message.role_mentions or message.mention_everyone:
                await self.reject_message(message, "Error! No mentions allowed.")
                return
            result = self.parse_add(message.content)
            if result:
                command = result[0]
                new_entry = result[1]
                if len(command) > 21:
                    await self.reject_message(message, "Error! Command cannot be longer than 20 characters.")
                    return
                if len(new_entry) > 500:
                    await self.reject_message(message, "Error! Message cannot be longer than 500 characters.")
                    return
                command = command.lower()
                if command in self.protected_commands:
                    await self.reject_message(message, "Error! That is a protected command")
                    return
                if self.bot_database.add_command(server_id, command, new_entry):
                    await message.add_reaction(self.get_emoji(445805262880899075))
                return
            else:
                await self.reject_message(message, "Error! Expected \"!add !<command length at least 3> <message>\".")
                return
        else:
            await self.reject_message(message, "Error! Insufficient privileges to add.", True)

    async def handle_remove(self, message, session):
        result = self.parse_remove(message.content)
        if not result:
            # TODO add error message
            await self.reject_message(message, "Error! incorrect remove format")
            return
        command = result[0]
        message_number = result[1]
        if message_number == "*":
            self.bot_database.remove_command(session.server_id, command)
            await message.add_reaction("🗑️")
        else:
            message_number = int(message_number)
            command_id = session.command_map[command][message_number][0]
            if (command_id >= 0):
                self.bot_database.remove_command(command_id=command_id)
                await message.add_reaction("🗑️")

        return

    async def handle_big_message(self, message, leftovers, new_line):
        if (len(leftovers) + len(new_line) > 2000):
            await message.channel.send(leftovers)
            return new_line
        else:
            return leftovers + new_line

    async def handle_list(self, message, session, show_message=False):
        search_command = self.parse_list(message.content)
        commands = None
        session.load_command_map()
        leftovers = ""
        for command_string in session.command_map:
            if show_message:
                # leftovers = await handle_big_message(message,leftovers,
                await self.get_command_response_lines(session.command_map, command_string, message, show_message)

    async def get_command_response_lines(self, command_map, command_string, message, show_message):
        response_message = ""
        leftovers = "!%s responses:\n" % (command_string)
        for count in command_map[command_string]:
            entry_value = command_map[command_string][count][1]
            if show_message:
                # await message.channel.send("!%s %d %s\n" % (command_string, count, entry_value))
                # TODO do this so that embeds are nice
                leftovers = await self.handle_big_message(message, leftovers,
                                                          "!%s %d %s\n" % (command_string, count, entry_value))
        if leftovers != "":
            await message.channel.send(leftovers)

    async def reject_message(self, message, error, show_message=True):
        """React with an x to the message, and provide an error message"""
        await message.add_reaction("❌")
        if show_message:
            await message.channel.send(error)

    def parse_add(self, content):
        """parse the content to get the command and message"""
        string_to_parse = content[5:]  # Cut off the add since we've already matched
        if re.fullmatch(self.after_add_compiled_regex, string_to_parse):
            first_space = string_to_parse.find(" ")
            command = string_to_parse[1:first_space]
            message = string_to_parse[first_space + 1:]
            return [command, message]
        else:
            return []

    def parse_remove(self, content):
        """
        Parse a remove command
        :param content: A string that starts with !remove
        :return: an array holding the command and the message number to remove
        """
        string_to_parse = content[8:]
        if re.fullmatch(self.remove_compiled_regex, string_to_parse):
            first_space = string_to_parse.find(" ")
            command = string_to_parse[:first_space]
            message_number = string_to_parse[first_space + 1:]
            return [command, message_number]
        else:
            return []

    def parse_search(self, content):
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

    def parse_list(self, content):
        string_to_parse = content[6:]
        return string_to_parse

    def parse_timeout(self, content):
        last_greater_than = content.rfind('>')
        try:
            time_in_hours = float(content[last_greater_than + 1:])
        except:
            return None
        return time_in_hours

    # def find_in_command_map(self,command, to_search):
    #     closest = ""
    #     closest_number = 10000000
    #     for entry in command_map[command]:
    #         new_closest_number = entry.lower().find(to_search)
    #         if len(to_search) > len(entry): continue
    #         if new_closest_number < closest_number and new_closest_number != -1:
    #             closest_number = new_closest_number
    #             closest = entry
    #     return closest

    # def add_to_map(command_map_to_add_to, command, message):
    #     """Add the command and message to the command map"""
    #     if command not in command_map_to_add_to:
    #         command_map_to_add_to[command] = []
    #     if message not in command_map_to_add_to[command]:
    #         command_map_to_add_to[command].append(message)
    #         return True
    #     else:
    #         return False
    #
    #
    # async def get_map_from_discord():
    #     """Load the map form the discord database channel"""
    #     # TODO Use an actual database
    #     new_command_map = {}
    #     channel = client.get_channel(bot_database_channel_id)
    #     messages = await channel.history(limit=1000).flatten()
    #     for message in messages:
    #         content = message.content
    #         first_space = content.find(" ")
    #         command = content[:first_space]
    #         message = content[first_space + 1:]
    #         add_to_map(new_command_map, command, message)
    #     return new_command_map

    async def add_user_timeout(self, user, timeout_time, server, role_id):
        await user.add_roles(server.get_role(role_id), reason="Timing out user")
        until_time_ms = int(round(datetime.utcnow().timestamp() * 1000)) + timeout_time * 1000
        self.bot_database.add_user_timeout_to_database(server.id, user.id, until_time_ms)
        # s = sched.scheduler()
        # s.enter(timeout_time / 1000, 1, remove_user_timeout, (user, server, role_id))
        # s.run()
        return

    async def remove_user_timeout(self, user, server, role_id):
        role = server.get_role(role_id)
        await user.remove_roles(role)
        self.bot_database.remove_user_timeout_from_database(server.id, user.id)
        print("Removed a timeout")
        return

    async def get_timeout_role(self, server):
        role_id = self.bot_database.get_timeout_role_for_server(server.id)
        if role_id and server.get_role(role_id):
            return role_id
        my_name = server.me.display_name
        role = await server.create_role(name="%s's Timeout Role" % (my_name),
                                        permissions=discord.Permissions(send_messages=False),
                                        reason="Creating a role for timing out. Feel free to edit the name but please don't mess with the permissions.")
        if (role):
            role_id = role.id
            self.bot_database.add_timeout_role_for_server(server.id, role_id)
        else:
            role_id = None
        return role_id

    # todo finish checking for timed out users

    # async def add_quote_to_discord(self,command, message):
    #     """Sends a message to the discord database with the new entry"""
    #     save_message = command + " " + message
    #     channel = client.get_channel(bot_database_channel_id)
    #     await channel.send(save_message)
    #     return

    def user_can_maintain(self, author, server):
        return author.id in self.author_whitelist


class CheckUserLoop:
    def __init__(self, bot):
        self.bot = bot
        self.check_users_to_remove.start()

    @tasks.loop(minutes=1)
    async def check_users_to_remove(self):
        users_from_db = self.bot.bot_database.get_user_timeouts_finished(
            int(round(datetime.utcnow().timestamp() * 1000)))
        print("Checking for users to remove")
        for user in users_from_db:
            server_id = user[1]
            server = await discord.guild(server_id)
            user_id = user[2]
            user = server.get_user(user_id)
            role_id = self.bot.bot_database.get_timeout_role_for_server(server_id)
            await self.bot.remove_user_timeout(user, server, role_id)


@tasks.loop(minutes=1)
async def check_users_to_remove():
    # users_from_db = get_user_timeouts_finished(conn, int(round(datetime.utcnow().timestamp() * 1000)))
    print("Checking for users to remove")
    # for user_from_db in users_from_db:
    #     server_id = user_from_db[0]
    #     server = client.get_guild(server_id)
    #     user_id = user_from_db[1]
    #     user = server.get_member(user_id)
    #     role_id = get_timeout_role_for_server(conn, server_id)
    #     await remove_user_timeout(user, server, role_id)





@atexit.register
def shutting_down():
    # TODO Make this work?
    conn.close()


class MaintenanceSession():
    command_map = {}

    def __init__(self, server_id=None, channel=None, bot_database=None):
        self.server_id = server_id
        self.channel_id = channel
        self.bot_database = bot_database
        self.command_map = self.load_command_map()

    def load_command_map(self):
        self.command_map = {}
        commands = self.bot_database.get_all_commands(self.server_id)
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


running_bot = BrokkolyBot(IS_TEST, token=TOKEN, database_url=DATABASE_URL)
CheckUserLoop(client)
