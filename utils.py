from discord import Embed
import hashlib
import os
import json
import random
from datetime import datetime
from time import time

import requests
from dotenv import load_dotenv

load_dotenv()


def get_user(handle: str):
    link = "https://codeforces.com/api/user.info?handles="
    target = link + handle

    try:
        data = requests.get(target).json()
    except Exception:
        return None

    if (data["status"] == "OK"):
        return data["result"][0]

    return None


def makeUserEmbed(user):
    rankcolor = ""
    colors = {"newbie": 0x808080, "legendary grandmaster": 0xFF0000,
              "pupil": 0x028000, "international grandmaster": 0xFF0000,
              "expert": 0x0000FF, "candidate master": 0xAA00AA,
              "master": 0xFF8C00, "international master": 0xFF8C00,
              "grandmaster": 0xFF0000, "specialist": 0x03A89E}

    try:
        CR = f":bar_chart: **Contest rating**: {user['rating']} \
        (max, {user['maxRank']}, {user['maxRating']})ㅤ"
        rankcolor = colors.get(user['rank'])
    except Exception:
        CR = ":bar_chart: **Contest rating**: 0ㅤㅤㅤ"
        rankcolor = 0

    CNT = f":star2: **Contribution**: {user['contribution']}"
    FRND = f":star: **Friend of**: {user['friendOfCount']}"
    embed = Embed(
        title=user["handle"] + "\n\n",
        url="https://codeforces.com/profile/" + user["handle"],
        description=f"ㅤ\n{CR}\n\n{CNT}\n\n{FRND}",
        color=rankcolor
    )
    try:
        embed.set_author(name=user['rank'].title())
    except Exception:
        embed.set_author(name="Unrated")

    embed.set_thumbnail(url=user["titlePhoto"])
    return embed




def synchandle(id, handle):
    path = "./data.json"
    data = dict()
    user = get_user(handle)
    if (not user):
        return None

    if os.path.isfile(path):
        with open(path, 'r') as f:
            if len(f.readlines()) != 0:
                f.seek(0)
                data = json.load(f)

    data[id] = user['handle']
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        # f.write(json.dumps(data))

    return user['handle']


def gethandle(id):
    path = "./data.json"
    data = dict()
    try:
        with open(path, 'r') as f:
            data = json.load(f)
    except Exception:
        return None
    return data.get(id)


def contests_list():
    """ To get your API-key visit codeforces.com/settings/api
    Then click on 'Add API key' then pass your key and secret
    For more info about API visit codeforces.com/apiHelp ."""

    apiKey = os.environ.get("CODEFORCES_API_KEY")
    secret = os.environ.get("CODEFORCES_API_SECRET")
    crnt_time = int(time())
    methodName = "contest.list"
    timezone = +2
    rand = random.randint(100000, 999999)
    encrypt = "{}/{}?apiKey={}&time={}#{}".format(
        rand, methodName, apiKey, crnt_time, secret)
    hash = hashlib.sha512(encrypt.encode('UTF-8')).hexdigest()
    apiSig = "{}{}".format(rand, hash)
    args = "apiKey={}&time={}&apiSig={}".format(apiKey, crnt_time, apiSig)
    target = "https://codeforces.com/api/{}?{}".format(methodName, args)
    data = requests.get(target).json()
    if (data["status"] == "FAILED"):
        print(f"\033[4mRequest failed...\033[0m\n{data['comment']}")
        return
    results = ''
    for contest in data['result']:
        if (contest["phase"] == "BEFORE"):
            remain = -contest["relativeTimeSeconds"] + timezone*60*60
            duration = contest["durationSeconds"]
            startTimeSeconds = contest["startTimeSeconds"] + timezone*60*60
            start_date = datetime.fromtimestamp(startTimeSeconds)
            start_date = start_date.strftime("%A, %B %d, %I:%M")
            results += f"\n> ## __[{contest['name']}](<https://codeforces.com"\
                f"/contests/{contest['id']}>)__ \n"\
                f"> Starts at: {start_date}\n> Time Remaining: "\
                f"{int(remain/(60*60*24)):02d} day(s), "\
                f"{int(remain%(60*60*24)/(60*60)):02d}:"\
                f"{int(remain%(60*60)/60):02d}\n"\
                f"> Contest duration: {int(duration/(60*60)):02d}:"\
                f"{int(duration%(60*60)/60):02d}\n"
    return results
