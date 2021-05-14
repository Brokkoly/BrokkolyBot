import atexit
import os
import random
import re
from datetime import datetime
from importlib import util

import discord
import requests
from discord.ext import commands
from discord.ext import tasks

from discord_slash import SlashCommand, SlashContext, error
from discord_slash.utils import manage_commands

from brokkoly_bot_database import *

# Todo: replace instances of server with guild

NO_MENTIONS_ALLOWED_ERROR = "Error! No mentions allowed."
BANG_NOT_NEEDED_WARNING = "Warning! \"!\" is no longer necessary when adding " \
                          "new commands, and will no longer be accepted in the future"
INSUFFICIENT_PRIVILEGES_ERROR = "Error! Insufficient privileges to add."
PROTECTED_COMMAND_ERROR = "Error! That is a protected command"
NEW_VALUE_TOO_LONG_ERROR = "Error! Message cannot be longer than 700 characters."
COMMAND_TOO_LONG_ERROR = "Error! Command cannot be longer than 20 characters."
EXPECTED_SYNTAX_ERROR = "Error! Expected \"!add <command length at least 3> <message>\"."
CAN_ONLY_CONTAIN_LETTERS_ERROR = "Error! Command can only contain letters"

TOKEN = None
IS_TEST = False
DATABASE_URL = None
TWITCH_ID = None
TWITCH_SECRET = None
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
    # TWITCH_ID = tokens.TWITCH_ID
    # TWITCH_SECRET = tokens.TWITCH_SECRET
else:
    TOKEN = os.environ['TOKEN']
    DATABASE_URL = os.environ['DATABASE_URL']
    # TWITCH_ID = os.environ['TWITCH_ID']
    # TWITCH_SECRET = os.environ['TWITCH_SECRET']

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

bot = None


def get_bot_id(is_test: bool):
    if (is_test):
        return brokkoly_bot_test_id
    return brokkoly_bot_id


