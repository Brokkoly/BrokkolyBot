import random
import atexit
import re
import discord
from importlib import util

from brokkoly_bot_database import *
from datetime import datetime
from discord.ext import tasks
from discord.ext import commands
import os
import unittest

# Todo: replace instances of server with guild
NO_MENTIONS_ALLOWED_ERROR = "Error! No mentions allowed."
BANG_NOT_NEEDED_WARNING = "Warning! \"!\" is no longer necessary when adding new commands, and will no longer be accepted in the future"
INSUFFICIENT_PRIVELIDGES_ERROR = "Error! Insufficient privileges to add."
PROTECTED_COMMAND_ERROR = "Error! That is a protected command"
NEW_VALUE_TOO_LONG_ERROR = "Error! Message cannot be longer than 500 characters."
COMMAND_TOO_LONG_ERROR = "Error! Command cannot be longer than 20 characters."
EXPECTED_SYNTAX_ERROR = "Error! Expected \"!add <command length at least 3> <message>\"."
CAN_ONLY_CONTAIN_LETTERS_ERROR = "Error! Command can only contain letters"

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

client = discord.Client()

command_map = {}

random.seed()
brokkoly_bot_test_id = 449815971897671690
brokkoly_bot_id = 225369871393882113
my_bots = [brokkoly_bot_id, brokkoly_bot_test_id]
# ids and constants
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528
madison_discord_id = 368078887361708033
bot_ui_channel_id = None
if IS_TEST:
    bot_ui_channel_id = bot_test_channel_ids["test"]
else:
    bot_ui_channel_id = bot_test_channel_ids["prod"]
game_jazz_id = 639124326385188864


