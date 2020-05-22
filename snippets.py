'''
   if message.content.startswith('!clap'):
       msg = "%s: "%message.author.nick
       msg = msg + message.content[6:].replace(" "," :clap: ")+" :clap:"
       #msg = msg.replace(" "," :clap: ")
       #msg = msg + " :clap:"
       msg = msg.format(message)
       await client.send_message(message.channel, msg)
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