class BrokkolyBot(commands.Bot):
    protected_commands = ["help", "add", "otherservers", "cooldown", "timeout", "removetimeout",
                          "extractemoji"]

    def __init__(self, is_test=False, token=None, database_url=None, is_unit_test=False):

        self.timeout = {}
        self.maintenance = {}
        self.last_message_time = {}
        self.after_add_compiled_regex = re.compile(r'(?<!.)(?!!?[aA]dd)!?[A-zA-Z]{3,} .+', re.DOTALL)
        self.remove_compiled_regex = re.compile(r'(?<!.)[a-zA-z]{3,20} ([0-9]{1,10}|\*)(?!.)')
        self.command_compiled_regex = re.compile(r'[a-zA-Z]+')
        self.prefixes = {}
        intents = discord.Intents.default()
        intents.members = True

        if not is_unit_test:
            self.token = token
            self.is_test = is_test
            self.bot_database = BrokkolyBotDatabase(database_url)
            for r in self.bot_database.get_all_server_prefixes():
                self.prefixes[int(r[0])] = r[1] or "!"
            commands.Bot.__init__(self, command_prefix=self.prefix, intents=intents)
            # self.add_listener(name="on_slash_command",func=self.on_slash_command)

    def prefix(self, _, message):
        return self.prefixes.get(message.guild.id, '!')

    # region events
    # @client.event
    # async def on_slash_command(self, ctx: SlashContext):
    #     print("got slash command")
    #     if (ctx.command == "populatecommands"):
    #         return
    #     ctx.defer()
    #     msg = self.bot_database.get_message(ctx.guild_id, ctx.command, ctx.message,
    #                                         user_is_mod=self.user_can_maintain(ctx.message))
    #     ctx.send(msg)
    #     print(ctx.guild.id)
    #     print(ctx.message)

    @client.event
    async def on_slash_command(self, ctx: SlashContext):
        if (ctx.command == "populatecommands"):
            return
        await ctx.defer()
        msg = self.bot_database.get_message(ctx.guild_id, ctx.command, ctx.kwargs.get("search"),
                                            user_is_mod=self.user_can_maintain(ctx.author, ctx.channel, ctx.guild_id))
        if (not msg):
            msg = "Couldn't find " + ctx.kwargs.get("search")
        await ctx.send(msg)

    @client.event
    async def on_message(self, message):
        """Fires every time a user sends a message in an associated server.
        This is where everything happens.
        """
        if message.author.id in my_bots:
            return
        if message.channel.type == discord.ChannelType.private:
            return
        try:
            # todo: make it not print about an exception on every message
            await self.process_commands(message)
        except discord.ext.commands.errors.CommandNotFound:
            pass
        if not message.content.startswith(self.prefix(None, message)):
            return

        command = message.content.lower()[1:]
        command, to_search = self.parse_search(command)
        msg = self.bot_database.get_message(message.guild.id, command, to_search,
                                            user_is_mod=self.user_can_maintain(message.author, message.channel,
                                                                               message.guild.id))
        if msg == "":
            return
        if message.guild.id in self.last_message_time:
            cooldown_result = self.bot_database.get_server_cooldown(message.guild.id)
            cooldown_result = 30 if cooldown_result < 0 else cooldown_result
            if not (message.created_at - self.last_message_time[message.guild.id]).total_seconds() > cooldown_result:
                await message.add_reaction("⏳")
                return
        self.last_message_time[message.guild.id] = message.created_at
        await message.channel.send(msg)

    @client.event
    async def on_guild_join(self, guild):
        self.bot_database.add_server(guild.id, 30)
        return

    @client.event
    async def on_guild_remove(self, guild):
        # remove_server(conn, guild.id)
        return

    # endregion events

    async def handle_add(self, message, command, new_entry, mod_only=False):
        """add the value in message to the the database"""
        server_id = message.guild.id
        if self.user_can_maintain(message.author, message.channel, message.guild.id):
            if message.mentions or message.role_mentions or message.mention_everyone:
                await self.reject_message(message, NO_MENTIONS_ALLOWED_ERROR
                                          )
                return
            # TODO: actual error class?
            if command[0] == "!":
                await message.channel.send(
                    BANG_NOT_NEEDED_WARNING)
                command = command[1:]
            error = self.validate_add(command, new_entry)
            if error:
                await self.reject_message(message, error)
                return
            if self.bot_database.add_command(server_id, command, new_entry, mod_only=mod_only):
                await message.add_reaction(self.get_emoji(445805262880899075))
                return
        else:
            await self.reject_message(message, INSUFFICIENT_PRIVILEGES_ERROR, True)

    def validate_add(self, command, new_entry):
        if not re.match(self.command_compiled_regex, command):
            return CAN_ONLY_CONTAIN_LETTERS_ERROR
        if len(command) < 3:
            return EXPECTED_SYNTAX_ERROR
        if len(command) >= 20:
            return COMMAND_TOO_LONG_ERROR
        if len(new_entry) > 700:
            return NEW_VALUE_TOO_LONG_ERROR
        if command in self.protected_commands:
            return PROTECTED_COMMAND_ERROR

    async def handle_help(self, message):
        """
        :param message: a discord message
        :return: none
        """
        response = "Available Commands:\n" \
                   "!help - You obviously know this\n" \
                   "!add - Add a new command. Syntax: !add !<command> <message>\n" \
                   "!extractemoji - Get the URL for the emojis in the rest of the message\n" \
                   "See my code: <https://github.com/Brokkoly/BrokkolyBot>\n" \
                   "             <https://github.com/Brokkoly/BrokkolyBotFrontend>\n" \
                   "To see all commands and responses,please go to https://brokkolybot.azurewebsites.net\n" \
                   "Plus the following commands: "
        for command in self.bot_database.get_all_command_strings(message.guild.id):
            response = response + "\n" + "!" + command[0]
        user_dm_channel = message.author.dm_channel
        user_dm_channel = user_dm_channel if user_dm_channel else await message.author.create_dm()
        await user_dm_channel.send(response)
        await message.add_reaction("📧")
        return

    async def handle_extract_emoji(self, message):
        message_from_url = await self.get_message_from_url(message)
        custom_emojis = self.get_emoji_ids(message_from_url if message_from_url else message)
        user_dm_channel = message.author.dm_channel
        user_dm_channel = user_dm_channel if user_dm_channel else await message.author.create_dm()
        await self.send_emoji_urls(custom_emojis, user_dm_channel)
        await message.add_reaction("📧")
        return

    async def handle_timeout(self, message, timeout_hours):
        # todo: just parse it from timeout_hours
        try:
            timeout_time = float(timeout_hours)
        except ValueError:
            # todo: error message
            timeout_time = 0
        timeout_time = timeout_time if timeout_time else self.parse_timeout(message)
        if timeout_time <= 0:
            return
        timeout_time = 0
        try:
            timeout_time = int(round(timeout_time))
        except ValueError:
            timeout_time = 0

        timeout_role_id = await self.get_timeout_role(message.guild)
        for user in message.mentions:
            await self.add_user_timeout(user, timeout_time, message.guild, timeout_role_id)
        return

    async def handle_remove_timeout(self, message):
        timeout_role_id = await self.get_timeout_role(message.guild)
        for user in message.mentions:
            await self.remove_user_timeout(user, message.guild, timeout_role_id)
        return

    @staticmethod
    async def reject_message(message, error, show_message=True):
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

    @staticmethod
    def parse_cooldown(content):
        string_to_parse = content[9:]
        try:
            new_timeout = int(string_to_parse)
        except ValueError:
            return -1
        if new_timeout >= 0:
            return new_timeout
        return -1

    @staticmethod
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

    @staticmethod
    def parse_timeout(content):
        last_greater_than = content.rfind('>')
        try:
            time_in_hours = float(content[last_greater_than + 1:])
        except ValueError:
            return 0
        return time_in_hours

    def get_emoji_ids(self, message):
        custom_emojis = self.get_emoji_ids_from_content(message.content)
        custom_emojis = custom_emojis + self.get_emoji_ids_from_reactions(message)
        return list(dict.fromkeys(custom_emojis))

    @staticmethod
    def get_emoji_ids_from_reactions(message):
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
        url = re.findall(r'https://(?:canary\.)?discord\.com/channels/[0-9]+/[0-9]+/[0-9]+', message.content)
        if (not url) or (not url[0]):
            return ""
        parts = url[0].split('/')
        try:
            message_id = int(parts[-1])
            channel_id = int(parts[-2])
            guild_id = int(parts[-3])
        except ValueError:
            await message.channel.send("Invalid URL")
            return
        guild = await self.fetch_guild(guild_id)
        if not guild:
            await message.channel.send("Sorry, I don't have access to the server that message is from.")
            return ""
        channel = await self.fetch_channel(channel_id)
        if not channel:
            await message.channel.send("Sorry, I don't have access to the channel that message is from.")
            return ""
        other_message = await channel.fetch_message(message_id)
        if other_message and other_message.content:
            return other_message.content
        else:
            return ""

    async def get_message_from_url(self, message):
        url = re.findall(r'https://(?:canary\.)?discord\.com/channels/[0-9]+/[0-9]+/[0-9]+', message.content)
        if (not url) or (not url[0]):
            return ""
        parts = url[0].split('/')
        try:
            message_id = int(parts[-1])
            channel_id = int(parts[-2])
            guild_id = int(parts[-3])
        except ValueError:
            await message.channel.send("Invalid URL")
            return
        guild = await self.fetch_guild(guild_id)
        if not guild:
            await message.channel.send("Sorry, I don't have access to the server that message is from.")
            return None
        channel = await self.fetch_channel(channel_id)
        if not channel:
            await message.channel.send("Sorry, I don't have access to the channel that message is from.")
            return None
        other_message = await channel.fetch_message(message_id)
        if other_message and other_message.content:
            return other_message
        else:
            return None

    @staticmethod
    async def send_emoji_urls(emoji_ids, channel):
        url = "https://cdn.discordapp.com/emojis/{}.{}"
        for e in emoji_ids:
            await channel.send(url.format(str(e[1]), "gif" if e[0] else "png"))

    async def add_user_timeout(self, user, timeout_time, server, role_id):
        await user.add_roles(server.get_role(role_id), reason="Timing out user")
        until_time_ms = int(round(datetime.utcnow().timestamp() * 1000)) + timeout_time * 1000
        self.bot_database.add_user_timeout_to_database(server.id, user.id, until_time_ms)
        return

    async def remove_user_timeout(self, user, server, role_id):
        role = server.get_role(role_id)
        await user.remove_roles(role)
        self.bot_database.remove_user_timeout_from_database(server.id, user.id)
        print("Removed a timeout")
        return

    # todo on channel creation set timeout role permissions in that channel

    async def get_timeout_role(self, server):
        role_id = self.bot_database.get_timeout_role_for_server(server.id)
        if role_id and server.get_role(role_id):
            return role_id
        my_name = server.me.display_name
        role = await server.create_role(name="%s's Timeout Role" % my_name,
                                        permissions=discord.Permissions(send_messages=False),
                                        reason="Creating a role for timing out. Feel free to edit the name but please "
                                               "don't mess with the permissions.")
        # TODO maybe initialize this separately or on startup so that new channels get properly set?
        await self.update_timeout_role_for_server(server, role)

        if role:
            role_id = role.id
            self.bot_database.add_timeout_role_for_server(server.id, role_id)
        else:
            role_id = None
        return role_id

    async def update_timeout_role_for_server(self, server, role=None):
        if not role:
            role = server.get_role(await self.get_timeout_role(server))
        if not role:
            return
        for channel in server.text_channels:
            if channel.permissions_for(server.get_member(self.user.id)).manage_channels:
                await channel.set_permissions(role, send_messages=False)
        return

    async def update_timeout_role_for_all_servers(self):
        for server in self.guilds:
            if not server.get_member(self.user.id).guild_permissions.manage_roles:
                continue
            role = server.get_role(await self.get_timeout_role(server))

            await self.update_timeout_role_for_server(server, role)

    def user_can_maintain_context(self, ctx):
        return self.user_can_maintain(ctx.author, ctx.channel, ctx.guild.id)

    def user_can_maintain(self, author, channel, guild_id):
        if (author.permissions_in(channel).manage_guild):
            return True
        if self.user_has_bot_manager_role(author, guild_id):
            return True

    # def user_can_maintain(self, message):
    #     author = message.author
    #     if author.permissions_in(message.channel).manage_guild:
    #         return True
    #     if self.user_has_bot_manager_role(author, message.guild.id):
    #         return True

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
        if parse_result < 0:
            await self.reject_message(message, "Error! Timeout value must be an integer >=0.")
        else:
            self.bot_database.set_server_cooldown(session.server_id, parse_result)

    async def handle_twitch_add(self, ctx, args):
        channel_name = args[0].lower()
        if not channel_name or "@" in channel_name:
            await ctx.message.channel.send("Error! Invalid twitch channel.")
            return
        discord_user_id = ""
        if ctx.message.mentions and len(ctx.message.mentions) == 1:
            discord_user_id = ctx.message.mentions[0].id
        self.bot_database.add_twitch_user(ctx.message.guild.id, channel_name, discord_user_id)
        # todo check if the channel is already tracked by the server
        await send_refresh_message(channel_name, ctx.message.guild.id)
        # todo tell the server to refresh its streams

    async def handle_twitch_remove(self, ctx, args):
        channel_name = args[0].lower()
        if not channel_name or "@" in channel_name:
            await ctx.message.channel.send("Error! Invalid twitch channel.")
            return
        guild = ctx.message.guild
        twitch_info = self.bot_database.get_server_twitch_info(guild.id)
        mentions = ctx.message.mentions
        discord_user_id = ""
        if len(mentions) > 0:
            if len(mentions) > 1:
                await ctx.message.channel.send("Error! You can only mention one person")
                return
            else:
                user = mentions[0]
                discord_user_id = user.id

        twitch_user = self.bot_database.get_twitch_user_for_server(guild.id, channel_name, discord_user_id)
        if discord_user_id and twitch_user and len(twitch_user) >= 2 and twitch_user[2]:
            if len(twitch_info) >= 2 and twitch_info[1]:
                twitch_role = ctx.message.guild.get_role(int(twitch_info[1]))
                # need a member not just a user
                await guild.get_member(discord_user_id).remove_roles(twitch_role)

        self.bot_database.remove_twitch_user(ctx.message.guild.id, channel_name, discord_user_id)

    @staticmethod
    def get_emoji_tuple(raw_emoji):
        parts = raw_emoji.split(':')
        return parts[0].replace('<', ''), parts[2].replace('>', '')

    @tasks.loop(hours=1)
    async def refresh_streams(self):
        await send_refresh_message()

    @tasks.loop(minutes=1.0)
    async def check_users_to_remove(self):
        users_from_db = self.bot_database.get_user_timeouts_finished(int(round(datetime.utcnow().timestamp() * 1000)))
        if users_from_db:
            for user in users_from_db:
                server_id = int(user[0])
                server = self.get_guild(server_id)
                user_id = user[1]
                user = server.get_member(user_id)
                role_id = self.bot_database.get_timeout_role_for_server(server_id)
                await self.remove_user_timeout(user, server, role_id)