class BrokkolyBot(commands.Bot):
    protected_commands = ["help", "add", "estop", "otherservers", "cooldown", "timeout", "removetimeout",
                          "extractemoji"]

    def __init__(self, is_test=False, token=None, database_url=None, is_unit_test=False):

        self.timeout = {}
        self.maintenance = {}
        self.last_message_time = {}
        self.initialize_regex()
        # todo: load command prefixes from database per guild.

        if not is_unit_test:
            self.token = token
            self.is_test = is_test
            self.bot_database = BrokkolyBotDatabase(database_url)
            commands.Bot.__init__(self, command_prefix=['!'])
        # self.run(token)

    # class BrokkolyBotTest(unittest.UnitTest):
    #    test1 = BrokkolyBot(is_unit_test=False)

    # region events
    # @client.event
    # async def on_message(self, message):
    #     """Fires every time a user sends a message in an associated server.
    #     This is where everything happens.
    #     """
    #     # global command_map
    #     # global maintenance
    #     # Don't reply to our own messages
    #     if message.author.id in my_bots:
    #         return
    #     if not message.content.startswith("!"):
    #         return
    #
    #     if message.content.startswith("!maintenance") and message.guild and self.user_can_maintain(message):
    #         dm_channel = await message.author.create_dm()
    #         self.maintenance[dm_channel.id] = MaintenanceSession(message.guild.id, dm_channel, self.bot_database)
    #
    #         await dm_channel.send("Entering maintenance mode for %s." % (message.guild.name)
    #                               + "\n!list <search param coming soon>: List out the commands for the server and their ids"
    #                               + "\n!remove <command (no !)> <command # from !list or * to remove all>"
    #                               + "\n!roles Coming Soon!"
    #                               + "\n!cooldown <integer> Set the message cooldown for the server"
    #                               + "\n!add !<command> <message>: Add a new command."
    #                               + "\n!exit: Leave the maintenance session. You should do this when you're done."
    #                               )
    #         await message.add_reaction("📧")
    #         return
    #
    #     # todo loop through commands as keys to a map of functions
    #
    #     if message.channel.id in self.maintenance:
    #         content = message.content
    #         if (content.startswith("!exit")):
    #             await message.add_reaction("🛑")
    #             self.maintenance.pop(message.channel.id)
    #             print("Exited maintenance")
    #             return
    #         if (content.startswith("!role")):
    #             print("Role Commands")
    #             return
    #         if (content.startswith("!add")):
    #             await self.handle_add(message, self.maintenance[message.channel.id].server_id)
    #             return
    #         if (content.startswith("!remove")):
    #             await self.handle_remove(message, self.maintenance[message.channel.id])
    #             return
    #         if (content.startswith("!list")):
    #             await self.handle_list(message, self.maintenance[message.channel.id], show_message=True)
    #             return
    #         if (content.startswith("!cooldown")):
    #             await self.handle_cooldown(message, self.maintenance[message.channel.id])
    #
    #             return
    #         return
    #
    #     if message.content.startswith("!timeout") and self.user_can_maintain(message):
    #         parsed_timeout = self.parse_timeout(message.content)
    #         if parsed_timeout <= 0:
    #             return
    #         timeout_time = int(round(parsed_timeout))
    #         timeout_role_id = await self.get_timeout_role(message.guild)
    #
    #         for user in message.mentions:
    #             await self.add_user_timeout(user, timeout_time, message.guild, timeout_role_id)
    #         return
    #
    #     if message.content.startswith("!removetimeout") and self.user_can_maintain(message):
    #         timeout_role_id = await self.get_timeout_role(message.guild)
    #         for user in message.mentions:
    #             await self.remove_user_timeout(user, message.guild, timeout_role_id)
    #         return
    #
    #     if message.content.startswith("!estop") and message.author.id in self.author_whitelist:
    #         # TODO Depreciate this part
    #         brokkoly = self.get_user(146687253370896385)
    #         brokkoly_dm = await brokkoly.create_dm()
    #         await brokkoly_dm.send("Emergency Stop Called. Send Help."
    #                                + "\nServer: " + message.guild.name
    #                                + "\nChannel: " + message.channel.name
    #                                + "\nTime & Date: " + message.created_at.strftime("%H:%M:%S, %m/%d/%Y")
    #                                + "\n" + message.jump_url
    #                                )
    #         await message.channel.send(
    #             "@Brokkoly#0001 Emergency Stop Called. Send Help."
    #             "\n<:notlikeduck:522871146694311937>\n<:Heck:651250241722515459>")
    #         quit()
    #
    #     if message.content.startswith("!extractemoji"):
    #         message_from_url = await self.get_message_from_url(message)
    #         custom_emojis = self.get_emoji_ids(message_from_url if message_from_url else message)
    #         await self.send_emoji_urls(custom_emojis, message.channel)
    #         return
    #
    #     if message.content.startswith("!help"):
    #         response = "Available Commands:\n" \
    #                    "!help - You obviously know this\n" \
    #                    "!add - Add a new command. Syntax: !add !<command> <message>\n" \
    #                    "!extractemoji - Get the URL for the emojis in the rest of the message\n" \
    #                    "See my code: <https://github.com/Brokkoly/BrokkolyBot>\n" \
    #                    "             <https://github.com/Brokkoly/BrokkolyBotFrontend>\n" \
    #                    "To see all commands and responses,please go to https://brokkolybot.azurewebsites.net\n" \
    #                    "Plus the following commands: "
    #
    #         for command in self.bot_database.get_all_command_strings(message.guild.id):
    #             response = response + "\n" + "!" + command[0]
    #         user_dm_channel = await message.author.create_dm()
    #         await user_dm_channel.send(response)
    #         await message.add_reaction("📧")
    #         return
    #
    #     if message.channel.type == discord.ChannelType.private:
    #         return
    #
    #     # if message.content.startswith("!add "):
    #     #     await self.handle_add(message)
    #     #     return
    #
    #     command = message.content.lower()[1:]
    #     command, to_search = self.parse_search(command)
    #     msg = self.bot_database.get_message(message.guild.id, command, to_search)
    #     if msg == "": return
    #
    #     if message.guild.id in self.last_message_time:
    #         # todo split out this retrieval
    #         cooldown_result = self.bot_database.get_server_cooldown(message.guild.id)
    #         cooldown_result = 30 if cooldown_result < 0 else cooldown_result
    #         if not (message.created_at - self.last_message_time[message.guild.id]).total_seconds() > cooldown_result:
    #             await message.add_reaction("⏳")
    #             return
    #
    #     self.last_message_time[message.guild.id] = message.created_at
    #     await message.channel.send(msg)

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
        self.check_users_to_remove.start()
        await self.update_timeout_role_for_all_servers()

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
        command_regex_string = r'[a-zA-Z]+'
        self.after_add_compiled_regex = re.compile(after_add_regex_string, re.DOTALL)
        self.remove_compiled_regex = re.compile(remove_regex_string)
        self.command_compiled_regex = re.compile(command_regex_string)

    # endregion initializers

    async def handle_add(self, message, command, new_entry):
        """add the value in message to the the database"""
        global command_map
        server_id = message.guild.id
        # else:
        #     await self.reject_message(message, "Error! Not in Maintenance Mode. Use !maintenance from a server")
        #     return
        if self.user_can_maintain(message):
            if message.mentions or message.role_mentions or message.mention_everyone:
                await self.reject_message(message, NO_MENTIONS_ALLOWED_ERROR
                                          )
                return
            error = ""
            # TODO: actual error class?
            if (command[0] == "!"):
                await message.channel.send(
                    BANG_NOT_NEEDED_WARNING)
                command = command[1:]
            if (error := self.validate_add(command, new_entry)):
                await self.reject_message(message, error)
                return
                if self.bot_database.add_command(server_id, command, new_entry):
                    await message.add_reaction(self.get_emoji(445805262880899075))
                return
        else:
            await self.reject_message(message, INSUFFICIENT_PRIVELIDGES_ERROR, True)

    def validate_add(self, command, new_entry):
        if not re.match(self.command_compiled_regex, command):
            return CAN_ONLY_CONTAIN_LETTERS_ERROR
        if len(command) < 3:
            return EXPECTED_SYNTAX_ERROR
        if len(command) >= 20:
            return COMMAND_TOO_LONG_ERROR
        if len(new_entry) > 500:
            return NEW_VALUE_TOO_LONG_ERROR
        if command in self.protected_commands:
            return PROTECTED_COMMAND_ERROR

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
                await self.get_command_response_lines(session.command_map, command_string, message, show_message)

    async def get_command_response_lines(self, command_map, command_string, message, show_message):
        response_message = ""
        leftovers = "!%s responses:\n" % (command_string)
        for count in command_map[command_string]:
            entry_value = command_map[command_string][count][1]
            if show_message:
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

    def parse_cooldown(self, content):
        string_to_parse = content[9:]
        try:
            new_timeout = int(string_to_parse)
        except:
            return -1
        if (new_timeout >= 0):
            return new_timeout
        return -1

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
            return 0
        return time_in_hours

    def get_emoji_ids(self, message):
        custom_emojis = self.get_emoji_ids_from_content(message.content)
        custom_emojis = custom_emojis + self.get_emoji_ids_from_reactions(message)
        return list(dict.fromkeys(custom_emojis))

    def get_emoji_ids_from_reactions(self, message):
        custom_emojis = []
        for reaction in [r.emoji for r in message.reactions]:
            if isinstance(reaction, str):
                continue
            custom_emojis.append((reaction.animated, reaction.id))
        return custom_emojis

    def get_emoji_ids_from_content(self, content):
        custom_emojis = re.findall(r'<a?:\w*:\d*>', content)
        custom_emojis = [self.get_emoji_tuple(e) for e in custom_emojis]
        return custom_emojis

    async def get_content_from_message_url(self, message):
        url = re.findall(r'https:\/\/(?:canary\.)?discordapp\.com\/channels\/[0-9]+\/[0-9]+\/[0-9]+', message.content)
        if (not url) or (not url[0]):
            return ""
        parts = url[0].split('/')
        try:
            message_id = int(parts[-1])
            channel_id = int(parts[-2])
            guild_id = int(parts[-3])
        except:
            await message.channel.send("Invalid URL")
            return
        guild = await self.fetch_guild(guild_id)
        if (not guild):
            await message.channel.send("Sorry, I don't have access to the server that message is from.")
            return ""
        channel = await self.fetch_channel(channel_id)
        if (not channel):
            await message.channel.send("Sorry, I don't have access to the channel that message is from.")
            return ""
        other_message = await channel.fetch_message(message_id)
        if (other_message and other_message.content):
            return other_message.content
        else:
            return ""

    async def get_message_from_url(self, message):
        url = re.findall(r'https:\/\/(?:canary\.)?discordapp\.com\/channels\/[0-9]+\/[0-9]+\/[0-9]+', message.content)
        if (not url) or (not url[0]):
            return ""
        parts = url[0].split('/')
        try:
            message_id = int(parts[-1])
            channel_id = int(parts[-2])
            guild_id = int(parts[-3])
        except:
            await message.channel.send("Invalid URL")
            return
        guild = await self.fetch_guild(guild_id)
        if (not guild):
            await message.channel.send("Sorry, I don't have access to the server that message is from.")
            return None
        channel = await self.fetch_channel(channel_id)
        if (not channel):
            await message.channel.send("Sorry, I don't have access to the channel that message is from.")
            return None
        other_message = await channel.fetch_message(message_id)
        if (other_message and other_message.content):
            return other_message
        else:
            return None

    async def send_emoji_urls(self, emoji_ids, channel):
        url = "https://cdn.discordapp.com/emojis/{}.{}"
        for e in emoji_ids:
            await channel.send(url.format(str(e[1]), "gif" if e[0] else "png"))

    async def add_user_timeout(self, user, timeout_time, server, role_id):
        await user.add_roles(server.get_role(role_id), reason="Timing out user")
        until_time_ms = int(round(datetime.utcnow().timestamp() * 1000)) + timeout_time * 1000 * 60
        self.bot_database.add_user_timeout_to_database(server.id, user.id, until_time_ms)
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
        # TODO maybe initialize this separately or on startup so that new channels get properly set?
        await self.update_timeout_role_for_server(server, role)

        if (role):
            role_id = role.id
            self.bot_database.add_timeout_role_for_server(server.id, role_id)
        else:
            role_id = None
        return role_id

    # todo finish checking for timed out users

    async def update_timeout_role_for_server(self, server, role=None):
        if not role:
            role = server.get_role(await self.get_timeout_role(server))
        if not role:
            return
        for channel in server.text_channels:
            if channel.permissions_for(server.get_member(self.user.id)).view_channel:
                await channel.set_permissions(role, send_messages=False)
        return

    async def update_timeout_role_for_all_servers(self):
        for server in self.guilds:
            if not server.get_member(self.user.id).guild_permissions.manage_roles:
                continue
            role = server.get_role(await self.get_timeout_role(server))

            await self.update_timeout_role_for_server(server, role)

    def user_can_maintain(self, message):
        author = message.author
        if (author.permissions_in(message.channel).manage_guild):
            return True
        if (self.user_has_bot_manager_role(author, message.guild.id)):
            return True

    def user_has_bot_manager_role(self, author, server_id):
        bot_manager_role_id = self.bot_database.get_manager_role_for_server(server_id)
        if not bot_manager_role_id:
            return False
        for role in author.roles:
            if str(role.id) == bot_manager_role_id:
                return True
        return False

    async def handle_cooldown(self, message, session):
        parse_result = self.parse_cooldown(message.content)
        if (parse_result < 0):
            await self.reject_message(message, "Error! Timeout value must be an integer >=0.")
        else:
            self.bot_database.set_server_cooldown(session.server_id, parse_result)

    def get_emoji_tuple(self, raw_emoji):
        parts = raw_emoji.split(':')
        return (parts[0].replace('<', ''), parts[2].replace('>', ''))

    @tasks.loop(minutes=1.0)
    async def check_users_to_remove(self):
        users_from_db = self.bot_database.get_user_timeouts_finished(int(round(datetime.utcnow().timestamp() * 1000)))
        if users_from_db:
            for user in users_from_db:
                server_id = user[0]
                server = self.get_guild(server_id)
                user_id = user[1]
                user = server.get_member(user_id)
                role_id = self.bot_database.get_timeout_role_for_server(server_id)
                await self.remove_user_timeout(user, server, role_id)


