# https://github.com/Rapptz/discord.py/blob/async/examples/reply.py
import discord
import re
import tokens
import madisontokens
import random
accountability = tokens.accountability
TOKEN = tokens.TOKEN
accountabilityMessages = []
accountabilityDates = []
#checkReaction = discord.reaction()
#accountabilityLoad = 0
client = discord.Client()
#global gotChannels = 0
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    #print(message.author.nick)
    #print(message.channel.id)
    print(message.server)
    print(message.server.id)
    #if(not gotChannels):
    for chan in message.server.channels:
        print(chan.name+" = \""+chan.id+"\"")
        #gotChannels = 1
    print(str(message.author))
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

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)
    '''
    if message.content.startswith('!clap'):
        msg = "%s: "%message.author.nick
        msg = msg + message.content[6:].replace(" "," :clap: ")+" :clap:"
        #msg = msg.replace(" "," :clap: ")
        #msg = msg + " :clap:"
        msg = msg.format(message)
        await client.send_message(message.channel, msg)
    '''
    if message.content.startswith('!cclap'):
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


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #print(client.servers)
    accountabilityChannel = client.get_channel(accountability)
    #accountabilityLogs = yielf from client.logs_from(accountabilityChannel)
    regexp = re.compile(r'[0-9](|[0-9])/[0-9](|[0-9])/[0-9][0-9](|[0-9][0-9])')



    async for message in client.logs_from(accountabilityChannel):
        result = regexp.search(message.content)
        if(result): #is an accountable object
            print(message.content)
            #for user in message.get_reaction_users():
            #    if(user == message.author):
            #        print("completed")

            #for reaction in message.reactions:
                #print(reaction.emoji)
                #print(reaction.message.author)
                #print(type(reaction.emoji))
                #print(message.get_reaction_users())
            #check for 



#def on_load_accountability():


client.run(TOKEN)