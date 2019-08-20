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
<<<<<<< HEAD
=======
TOKEN = tokens.TOKEN
>>>>>>> be1286ca92c6446c433ad2329112d1c71cccb38d

ready = False
client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    global lastDRS
    global highscoreDRS
    global lastRL
    global highscoreRL
    
    #print(client.user.name)
    #print(str(message.author))

    if message.author == client.user:
        return
    if (message.guild.id == "225374061386006528")and(message.channel.id == "329746807599136769"):#"329746807599136769":
        ###Legacy Discord, only currently uses the drs and rL commands

        # if(message.author.roles.id == "449799376387440642"):
        #
        #     if(message.content.startswith("!drs")):
        #         time_since = (time.time()-lastDRS)/86400.0
        #         lastDRS = time.time()
        #         print(lastDRS)
        #         msg = "DRS banning conversation detected! Resetting counter. Y'all made it %.4f days without talking about it"%time_since
        #
        #         if(time_since > highscoreDRS):
        #             msg = msg + "\nYou set a new high score! The previous high score was %.4f days!"%highscoreDRS
        #             highscoreDRS = time_since
        #
        #         await client.send_message(message.channel,msg)
        #         return
        #     if message.content.startswith("!checkdrs"):
        #         time_since = (time.time()-lastDRS)/86400.0
        #         msg = "Last drs conversation occured %.4f days ago. Current highscore: %.4f days."%(time_since,highscoreDRS)
        #         await client.send_message(message.channel,msg)
        #         return
        #     if(message.content.startswith("!rl")):
        #         time_since = (time.time()-lastDRS)/86400.0
        #         lastDRS = time.time()
        #
        #         msg = "Reserved list conversation detected! Resetting counter. Y'all made it %.4f days without talking about it"%time_since
        #
        #         if(time_since > highscoreRL):
        #             msg = msg + "\nYou set a new high score! The previous high score was %.4f days!"%highscoreRL
        #             highscoreRL = time_since
        #         await client.send_message(message.channel,msg)
        #         return
        #     if message.content.startswith("!checkrl"):
        #         time_since = (time.time()-lastDRS)/86400.0
        #         msg = "Last reserved list conversation occured %.4f days ago. Current highscore: %.4f days."%(time_since,highscoreRL)
        #         return
        #     if message.content.startswith("!help"):
        #         msg = "!drs: mark a new deathrite banning conversation\n"
        #         msg = msg+"!rl: mark a new reserved list conversation\n"
        #         msg = msg+"!drscheck: check the time since and highscore for the deathrite clock"
        #         msg = msg+"!rlcheck: check the time since and highscore for the reserved list clock"
        #         await client.send_message(message.channel,msg)
        #         return

        print(message.author.nick)
        print(message.channel.id)
        print(message.guild)
        print(message.guild.id)

        return
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
    '''
    if(str(message.author) == "RedCloakedCrow#3318"):
        if(random.randint(0,10000)<= 10):
            await client.add_reaction(message,"\N{EYE}")
            await client.add_reaction(message,"\N{PERSON WITH FOLDED HANDS}")
            await client.add_reaction(message,"\N{CLOUD WITH RAIN}")
            await client.add_reaction(message,"\N{DOWNWARDS BLACK ARROW}")
            await client.add_reaction(message,"\N{EARTH GLOBE EUROPE-AFRICA}")
    '''
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
    legacyServerTest()
    #lastDRS = time.time()
    #lastRL = time.time()
    #print(client.servers)
    #if(lastDRS == 0.0):
    #    lastDRS = time.time()
    #if(lastRL == 0.0):
    #    lastRL = time.time()
    #regexp = re.compile(r'[0-9](|[0-9])/[0-9](|[0-9])/[0-9][0-9](|[0-9][0-9])')
    await legacyServerTest()

def ban_drs_check(message,client):
    regexp = re.compile(r'[bB][aA][nN] (([dD][rR][sS])|[dD]eathrite [sS]haman)')

def legacyServerTest():
    data = np.empty()
    general_channel_id='329746807599136769'
    general_channel=get_channel(general_channel_id)
    scryfall = member_id("268547439714238465")
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
    regexstr=re.compile(r'')
    async for message in channel.history(limit=10):
        if message.author=scryfall:
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