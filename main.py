# -*- coding: utf-8 -*-
import discord
import os
import unicodedata
import time
import praw
from tabulate import tabulate
from urllib3 import Retry

from random_drg import Build, is_valid_class


from dotenv import load_dotenv
load_dotenv()

class DeepDive:
    def __init__(self, type, name, biome):
        self.type = type
        self.name = name
        self.biome = biome
        self.stages = []
    
    def add_stage(self, stage, primary, secondary, anomaly, warning):
        self.stages.append([stage, primary, secondary, anomaly, warning])
    
    def to_beautiful_string(self):
        out = f'**{self.type}**\n```\n'
        out += tabulate(self.stages, headers=["Stage", "Primary", "Secondary", "Anomaly", "Warning"], tablefmt="fancy_grid")
        out += '```'
        return out
    def to_beautiful_embed(self):
        out = discord.Embed(title = self.type, description = DeepDive.to_beautiful_string(self))
        return out

def parse_deep_dive_info(text, type):
    dd = None
    for line in text.split('\n'):
        line = line.replace('*', '')
        sline = [x.strip() for x in line.split('|')]
        if len(sline) > 2 and sline[0] == type:
            dd = DeepDive(type, sline[1], sline[2])
        if dd and len(sline) >= 6 and sline[0] == '':
            [stage, primary, secondary, anomaly, warning] = sline[1:6]
            # ignore header
            if stage == 'Stage' or stage == ':-':
                continue
            dd.add_stage(stage, primary, secondary, anomaly, warning)
            if stage == '3':
                break
    return dd

reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_SECRET'],
    user_agent="my user agent",
    check_for_async=False
)
subreddit = reddit.subreddit("DeepRockGalactic")

def get_last_deep_dive_submission():
    for submission in subreddit.hot(limit=5):
        if "Weekly Deep Dives Thread" in submission.title:
            return submission
    print('No deep dive submission found')
    return None

def get_last_deep_dive_info(raw=False):
    submission = get_last_deep_dive_submission()
    if not submission:
        return None
    text = submission.selftext
    if raw:
        return text
    
    dd = parse_deep_dive_info(text, 'Deep Dive')
    edd = parse_deep_dive_info(text, 'Elite Deep Dive')

    if not dd or not edd:
        print('No deep dive (or elite deep dive) info found')
        return None

    url = f'**Source**: <{submission.url}>'
    title = f'**{submission.title}**'

    result = '\n'.join([title,
                      '',
                      dd.to_beautiful_string(),
                      edd.to_beautiful_string(),
                      url])
    print(f"Result len: {len(result)}")
    
    return result

def get_last_deep_dive_info_embed(raw=False):
    submission = get_last_deep_dive_submission()
    if not submission:
        return None
    text = submission.selftext
    if raw:
        return text
    
    dd = parse_deep_dive_info(text, 'Deep Dive')
    edd = parse_deep_dive_info(text, 'Elite Deep Dive')

    if not dd or not edd:
        print('No deep dive (or elite deep dive) info found')
        return None

    url = f'**Source**: <{submission.url}>'
    title = f'**{submission.title}**'

    result = [dd.to_beautiful_embed(), edd.to_beautiful_embed()]

    return result

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

todolist = "- Do the disc quest, steal plane-attuned forks and upper/lower plane symbols from Eronan"
longertermgoals = "Save violet, PR campaign, secure funding, assassinate duke/dealer, CJ drug intervention, talk with Mrs. Boudua for a political ally, teach Tyrell morals"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    #print('received message:')
    #print(message.content)
    if message.author == client.user:
        return

    raw_cmd = ['!deep-dive-raw']
    dd_cmd = ['!deep-dive', '!deepdive', '!dd']
    if any(map(message.content.startswith, raw_cmd)):
        info = get_last_deep_dive_info(True)
        await message.channel.send(info)
        return
    if any(map(message.content.startswith, dd_cmd)):
        info = get_last_deep_dive_info()
        if info:
            await message.channel.send(info)
        return
    if (message.content.startsWith('!dd-embed')):
        info = get_last_deep_dive_info_embed()
        for embed in info:
            await client.send(embed)

    if (message.content.startswith('!rand')):
        splitted_message = message.content.split(' ')
        klass = splitted_message[1].lower() if len(splitted_message) > 1 else None
        if is_valid_class(klass):
            build = Build(klass)
            await message.channel.send(str(build))
        else:
            await message.channel.send(f'Invalid class {klass}. Valid classes are Engineer, Gunner, Driller or Scout. Leave empty for random.')
        return

    if message.content.startswith('!stupid'):
        await message.channel.send('Remember not to do anything stupid! 😃')
    if message.content.startswith('!schedule'):
        print('doing schedule')
        c = message.channel
        vote = '<@&692777373543956561> Initializing forced voting process...done in 0.56 ms. Begin remote transmission from orb with ORB_NAME: Phobos.'
        vote += ' It\'s voting time! \n Monday Evening ♠️\nTuesday Evening ♥️\n Wednesday Evening ♦️\nThursday Evening♣️ \nFriday Evening 🃏 \nSaturday 10am-2pm 🟨 \nSaturday 12-4pm🟩'
        vote += '\nSaturday 4pm-8pm 🟦 \nSaturday 6-10pm 🟪 \nSaturday 8pm-12 🔴 \nSunday 10am-2pm 🟠 \nSunday 12-4pm🟡'
        vote += '\nSunday 4pm-8pm 🟢 \nSunday 6-10pm 🔵 \nSunday 8pm-12 🟣 \nNot this week 🏳️'
        m = await c.send(vote)
        emoteList = ['\N{Black Spade Suit}','\N{Black Heart Suit}','\N{Black Diamond Suit}','\N{Black Club Suit}','\N{Playing Card Black Joker}','\N{Large Yellow Square}','\N{Large Green Square}','\N{Large Blue Square}','\N{Large Purple Square}','\N{Large Red Circle}', '\N{Large Orange Circle}', '\N{Large Yellow Circle}','\N{Large Green Circle}', '\N{Large Blue Circle}', '\N{Large Purple Circle}','\N{Waving White Flag}']

        for reaction in emoteList:
            print('adding reaction')
            await m.add_reaction(reaction)
            time.sleep()
        await c.send('Remember not to do anything stupid! 😃')
        await c.send('TODOS: ' + todolist)
        await c.send('LONG-TERM GOALS: ' + longertermgoals)
    if message.content.startswith('!todo'):
        await message.channel.send('TODOS: ' + todolist)
        await message.channel.send('LONG-TERM GOALS: ' + longertermgoals)

    


client.run(os.environ['TOKEN'])