@atexit.register
def shutting_down():
    conn.close()


async def send_refresh_message(username="", server_id=""):
    url = 'https://brokkolybot.azurewebsites.net/api/Twitch/RefreshStreams'
    if username and server_id:
        url += '?username=%s&serverId=%s' % (username, server_id)
    requests.get(url)
    print("Refreshed Streams")


if __name__ == '__main__':
    bot = BrokkolyBot(IS_TEST, token=TOKEN, database_url=DATABASE_URL)
    slash = SlashCommand(bot, override_type=True)
    bot.remove_command("help")


    @bot.command(rest_is_raw=True)
    @commands.check(bot.user_can_maintain_context)
    async def add(ctx, *args):
        await bot.handle_add(ctx.message, args[0].lower(), " ".join(args[1:]))
        await add_manage(ctx.message.guild.id, args[0].lower())
        add_slash(ctx.message.guild.id, args[0].lower())

    @bot.command(rest_is_raw=True)
    @commands.check(bot.user_can_maintain_context)
    async def addmod(ctx, *args):
        await bot.handle_add(ctx.message, args[0].lower(), " ".join(args[1:]), mod_only=True)


    @bot.command()
    async def help(ctx):
        await bot.handle_help(ctx.message)
        return


    @bot.command()
    async def extractemoji(ctx):
        await bot.handle_extract_emoji(ctx.message)
        return


    @bot.command()
    @commands.check(bot.user_can_maintain_context)
    async def timeout(ctx, *args):
        await bot.handle_timeout(ctx.message, args[-1])
        return


    @bot.command()
    @commands.check(bot.user_can_maintain_context)
    async def removetimeout(ctx):
        await bot.handle_remove_timeout(ctx.message)
        return


    @bot.command()
    @commands.check(bot.user_can_maintain_context)
    async def twitchadd(ctx, *args):
        await bot.handle_twitch_add(ctx, args)


    @bot.command()
    @commands.check(bot.user_can_maintain_context)
    async def twitchremove(ctx, *args):
        await bot.handle_twitch_remove(ctx, args)


    @bot.event
    async def on_ready():
        """Fires once the discord bot is ready.
        Notify the test server that the bot has started
        """
        await bot.get_channel(bot_ui_channel_id).send("Starting Up")
        await bot.get_channel(bot_ui_channel_id).send("Online")
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        bot.check_users_to_remove.start()
        bot.refresh_streams.start()
        await bot.update_timeout_role_for_all_servers()
        for g in bot.guilds:
            try:
              commands = await manage_commands.get_all_commands(bot_id=get_bot_id(IS_TEST),bot_token=TOKEN, guild_id=g.id)
              for c in commands:
                  if (c["name"] == "populatecommands"):
                      continue
                  try:
                      slash.add_slash_command(on_slash_command, c["name"], guild_ids=[g.id], options=[{
                          "name": "search",
                          "description": "A substring to search for",
                          "type": 3,
                          "required": "false"
                      }])
                  except(error.DuplicateCommand):
                      continue
            except:
              print("Guild Failed: "+str(g.id))
              print("Guild Failed: "+g.name)
              continue
        await slash.sync_all_commands()
        await bot.get_channel(bot_ui_channel_id).send("Commands Ready")


    # @bot.listen('on_slash_command')
    async def on_slash_command(ctx: SlashContext, *args, **kwargs):
        pass
        # print("in on_slash_command")
        # await bot.handle_slash_command(ctx)


    async def add_manage(guild_id, command):
        try:
            await manage_commands.add_slash_command(
                bot_id=get_bot_id(IS_TEST),
                bot_token=TOKEN,
                guild_id=guild_id,
                cmd_name=command,
                description=command,
                options=[{
                    "name": "search",
                    "description": "A substring to search for",
                    "type": 3,
                    "required": "false"
                }]
            )
        except(error.DuplicateCommand):
            pass


    def add_slash(guild_id, command):
        try:
            slash.add_slash_command(on_slash_command, command, guild_ids=[guild_id])
        except:
            pass


    @slash.slash(name="populateCommands")
    async def populateCommands(ctx: SlashContext):
        await ctx.defer(hidden=True)
        guild_id = ctx.guild.id
        commands = bot.bot_database.get_all_command_strings(guild_id)
        print(guild_id)
        for c in commands:
            command = c[0]
            print(c[0])
            await add_manage(guild_id, command)
            add_slash(guild_id, command)
        await ctx.send(content="Commands Populated", hidden=True)


    # Todo: start thread to refresh stream subscriptions every 24 hours
    bot.run(TOKEN)
