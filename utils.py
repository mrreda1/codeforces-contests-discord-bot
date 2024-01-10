from datetime import datetime
from time import time
import requests
import hashlib
import random
import os
import aiohttp
from dotenv import load_dotenv
load_dotenv()


def contests_list():
    """ To get your API-key visit codeforces.com/settings/api
    Then click on 'Add API key' then pass your key and secret
    For more info about API visit codeforces.com/apiHelp ."""

    apiKey = os.environ.get("CODEFORCES_API_KEY")
    secret = os.environ.get("CODEFORCES_API_SECRET")
    crnt_time = int(time())
    methodName = "contest.list"
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
            remain = -contest["relativeTimeSeconds"]
            duration = contest["durationSeconds"]
            start_date = datetime.fromtimestamp(contest["startTimeSeconds"])
            start_date = start_date.strftime("%A, %B %d, %I:%M")
            results += f"\n> ## __[{contest['name']}](<https://codeforces.com/contests/{contest['id']}>)__ \n"\
                f"> Starts at: {start_date}\n> Time Remaining: "\
                f"{int(remain/(60*60*24)):02d} day(s), "\
                f"{int(remain%(60*60*24)/(60*60)):02d}:"\
                f"{int(remain%(60*60)/60):02d}\n"\
                f"> Contest duration: {int(duration/(60*60)):02d}:"\
                f"{int(duration%(60*60)/60):02d}\n"
    return results

async def user_info(handle):
    CLIST_API_KEY = os.environ.get("CLIST_API_KEY")
    CLIST_API_USERNAME = os.environ.get("CLIST_API_USERNAME")
    CLIST_API_URL = f'https://clist.by:443/api/v4/account/?handle={handle}&order_by=-rating'

    clist_headers = {
        'Authorization': f'ApiKey {CLIST_API_USERNAME}:{CLIST_API_KEY}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(CLIST_API_URL, headers=clist_headers) as response:
            status_code = response.status

            if status_code == 200:
                stats = {}
                user_info = await response.json()
                for website in user_info["objects"]:
                    webiste_name = website["resource"]
                    rating = website["rating"]
                    if rating:
                        stats[webiste_name] = rating
                
                return stats
            else:
                raise Exception(f"Error fetching user info for {handle} from clist.by API. Status code: {status_code}")