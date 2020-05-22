import discord
import re
import tokens
import random
import atexit
from quote_arrays import *

TOKEN = tokens.TOKEN
ready = False
client = discord.Client()
hymn_quotes = get_hymn_quotes()
mentor_quotes = get_mentor_quotes()
labe_tweets = get_labe_tweets()
mtg_legacy_discord_id = 329746807599136769
brokkolys_bot_testing_zone_id = 225374061386006528


@client.event
async def on_message(message):
    global lastDRS
    global highscoreDRS
    global lastRL
    global highscoreRL

    # print(str(message.author))
    # print(message.guild.id==329746807599136769)
    # print(message.content)

    # Don't reply to our own messages
    if message.author == client.user:
        return
    if (
            message.guild.id == 329746807599136769):  # and(message.channel.id == "329746807599136769"):#"329746807599136769":

        print(message.author.nick)
        print(message.channel.id)
        print(message.guild)
        print(message.guild.id)

    if (message.content.startswith("!hymn")):
        msg = random.choice(hymn_quotes)
        await message.channel.send(msg)
    if (message.content.startswith("!mentor")):
        msg = random.choice(mentor_quotes)
        await message.channel.send(msg)
    if (message.content.startswith("!labe") or message.content.startswith("!astrolabe")):
        msg = random.choice(labe_tweets)
        await message.channel.send(msg)
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
    if (str(message.author.nick) == "None"):
        # no nickname
        nick = message.author.name
    else:
        # has nickname
        # print("has Nickname")
        nick = message.author.nick

    # if message.content.startswith('!bless'):
    if (str(message.author) == "RedCloakedCrow#3318"):
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
    '''
    if message.content.startswith('!clap'):
        msg = "%s: "%message.author.nick
        msg = msg + message.content[6:].replace(" "," :clap: ")+" :clap:"
        #msg = msg.replace(" "," :clap: ")
        #msg = msg + " :clap:"
        msg = msg.format(message)
        await client.send_message(message.channel, msg)
    '''
    '''
    if message.content.startswith('!clap'):
        msg = "%s: "%nick
        msg = msg + message.content[6:].replace(" "," :clap: ")+" :clap:"
        #id = message.id

        #msg = msg.replace(" "," :clap: ")
        #msg = msg + " :clap:"
        msg = msg.format(message)

        await client.send_message(message.channel, msg)
        try:
            await client.delete_message(message)
        except discord.Forbidden:
            print("Don't have permissions")
        except discord.HTTPException:
            print("Other Error")
    #if message.content.startswith('!help')
    '''


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global lastDRS
    global lastRL
    # legacyServerTest()
    # lastDRS = time.time()
    # lastRL = time.time()
    # print(client.servers)
    # if(lastDRS == 0.0):
    #    lastDRS = time.time()
    # if(lastRL == 0.0):
    #    lastRL = time.time()
    # regexp = re.compile(r'[0-9](|[0-9])/[0-9](|[0-9])/[0-9][0-9](|[0-9][0-9])')
    # await legacyServerTest()


# def ban_drs_check(message,client):
#     regexp = re.compile(r'[bB][aA][nN] (([dD][rR][sS])|[dD]eathrite [sS]haman)')

# async def legacyServerTest():
#     data = np.empty()
#     general_channel_id='329746807599136769'
#     general_channel=client.get_channel(general_channel_id)
#     scryfall = client.member_id("268547439714238465")
#     data=np.empty((0,0,0,0))
#     userHash= dict()
#     emojiHash= dict()
#     messageVals = []
#     userIndex=0
#     emojiIndex=0
#     userNum=0
#     emojiNum=0
#     authorId=""
#     #reactionVals = []
#     extractedMessages=[]
#     regexstr=re.compile(r'')
#     async for message in general_channel.history(limit=10):
#         if message.author==scryfall:
#             continue
#         else:
#             messageVals = parse_message(message)
#             if len(messageVals[3])>0:
#                 extractedMessages.append(messageVals)
#                 #print("Author Id: {}".format(messageVals[0]))
#                 #print("Author Name: {}".format(client.get_user(messageVals[0])))
#                 #print("Channel Id: {}".format(messageVals[1]))
#                 #print("Channel Name: {}".format(client.get_channel(messageVals[1])))
#                 #print("Date info: {}".format(messageVals[2]))
#                 #print("Emoji ids: {}".format((messageVals[3])))
#     compileNumbers(extractedMessages)
#             #reactionVals= parseReactions(message)

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
random.seed()
client.run(TOKEN)
