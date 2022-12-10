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
        diveColor = 0xffc800
        if self.type.startswith("Elite Deep Dive") :
            diveColor = 0xb82500
        out = discord.Embed(title = self.type, color = diveColor)
        for stage in self.stages:
            if stage[1].startswith("Primary") :
                continue
            stageContents = "**Objectives**: {primary_icon} {primary}** / **{secondary_icon} {secondary}\n**Anomaly**: {anomaly}\n**Warning**: {warning}".format(primary_icon=get_mission_icon(stage[1]), primary=stage[1], secondary_icon=get_mission_icon(stage[2]), secondary=stage[2], anomaly=stage[3], warning=stage[4])
            out.add_field(name="Stage {stg}".format(stg=stage[0]), value=stageContents, inline=False)
        return out
def get_mission_icon(input) :
    text = input.lower()
    if 'morkite' in text :
        return '<:mining:1050919827809783950>'
    if 'eggs' in text :
        return '<:alienegg:1050919736516558878>'
    if 'escort duty' in text :
        return '<:escort:1050919813242953769>'
    if 'aquarqs' in text :
        return '<:pointextraction:1050919841617416203>'
    if 'refinery' in text :
        return '<:refining:1050919894478245970>'
    if 'industrial sabotage' in text :
        return '<:sabotage:1050919908772417597>'
    if 'dreadnaught' in text or 'twins' in text or 'hiveguard' in text:
        return '<:elim:1050919798395129956>'
    if 'mini-mule' in text :
        return '<:salvage:1050919924081643630>'
    if 'black box' in text :
        return '<:blackbox:1050919626231521311>'
    return '<:gunner_two_oranges:1003106079007326338>'
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
    dd_mobile_cmd = ['!compact-dd', '!mobile-dd', '!cdd', '!sdd']
    if any(map(message.content.startswith, raw_cmd)):
        info = get_last_deep_dive_info(True)
        await message.channel.send(info)
        return
    if any(map(message.content.startswith, dd_cmd)):
        info = get_last_deep_dive_info()
        if info:
            await message.channel.send(info)
        return
    if any(map(message.content.startswith, dd_mobile_cmd)):
        info = get_last_deep_dive_info_embed()
        print('sending embed')
        await message.channel.send(info[0].name)
        for embed in info:
            await message.channel.send(embed = embed)
        return

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
