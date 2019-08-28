# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
import re
import tokens
import random
import time
import asyncio
import atexit
import datetime
import numpy as np
TOKEN = tokens.TOKEN
ready = False
client = discord.Client()

def mentorQuotes():
    retarr=[]
    retarr.append("It's mentor, but instead of monk tokens it makes thalias.")#brokkoly
    retarr.append("The wombo of mentor and astrolabe will shatter moderns foundation")#richard cranium
    retarr.append("\"mentor kills people surprisingly fast\" -Silly")
    retarr.append("\"You might be shocked to hear this, but on a personal level I find that mentor kills people shockingly fast\" -Brokkoly")
    retarr.append("sometimes just terminus your mentor + 3 monk tokens when they have no creatures")
    return retarr
def makeQuotes():
    retarr=[]
    retarr.append("Every time I watch a grixis player cast hymn and die to combo the following turn I have an unreasonable amount of joy.") #kyle
    retarr.append("You incorrectly decided Liliana of the Veil and Hymn are good magic cards.") #kyle
    retarr.append("I'd rather just cast TS and not cross my fingers to either draw the hymn nut or hit their TNN.") #kyle
    retarr.append("Legacy has shifted in a direction where specific cards matter much more than raw quantity. Most of the fair decks have only 4-6 cards that actually matter, so hymn sucks.") #kyle
    retarr.append("People cast hymn on turn 2 against combo because they enjoy losing.") #kyle
    retarr.append("If you sleeve up your first hymn before your third thoughtseize you're just trying to have an early dinner.") #kyle
    retarr.append("I'm sorry you can't afford astrolabe and have to play hymn instead of Leovold and Wrenn and Six.")
    retarr.append("Luck is thinking Hymn makes your deck better. Varience just proves how wrong you are")
    retarr.append("Hymn blows. Feel free to @ me") #kyle
    retarr.append("Hymn isn't a threat in your glacially slow control deck. I really hope they don't recover in the 15 more turns they have.")
    retarr.append("Licking doorknobs is illegal on other planets.")
    return retarr
hymn_quotes=makeQuotes()
mentor_quotes=mentorQuotes()
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    global lastDRS
    global highscoreDRS
    global lastRL
    global highscoreRL
    
    #print(client.user.name)
    print(str(message.author))
    print(message.guild.id==329746807599136769)

    if message.author == client.user:
        return
    if (message.guild.id == 329746807599136769):#and(message.channel.id == "329746807599136769"):#"329746807599136769":
        ###Legacy Discord, only currently uses the drs and rL commands

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
    if (message.content.startswith("!auri")):
        msg ="Ignoring exception in on_message\nTraceback (most recent call last):\nFile \"C:\ProgramData\Anaconda3\lib\site-packages\discord\client.py\", line 270, in _run_event\nawait coro(*args, **kwargs)\nFile \"C:/Users/[REDACTED]/PycharmProjects/BrokkolyBot/brokkoly_bot.py\", line 68, in on_message\nawait message.channel.send(msg)\nFile \"C:\ProgramData\Anaconda3\lib\site-packages\discord\abc.py\", line 823, in send\ndata = await state.http.send_message(channel.id, content, tts=tts, embed=embed, nonce=nonce)\nFile \"C:\ProgramData\Anaconda3\lib\site-packages\discord\http.py\", line 222, in request\nraise HTTPException(r, data)\ndiscord.errors.HTTPException: 400 BAD REQUEST (error code: 50035): Invalid Form Body\nIn content: Must be 2000 or fewer in length."
        await message.channel.send(msg)
    #if(not gotChannels):
    #for chan in message.server.channels:
    #    print(chan.name+" = \""+chan.id+"\"")
        #gotChannels = 1
    #print(str(message.author))
    #if message.author is "Brokkoly#0001":
    #    return
    #print(type(message.author.nick))
    if(str(message.author.nick) == "None"):
        #no nickname
        nick = message.author.name
    else:
        #has nickname
        #print("has Nickname")
        nick = message.author.nick
    
    #if message.content.startswith('!bless'):
    if(str(message.author) == "RedCloakedCrow#3318"):
        if(random.randint(0,10000)<= 10):
            await client.add_reaction(message,"\N{EYE}")
            await client.add_reaction(message,"\N{PERSON WITH FOLDED HANDS}")
            await client.add_reaction(message,"\N{CLOUD WITH RAIN}")
            await client.add_reaction(message,"\N{DOWNWARDS BLACK ARROW}")
            await client.add_reaction(message,"\N{EARTH GLOBE EUROPE-AFRICA}")
    if message.mention_everyone:
        msg = 'Don\'t do that {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
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
    #legacyServerTest()
    #lastDRS = time.time()
    #lastRL = time.time()
    #print(client.servers)
    #if(lastDRS == 0.0):
    #    lastDRS = time.time()
    #if(lastRL == 0.0):
    #    lastRL = time.time()
    #regexp = re.compile(r'[0-9](|[0-9])/[0-9](|[0-9])/[0-9][0-9](|[0-9][0-9])')
    #await legacyServerTest()