class CheckUserLoop:
    def __init__(self, bot):
        self.bot = bot
        self.check_users_to_remove.start()

    @tasks.loop(minutes=1.0)
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

    @check_users_to_remove.before_loop
    async def before_check_users(self):
        await self.bot.wait_until_ready()


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


bot = None

if __name__ == '__main__':
    bot = BrokkolyBot(IS_TEST, token=TOKEN, database_url=DATABASE_URL)


    @commands.command(aliases=["add"], rest_is_raw=True)
    async def testAdd(ctx, *args):
        print('Command: {}\nMessage: {}'.format(args[0] or "", " ".join(args[1:]) or ""))
        await ctx.send('Command: {}\nMessage: {}'.format(args[0] or "", " ".join(args[1:]) or ""))
        await bot.handle_add(ctx.message, args[0].lower(), " ".join(args[1:]))


    bot.add_command(testAdd)
    # @bot.command(rest_is_raw=True)
    # async def add(ctx, *args):
    #     print('Command: {}\nMessage: {}'.format(args[0] or "", " ".join(args[1:]) or ""))
    #     await ctx.send('Command: {}\nMessage: {}'.format(args[0] or "", " ".join(args[1:]) or ""))

    # await self.handle_add(ctx.message)
    bot.run(TOKEN)
