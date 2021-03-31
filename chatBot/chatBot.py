from re import A
import discord
from discord.ext.commands import Bot
import numpy as np
import os
import sys
import datetime
import scipy.interpolate
import lda
import levenshtein
import random

intents = discord.Intents.all()
my_bot = Bot(command_prefix="!", intents=intents)

global INFO,LOG
ASYNCCOUNT = 0

try:
    LOG = np.load("chatBotLog.npy", allow_pickle=True).tolist()
except:
    LOG = np.array([])
    np.save("chatBotLog.npy", LOG)
    LOG = LOG.tolist()
try:
    INFO = np.load("chatBotInfo.npy", allow_pickle=True).tolist()
except:
    INFO = np.array({"lastLog":datetime.datetime.fromtimestamp(1457045302), "counts":{}})
    np.save("chatBotInfo.npy", INFO)
    INFO = INFO.tolist()

contextWProf = [1,0] #Weight profile
contextLen = 10
contextWProfInterp = scipy.interpolate.PchipInterpolator(np.linspace(0,contextLen-1, num=len(contextWProf)), contextWProf)

reptWProf = [9,0]
reptWTime = [0, 60*60*60] #seconds
reptCap = 10
reptWProfInterp = scipy.interpolate.PchipInterpolator(reptWTime, reptWProf)

#############################################################

def reptWeighter(msg):
    rLOG = LOG[::-1]
    i = -1
    out = 1
    beforeBound = True
    j = 0
    while beforeBound and i < reptCap:
        j += 1
        delta = (datetime.datetime.utcnow() - rLOG[j]["time"]).total_seconds()
        if delta > reptWTime[-1]:
            beforeBound = False
        elif rLOG[j]["author"] == msg["author"]:
            i += 1
            #print(reptWProfInterp(delta), lda.LDAquery(LDAMODEL, LDADICT, [msg["content"], rLOG[i]["content"]]), levenshtein.levenshtein(msg["content"], rLOG[i]["content"]))
            out += reptWProfInterp(delta) * (lda.LDAquery(LDAMODEL, LDADICT, [msg["content"], rLOG[i]["content"]])) #levenshtein.levenshtein(msg["content"], rLOG[i]["content"])
    return out

imitate = 287257198436810762

def main():
    print("Python script started.")
    try:
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(location, 'token.txt'), 'r')
        my_bot.run(f.read().split('\n')[0], bot=True)
    except discord.errors.LoginFailure as e:
        print(e, 'Try adding the `--bot` flag.')

def logNewMessage(message):
    at = ",".join([i.url for i in message.attachments])
    if len(at) > 0:
        at = " " + at
    mes = {"author":message.author.id, "time":message.created_at, "content":message.content + at}
    LOG.append(mes)
    np.save("chatBotLog.npy", LOG)
    try:
        INFO["counts"][message.author.id] += 1
    except:
        INFO["counts"][message.author.id] = 0
    #LDAMODEL.update([mes["content"]])
    print("LOGGED (" + str(len(LOG)) + ")", message.created_at, message.channel.name, ":", message.author.name, ":", message.content)

@my_bot.event
async def on_message(message):
    global ASYNCCOUNT
    if message.channel.name == "general" or message.channel.name == "dorime":
        if message.author.id != 826150125206110208:
            logNewMessage(message)
    
    if message.author.id != 826150125206110208 and message.channel.name == "dorime" and ASYNCCOUNT < 3:
        ASYNCCOUNT += 1
        myreplyobj = await message.reply("0%", mention_author=False)
        try:
            realContext = LOG[-contextLen:]
            y = []
            LOGlen = len(LOG) - 1
            LOGcap = 1000
            ratio = LOGcap/INFO["counts"][message.author.id]
            if ratio > 1:
                ratio = 1
            compress = random.choices([True, False], weights=[1-ratio, ratio], k=LOGlen)
            for i in range(LOGlen):
                msg = LOG[i+1]
                if msg["author"] == imitate and not compress[i]:
                    if i % 100 == 0:
                        await myreplyobj.edit(content=str(np.round(100 * (i/LOGlen), 2)) + "%")
                        print(100 * (i/LOGlen), "%")
                    if i < contextLen:
                        start = 0
                    else:
                        start = (i+1) - contextLen
                    cLen = (i+1)-start
                    context = LOG[start:i+1]
                    msg = LOG[i+1]
                    sims = []
                    weights = []
                    rW = reptWeighter(msg)
                    authorChecks = []
                    for c in range(cLen):
                        sims.append(lda.LDAquery(LDAMODEL, LDADICT, [realContext[c]["content"], context[c]["content"]]))
                        weights.append(contextWProfInterp(cLen-c))
                        if realContext[c]["author"] == context[c]["author"]:
                            authorChecks.append(1)
                        else:
                            authorChecks.append(0)
                    y.append(((np.average(sims, weights=weights) + np.average(authorChecks, weights=weights)) / rW, msg))
            a = sorted(y, key=lambda x: x[0])
            out = None
            for i in range(len(a)):
                if a[i][1]["author"] == imitate and len(a[i][1]["content"]) > 0:
                    out = a[i]
            if out != None:
                print("---------")
                print("RESPONSE:", out)
                print(a[:10])
                print("---------")
                try:
                    await myreplyobj.edit(content=out[1]["content"])
                    logNewMessage(myreplyobj)
                except:
                    pass
            else:
                await myreplyobj.delete()
        except Exception as e:
            myreplyobj.delete()
            print("Exception in trying to respond:", e)

        if message.content.startswith('!'):
            print("I've seen a message!")
            await message.channel.send("epical")
        ASYNCCOUNT -= 1

@my_bot.event
async def on_ready():
    print("Bot logged in.")
    print("-------------------------------------------------")
    await make_logs()
    print("-------------------------------------------------")
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
    print("INFO:", INFO)
    for guild in my_bot.guilds:
        for channel in guild.channels:
            if channel.name == "general" and isinstance(channel, discord.TextChannel):
                if channel.permissions_for(guild.get_member(my_bot.user.id)).read_message_history:
                    print("Do you want to log this channel? y/n", guild.name, channel.name)
                    shallIContinue = input("")
                    if shallIContinue == "y":
                        sys.stdout.write("Logging {0}:".format(channel.name))
                        sys.stdout.flush()
                        i = 0
                        async for message in channel.history(limit=None,after=prevLog):
                            try:
                                i += 1
                                print(i)
                                if message.content != '':
                                    at = ",".join([i.url for i in message.attachments])
                                    if len(at) > 0:
                                        at = " " + at
                                    msg = {"author":message.author.id, "time":message.created_at, "content":message.content + at}
                                    LOG.append(msg)
                                    try:
                                        INFO["counts"][message.author.id] += 1
                                    except:
                                        INFO["counts"][message.author.id] = 0
                                #print((channel.id), (message.author.id, message.created_at, message.content + " " + at))
                            except Exception as e:
                                print(e)
                        if i != 0:
                            INFO["lastLog"] = datetime.datetime.now()
                        print("\rLogging {0}: [DONE]            ".format(channel.name))
    #print(LOG)
        np.save("chatBotLog.npy", LOG)
        np.save("chatBotInfo.npy", INFO)
        print("Logs made, length", len(LOG))

if __name__ == '__main__':
    #my_bot.run(open('token.txt','r').read().split('\n')[0], bot=False)
    main()