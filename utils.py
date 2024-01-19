from datetime import datetime, timedelta
import time
import pytz
import os
import aiohttp
from dotenv import load_dotenv
load_dotenv()


CLIST_API_KEY = os.environ.get("CLIST_API_KEY")
CLIST_API_USERNAME = os.environ.get("CLIST_API_USERNAME")
CLIST_HEADERS = {
    'Authorization': f'ApiKey {CLIST_API_USERNAME}:{CLIST_API_KEY}'
}


async def create_contests_message(contests_list={}):
    if not contests_list:
        contests_list = await contests_list()

    message = ""
    for contest in contests_list:
        message += f"""> ## __[{contest['name']}](<{contest['event_url']}>)__
> Starts <t:{contest['start_time_unix']}:R> (Cairo Time)
> Contest duration: {int(contest['duration']/(60*60)):02d}:{int(contest['duration']%(60*60)/60):02d}

"""
    return message


async def get_upcoming_contests(host="codeforces.com"):
    CLIST_CONTESTS_API = f"https://clist.by:443/api/v4/contest/?upcoming=true&order_by=start&host={host}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(CLIST_CONTESTS_API, headers=CLIST_HEADERS) as response:
            status_code = response.status
            contests_list = []

            if status_code == 200:
                contests = await response.json()
                for website in contests["objects"]:
                    start_time = datetime.fromisoformat(website["start"])
                    start_time = start_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Africa/Cairo"))
                    start_time_unix = int(time.mktime(start_time.timetuple()))
                    duration = website["duration"]
                    event_name = website["event"]
                    event_url = website["href"]
                    id = str(website["id"])
                    contests_list.append({
                        "start_time": start_time,
                        "start_time_unix": start_time_unix,
                        "duration": duration,
                        "name": event_name,
                        "event_url": event_url,
                        "id": id
                    })
                
                return contests_list

            else:
                raise Exception(f"Error fetching contests from clist.by API. Status code: {status_code}")


async def get_user_info(handle):
    CLIST_USER_API = f'https://clist.by:443/api/v4/account/?handle={handle}&order_by=-rating'

    async with aiohttp.ClientSession() as session:
        async with session.get(CLIST_USER_API, headers=CLIST_HEADERS) as response:
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