def ban_drs_check(message,client):
    regexp = re.compile(r'[bB][aA][nN] (([dD][rR][sS])|[dD]eathrite [sS]haman)')

async def legacyServerTest():
    data = np.empty()
    general_channel_id='329746807599136769'
    general_channel=client.get_channel(general_channel_id)
    scryfall = client.member_id("268547439714238465")
    data=np.empty((0,0,0,0))
    userHash= dict()
    emojiHash= dict()
    messageVals = []
    userIndex=0
    emojiIndex=0
    userNum=0
    emojiNum=0
    authorId=""
    #reactionVals = []
    extractedMessages=[]
    regexstr=re.compile(r'')
    async for message in general_channel.history(limit=10):
        if message.author==scryfall:
            continue
        else:
            messageVals = parse_message(message)
            if len(messageVals[3])>0:
                extractedMessages.append(messageVals)
                #print("Author Id: {}".format(messageVals[0]))
                #print("Author Name: {}".format(client.get_user(messageVals[0])))
                #print("Channel Id: {}".format(messageVals[1]))
                #print("Channel Name: {}".format(client.get_channel(messageVals[1])))
                #print("Date info: {}".format(messageVals[2]))
                #print("Emoji ids: {}".format((messageVals[3])))
    compileNumbers(extractedMessages)
            #reactionVals= parseReactions(message)

def parse_message(message):
    retval=[]
    retval.append(message.author.id)
    retval.append(message.channel.id)
    retval.append(message.created_at)
    custom_emojis = re.findall(r'<:\w*:\d*>', message.content)
    #print(message.content)
    #rint(custom_emojis)
    custom_emojis = [int(e.split(':')[2].replace('>', '')) for e in custom_emojis]
    #custom_emojis = [client.get_emoji(e) for e in custom_emojis]
    retval.append(custom_emojis)
    return retval

def compileNumbers(messages):
    print("Compiling Data")
    print("Length of messages: {}".format(len(messages)))
    data=dict()
    for message in messages:
        for e in message[3]:
            if str(e) in data:
                data[str(e)]+=1
            else:
                data[str(e)]=1
    print(data)
    print("Length of dict: {}".format(len(data.keys())))
    for e in data:
        print(e)
        #print(discord.utils.get(client.emojis,id=int(e)))
        emoji = discord.utils.get(client.emojis,id=int(e))
        print(":{}: : ".format(str(emoji),data[str(e)]))


def loadStuff():
    global lastDRS
    global lastRL
    global highscoreDRS
    global highscoreRL
    rfile = open("botstuff.txt","r")
    lastDRS = float(rfile.readline())
    print("lastdrs: %f"%lastDRS)
    lastRL = float(rfile.readline())
    print("lastRL: %f"%lastRL)
    highscoreDRS = float(rfile.readline())
    print("highscoredrs: %f"%highscoreDRS)
    highscoreRL = float(rfile.readline())
    print("highscoreRL: %f"%highscoreRL)
    rfile.close()

def saveStuff():
    global lastDRS
    global lastRL
    global highscoreDRS
    global highscoreRL
    wfile = open("botstuff.txt","w+")
    wfile.write(str(lastDRS)+"\n")
    wfile.write(str(lastRL)+"\n")
    wfile.write(str(highscoreDRS)+"\n")
    wfile.write(str(highscoreRL)+"\n")
    wfile.close()
atexit.register(saveStuff)
loadStuff()
client.run(TOKEN)