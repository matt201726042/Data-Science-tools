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

global INFO,LOG,READY
ASYNCCOUNT = 0
READY = False

try:
    LOG = np.load("chatBotLog.npy", allow_pickle=True).tolist()
except:
    LOG = np.array({})
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

def reptWeighter(msg, model, dictionary, rLOG):
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
            out += reptWProfInterp(delta) * (lda.LDAquery(model, dictionary, [msg["content"], rLOG[i]["content"]])) #levenshtein.levenshtein(msg["content"], rLOG[i]["content"])
    return out

imitate = 309724935495090178

def main():
    print("Python script started.")
    try:
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(location, 'token.txt'), 'r')
        my_bot.run(f.read().split('\n')[0], bot=True)
    except discord.errors.LoginFailure as e:
        print(e, 'Try adding the `--bot` flag.')

def logNewMessage(message):
    if message.content not in ['', '~'] and READY:
        at = ",".join([i.url for i in message.attachments])
        if len(at) > 0:
            at = " " + at
        messageContent = message.content
        if message.content[0] == "~":
            messageContent = message.content[1:]
        mes = {"author":message.author.id, "time":message.created_at, "content":messageContent + at}
        try:
            LOG[message.channel.id].append(mes)
        except:
            LOG[message.channel.id] = []
        np.save("chatBotLog.npy", LOG)
        try:
            INFO["counts"][message.author.id] += 1
        except:
            INFO["counts"][message.author.id] = 0
        #LDAMODEL.update([mes["content"]])
        print("LOGGED (" + str(len(LOG[message.channel.id])) + ")", message.channel.name, ":", message.created_at, ":", message.author.name, ":", mes["content"])

@my_bot.event
async def on_message(message):
    global ASYNCCOUNT
    if message.author.id != 826150125206110208 and len(message.content) > 0:
        if message.channel.name == "general" or "dorime" in message.channel.name or message.content[0] == "~":
            logNewMessage(message)
        
        if ("dorime" in message.channel.name or message.content[0] == "~" or message.author.id == 569277281046888488) and ASYNCCOUNT < 3 and READY:
            ASYNCCOUNT += 1
            myreplyobj = await message.reply("0%", mention_author=False)
            try:
                realContext = LOG[message.channel.id][-contextLen:]
                y = []
                LOGlen = len(LOG[message.channel.id]) - 1
                LOGcap = 750
                ratio = LOGcap/INFO["counts"][message.channel.id][message.author.id]
                if ratio > 1:
                    ratio = 1
                compress = random.choices([True, False], weights=[1-ratio, ratio], k=LOGlen)
                for i in range(LOGlen):
                    msg = LOG[message.channel.id][i+1]
                    if msg["author"] == imitate and not compress[i]:
                        if i % 100 == 0:
                            await myreplyobj.edit(content=str(np.round(100 * (i/LOGlen), 2)) + "%")
                            print(100 * (i/LOGlen), "%")
                        if i < contextLen:
                            start = 0
                        else:
                            start = (i+1) - contextLen
                        cLen = (i+1)-start
                        context = LOG[message.channel.id][start:i+1]
                        sims = []
                        weights = []
                        rLOG = LOG[message.channel.id][::-1]
                        rW = reptWeighter(msg, LDAMODEL[message.channel.id], LDADICT[message.channel.id], rLOG)
                        authorChecks = []
                        for c in range(cLen):
                            sims.append(lda.LDAquery(LDAMODEL[message.channel.id], LDADICT[message.channel.id], [realContext[c]["content"], context[c]["content"]]))
                            weights.append(contextWProfInterp(cLen-c))
                            if realContext[c]["author"] == context[c]["author"]:
                                authorChecks.append(0.5)
                            else:
                                authorChecks.append(0)
                        y.append(((np.average(sims, weights=weights) + np.average(authorChecks, weights=weights)) / rW, msg))
                a = sorted(y, key=lambda x: x[0])[::-1]
                out = None
                for i in range(len(a)):
                    if a[i][1]["author"] == imitate and len(a[i][1]["content"]) > 0:
                        out = a[i]
                        break
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
                await myreplyobj.delete()
                print("Exception in trying to respond:", e)
                print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            ASYNCCOUNT -= 1

@my_bot.event
async def on_ready():
    print("Bot logged in.")
    print("-------------------------------------------------")
    await make_logs()
    print("-------------------------------------------------")
    await make_model()
    print("-------------------------------------------------")
    READY = True
    #await my_bot.logout()
    
async def make_model():
    global LDAMODEL, LDADICT
    LDAMODEL = {}
    LDADICT = {}
    for id,messages in LOG.items():
        print("Making the model for channel", id)
        try:
            LDAMODEL[id], LDADICT[id] = lda.LDAtrain([msg["content"] for msg in messages])
        except:
            print("I can't make the model for channel", id)
        print("Model made.")
    print("Training complete.")

async def make_logs():
    prevLog = INFO["lastLog"]
    print("The last log was", prevLog)
    print("INFO:", INFO)
    print("Do you want to log any channels? y/n")
    shallIContinue = input("")
    if shallIContinue == "y":
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
                            LOG[channel.id] = []
                            async for message in channel.history(limit=None,after=prevLog):
                                try:
                                    i += 1
                                    if i % 100 == 0:
                                        print("count:", i)
                                    if message.content not in ['', '~']:
                                        at = ",".join([i.url for i in message.attachments])
                                        if len(at) > 0:
                                            at = " " + at
                                        messageContent = message.content
                                        if message.content[0] == "~":
                                            messageContent = message.content[1:]
                                        msg = {"author":message.author.id, "time":message.created_at, "content":messageContent + at}
                                        LOG[channel.id].append(msg)
                                        if message.channel.id not in INFO["counts"].keys():
                                            INFO["counts"][message.channel.id] = {}
                                        if message.author.id not in INFO["counts"][message.channel.id].keys():
                                            INFO["counts"][message.channel.id][message.author.id] = 0
                                        else:
                                            INFO["counts"][message.channel.id][message.author.id] += 1
                                    #print((channel.id), (message.author.id, message.created_at, message.content + " " + at))
                                except Exception as e:
                                    print(e)
                            if i != 0:
                                INFO["lastLog"] = datetime.datetime.now()
                            print("\rLogging {0}: [DONE]            ".format(channel.name))
                            #print(LOG)
                            np.save("chatBotLog.npy", LOG)
                            np.save("chatBotInfo.npy", INFO)
                            print("Channel length:", len(LOG[channel.id]))
    print("Channel count:", len(LOG))

if __name__ == '__main__':
    #my_bot.run(open('token.txt','r').read().split('\n')[0], bot=False)
    main()