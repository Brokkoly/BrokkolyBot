# TODO Get ~~and validate~~ input for new commands
# TODO Turn strings into a data file instead of a function
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
from quote_arrays import *

# s3 = S3Connection(os.environ['TOKEN'])
TOKEN = None
# if not s3.access_key(['Token']):
TOKEN = tokens.TOKEN
# else
#    TOKEN =s3.access_key(['Token'])
ready = False
client = discord.Client()
hymn_quotes = get_hymn_quotes()
mentor_quotes = get_mentor_quotes()
labe_tweets = get_labe_tweets()
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528
game_jazz_id = 639124326385188864
lastDRS = None
highScoreDRS = None
lastRL = None
highScoreRL = None
after_add_regex_string = r'(?<!.)(?!![aA]dd)![A-zA-Z]{3,} .+'  # we've already stripped "!add" from the
after_add_compiled_regex = re.compile(after_add_regex_string)
random.seed()


@client.event
async def on_message(message):
    # print(str(message.author))
    # print(message.guild.id==329746807599136769)
    # print(message.content)

    # Don't reply to our own messages
    if message.author == client.user:
        return
    # if message.guild.id == 329746807599136769:
    # print(message.author.nick)
    # print(message.channel.id)
    # print(message.guild)
    # print(message.guild.id)
    if message.guild.id == brokkolys_bot_testing_zone_id:
        if (message.content.startswith("!add ")):
            string_to_parse = message.content[5:]  # Cut off the add since we've already matched
            if re.fullmatch(after_add_compiled_regex, string_to_parse):
                first_space = string_to_parse.find(" ")
                command = string_to_parse[:first_space]
                message = string_to_parse[first_space:]

                # TODO add to file or add to approval queue
                return
            else:
                message.channel.send("Error! Expected \"!add !<command> <message>\"")
                # TODO add error message
                return

    if message.content.startswith("!hymn"):
        msg = random.choice(hymn_quotes)
        await message.channel.send(msg)
    if message.content.startswith("!mentor"):
        msg = random.choice(mentor_quotes)
        await message.channel.send(msg)
    if message.content.startswith("!labe") or message.content.startswith("!astrolabe"):
        msg = random.choice(labe_tweets)
        await message.channel.send(msg)
    if message.guild.id == game_jazz_id and message.content.startswith("!gamejazz"):
        """If you're reading this go listen to game jazz, it's a good podcast"""
        # TODO load random game type
        # TODO load random game modifier
        # TODO send great game idea
        # TODO syntax and proper detection of plurals
        return
    """
    if(not gotChannels):
    for chan in message.server.channels:
        print(chan.name+" = \""+chan.id+"\"")
        gotChannels = 1
    print(str(message.author))
    if message.author is "Brokkoly#0001":
        return
    print(type(message.author.nick))
    """
    if str(message.author == "RedCloakedCrow#3318"):
        if (random.randint(0, 10000) <= 10):
            await message.add_reaction("\N{EYE}")
            await message.add_reaction("\N{PERSON WITH FOLDED HANDS}")
            await message.add_reaction("\N{CLOUD WITH RAIN}")
            await message.add_reaction("\N{DOWNWARDS BLACK ARROW}")
            await message.add_reaction("\N{EARTH GLOBE EUROPE-AFRICA}")
    if message.mention_everyone:
        msg = 'Don\'t do that {0.author.mention}'.format(message)
        await message.channel.send(msg)
    '''
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    '''


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global lastDRS
    global lastRL


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


def loadStuff():
    global lastDRS
    global lastRL
    global highscoreDRS
    global highscoreRL
    rfile = open("botstuff.txt", "r")
    lastDRS = float(rfile.readline())
    print("lastdrs: %f" % lastDRS)
    lastRL = float(rfile.readline())
    print("lastRL: %f" % lastRL)
    highscoreDRS = float(rfile.readline())
    print("highscoredrs: %f" % highscoreDRS)
    highscoreRL = float(rfile.readline())
    print("highscoreRL: %f" % highscoreRL)
    rfile.close()


def saveStuff():
    global lastDRS
    global lastRL
    global highscoreDRS
    global highscoreRL
    wfile = open("botstuff.txt", "w+")
    wfile.write(str(lastDRS) + "\n")
    wfile.write(str(lastRL) + "\n")
    wfile.write(str(highscoreDRS) + "\n")
    wfile.write(str(highscoreRL) + "\n")
    wfile.close()


atexit.register(saveStuff)
loadStuff()
client.run(TOKEN)
