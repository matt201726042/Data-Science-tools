from re import A
import discord
from discord.ext.commands import Bot
import numpy as np
import os
import sys
import datetime
import scipy.interpolate
import lda

global INFO,LOG

try:
    LOG = np.load("chatBotLog.npy", allow_pickle=True).tolist()
except:
    LOG = np.array([])
    np.save("chatBotLog.npy", LOG)
    LOG = LOG.tolist()
try:
    INFO = np.load("chatBotInfo.npy", allow_pickle=True).tolist()
except:
    INFO = np.array({"lastLog":datetime.datetime.fromtimestamp(1457045302)})
    np.save("chatBotInfo.npy", INFO)
    INFO = INFO.tolist()

intents = discord.Intents.all()
my_bot = Bot(command_prefix="!", intents=intents)

#############################################################

contextWProf = [1,0] #Weight profile
contextLen = 10
contextWProfInterp = scipy.interpolate.PchipInterpolator(np.linspace(0,contextLen-1, num=len(contextWProf)), contextWProf)

reptWProf = [100,0]
reptWTime = [0, 60*60] #seconds
reptCap = 20
reptWProfInterp = scipy.interpolate.PchipInterpolator([0, 60*60], [1,0])

def reptWeighter(msg):
    rLOG = LOG[::-1]
    i = -1
    out = 1
    beforeBound = True
    while beforeBound and i < reptCap:
        i += 1
        delta = (datetime.datetime.now() - rLOG[i]["time"]).total_seconds()
        if delta > reptWTime[-1]:
            beforeBound = False
        elif rLOG[i]["author"] == msg["author"]:
            out += reptWProfInterp(delta) * lda.LDAquery(LDAMODEL, LDADICT, [msg["content"], rLOG[i]["content"]])
    return out

imitate = 316988873710501888

def main():
    try:
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(location, 'token.txt'), 'r')
        my_bot.run(f.read().split('\n')[0], bot=True)
    except discord.errors.LoginFailure as e:
        print(e, 'Try adding the `--bot` flag.')

@my_bot.event
async def on_message(message):
    print("LOGGED", message.created_at, message.channel.name, ":", message.author.name, ":", message.content)
    at = ",".join([i.url for i in message.attachments])
    if len(at) > 0:
        at = " " + at
    mes = {"author":message.author.id, "time":message.created_at, "content":message.content + at}
    LOG.append(mes)
    np.save("chatBotLog.npy", LOG)
    
    if message.author.id != 826150125206110208 and message.channel.name == "dorime":
        realContext = LOG[-contextLen:]
        y = []
        LOGlen = len(LOG) - 1
        sims = []
        y = []
        for i in range(1, len(LOG)):
            if i % 40 == 0:
                print(100 * (i/LOGlen), "%")
            sims.append([])
            print([c["content"] for c in LOG[:10]])
            print([c["content"] for c in LOG[:i]], LOG[i]["content"])
            a = lda.LDAquery(LDAMODEL, LDADICT, [c["content"] for c in LOG[:i]], LOG[i]["content"])
            for i in range(len(a)):
                sims[i].append(a)
            sims[i] = sims[i][-10:]
            msg = LOG[LOGlen-(i)]["content"]
            weights = contextWProfInterp([k for k in range((LOGlen+1)-i, 0, -1)])
            rW = reptWeighter(msg)
            print(sims, weights)
            y.append((np.average(sims, weights=weights) / rW, msg))
        a = sorted(y, key=lambda x: x[0])
        for i in range(len(a)):
            if a[i][1]["author"] == imitate and len(a[i][1]["content"]) > 0:
                out = a[i]
        print("---------")
        print("RESPONSE:", out)
        print(a[:10])
        print("---------")
        try:
            await message.channel.send(out[1]["content"])
        except:
            pass
        if message.content.startswith('!'):
            print("I've seen a message!")
            await message.channel.send("epical")

@my_bot.event
async def on_ready():
    print("Message loader logged in.")
    await make_logs()
    await make_model()
    print("-------------------------------------------------")
    #await my_bot.logout()
    
async def make_model():
    global LDAMODEL, LDADICT
    LDAMODEL, LDADICT = lda.LDAtrain([msg["content"] for msg in LOG])
    print("Model made.")

async def make_logs():
    prevLog = INFO["lastLog"]
    print("The last log was", prevLog)
    INFO["lastLog"] = datetime.datetime.now()
    for guild in my_bot.guilds:
        for channel in guild.channels:
            if channel.name == "general" and isinstance(channel, discord.TextChannel):
                if channel.permissions_for(guild.get_member(my_bot.user.id)).read_message_history:
                    sys.stdout.write("Logging {0}:".format(channel.name))
                    sys.stdout.flush()
                    async for message in channel.history(limit=None,after=prevLog):
                        if message.content != '':
                            at = ",".join([i.url for i in message.attachments])
                            if len(at) > 0:
                                at = " " + at
                            message = {"author":message.author.id, "time":message.created_at, "content":message.content + at}
                            LOG.append(message)
                        #print((channel.id), (message.author.id, message.created_at, message.content + " " + at))
                    print("\rLogging {0}: [DONE]            ".format(channel.name))
    #print(LOG)
    np.save("chatBotLog.npy", LOG)
    np.save("chatBotInfo.npy", INFO)
    print("Logs made, length", len(LOG))

if __name__ == '__main__':
    #my_bot.run(open('token.txt','r').read().split('\n')[0], bot=False)
    main()