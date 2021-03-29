import os
import sys
import datetime

import discord
from discord.ext.commands import Bot

my_bot = Bot(command_prefix="!")

global_filename = ''
global_guildid = 0

def main():
    try:
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(location, 'token.txt'), 'r')
        my_bot.run(f.read().split('\n')[0], bot=True)
    except discord.errors.LoginFailure as e:
        print(e, 'Try adding the `--bot` flag.')

@my_bot.event
async def on_ready():
    print("Backup bot logged in.")
    await make_logs()
    #await my_bot.logout()
    
async def make_logs():
    for guild in my_bot.guilds:
        for channel in guild.channels:
            if channel.name == "general" and isinstance(channel, discord.TextChannel):
                if channel.permissions_for(guild.get_member(my_bot.user.id)).read_message_history:
                    sys.stdout.write("Logging {0}:".format(channel.name))
                    sys.stdout.flush()
                    after = datetime.datetime(2015,3,1)
                    async for message in channel.history(limit=None,after=after):
                        at = ",".join([i.url for i in message.attachments])
                        if len(at) > 0:
                            at = " " + at
                        message = {"author":message.author.id, "time":message.created_at, "content":message.content + at}
                        print(message)
                        #print((channel.id), (message.author.id, message.created_at, message.content + " " + at))
                    print("\rLogging {0}: [DONE]            ".format(channel.name))
    print("LOGS FINISHED")

if __name__ == '__main__':
    #my_bot.run(open('token.txt','r').read().split('\n')[0], bot=False)
    main()