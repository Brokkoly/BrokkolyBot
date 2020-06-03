# TODO Get ~~and validate~~ input for new commands
# TODO Time out users who abuse the bot
# TODO Properly figure out if we're on heroku or running locally
# TODO In chat maintenance of the string library
# TODO Figure out performance of stripping command from string before doing manipulation when adding
# TODO Make a channel where adding is allowed instead of a server.
# TODO Internationalize? No, that costs money
import atexit
import random
import re

import discord

import tokens

# s3 = S3Connection(os.environ['TOKEN'])
TOKEN = None
# if not s3.access_key(['Token']):
TOKEN = tokens.TOKEN
# else
#    TOKEN =s3.access_key(['Token'])
ready = False
client = discord.Client()


def add_to_map(command_map, command, message):
    if not command in command_map:
        command_map[command] = []
    if not message in command_map[command]:
        command_map[command].append(message)


def get_all_quotes():
    read_file = open("botdb.txt", "r")
    command_map = {}
    lines = read_file.readlines()
    for line in lines:
        first_space = line.find(" ")
        command = line[:first_space]
        message = line[first_space + 1:]

        add_to_map(command_map, command, message)
    read_file.close()
    return command_map


brokkoly_favicon = None
command_map = get_all_quotes()
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528
game_jazz_id = 639124326385188864
author_whitelist = [146687253370896385  # me
    , 115626912394510343  # ori
    , 200773608094564352  # wind
    , 716358081222672404  # thaya
    , 185287142388400129  # thalia
    , 120756475768471554  # solyra
                    ]
# TODO Check roles instead of just ids
lastDRS = None
highScoreDRS = None
lastRL = None
highScoreRL = None
after_add_regex_string = r'(?<!.)(?!![aA]dd)![A-zA-Z]{3,} .+'  # we've already stripped "!add" from the message
after_add_compiled_regex = re.compile(after_add_regex_string)
timeout = {
    mtg_legacy_discord_id: 60,
    brokkolys_bot_testing_zone_id: 5
}
last_message_time = {}
random.seed()


@client.event
async def on_message(message):
    global brokkoly_favicon
    is_timed_out = True
    # old_timeout_time = last_message_time[message.guild.id]
    if not message.guild.id == brokkolys_bot_testing_zone_id:
        return

    # Don't reply to our own messages
    if message.author == client.user:
        return
    if not message.content.startswith("!"):
        return
    if message.content.startswith("!estop") and message.author.id in author_whitelist:
        brokkoly = client.get_user(146687253370896385)
        brokkoly_dm = await brokkoly.create_dm()
        await brokkoly_dm.send("Emergency Stop Called. Send Help.")
        await message.channel.send("<:notlikeduck:522871146694311937>\n<:Heck:651250241722515459>")
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
        # todo should we allow people to use !help and not have it affect the time
        # last_message_time[message.guild.id]=old_timeout_time

    if (message.content.startswith("!add ")):
        if (message.author.id in author_whitelist):
            if len(message.mentions) > 0 or len(message.role_mentions) > 0 or message.mention_everyone:
                await reject_message(message, "Error! No mentions allowed.")
                return
            result = parse_add(message.content)
            if result[0]:
                if (len(result[1]) > 21):
                    await reject_message(message, "Error! Command cannot be longer than 20 characters.")
                    return
                if len(result[2]) > 500:
                    await reject_message(message, "Error! Message cannot be longer than 500 characters.")
                    return
                if result[1]=="!help" or result[1] == "!add" or result[1] == "!estop" or result[1] == "!otherservers":
                    await reject_message(message, "Error! That is a protected command")
                    #todo make this into its own list
                result[1] = result[1].lower()
                add_to_file(result[1], result[2])
                add_to_map(command_map, result[1], result[2])
                await message.add_reaction(client.get_emoji(445805262880899075))
                return
            else:
                await reject_message(message, "Error! Expected \"!add !<command length at least 3> <message>\".")
                return
        else:
            await reject_message(message, "Error! Insufficient privileges to add.")

    if message.guild.id in last_message_time and message.guild.id in timeout and \
            not (message.created_at - last_message_time[message.guild.id]).total_seconds() > timeout[message.guild.id]:
        return
    else:
        is_timed_out = False
        last_message_time[message.guild.id] = message.created_at

    command = message.content.lower()
    if command in command_map:
        msg = random.choice(command_map[command])
        await message.channel.send(msg)
    else:
        await reject_message(message, "Error! Command Not Found.")

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
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


async def reject_message(message, error):
    await message.add_reaction("❌")
    await message.channel.send(error)


def parse_add(content):
    string_to_parse = content[5:]  # Cut off the add since we've already matched
    # TODO figure out if doing string slicing costs more than just regexing
    if re.fullmatch(after_add_compiled_regex, string_to_parse):
        first_space = string_to_parse.find(" ")
        command = string_to_parse[:first_space]
        message = string_to_parse[first_space + 1:]
        return [True, command, message]
    else:
        return [False]


def add_to_file(command, message):
    write_file = open("botdb.txt", "a")
    write_file.write(command + " " + message)
    write_file.write("\n")
    write_file.close()


def parse_message(message):
    retval = []
    retval.append(message.author.id)
    retval.append(message.channel.id)
    retval.append(message.created_at)
    custom_emojis = re.findall(r'<:\w*:\d*>', message.content)
    # print(message.content)
    # rint(custom_emojis)
    custom_emojis = [int(e.split(':')[2].replace('>', '')) for e in custom_emojis]
    # custom_emojis = [client.get_emoji(e) for e in custom_emojis]
    retval.append(custom_emojis)
    return retval


def compileNumbers(messages):
    print("Compiling Data")
    print("Length of messages: {}".format(len(messages)))
    data = dict()
    for message in messages:
        for e in message[3]:
            if str(e) in data:
                data[str(e)] += 1
            else:
                data[str(e)] = 1
    print(data)
    print("Length of dict: {}".format(len(data.keys())))
    for e in data:
        print(e)
        # print(discord.utils.get(client.emojis,id=int(e)))
        emoji = discord.utils.get(client.emojis, id=int(e))
        print(":{}: : ".format(str(emoji), data[str(e)]))


# atexit.register(saveStuff)
client.run(TOKEN)
