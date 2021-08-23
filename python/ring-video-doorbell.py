# Ring Video Downloader.
#
# Ring is a subscription service, which only stores your videos for 90 days. This script will download all videos from ring into OneDrive
# so they will be saved for ever.

import json
import os
import schedule
import time
import itertools
import pendulum
from pathlib import Path
from ring_doorbell import Ring, Auth
import time
import sys
import pdb, traceback, sys
from icecream import ic
import urllib
import requests
import time
from typing import List

PASSWORD = "replaced_from_secret_box"
with open("/gits/igor2/secretBox.json") as json_data:
# with open("/home/ec2-user/gits/igor2/secretBox.json") as json_data:
    SECRETS = json.load(json_data)
    PASSWORD = SECRETS["RingAccountPassword"]

from pprint import pprint
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError

cache_file = Path("test_token.cache")


def token_updated(token):
    cache_file.write_text(json.dumps(token))


def otp_callback():
    auth_code = input("2FA code: ")
    return auth_code


auth = None
app_name = "PleaseForTheLoveOfferAnOfficialAPI/1.0"
if cache_file.is_file():
    auth = Auth(app_name, json.loads(cache_file.read_text()), token_updated)
else:
    username = "idvorkin@gmail.com"
    password = PASSWORD
    auth = Auth(app_name, None, token_updated)
    try:
        auth.fetch_token(username, password)
    except MissingTokenError:
        auth.fetch_token(username, password, otp_callback())

ring = Ring(auth)
ring.update_data()
devices = ring.devices()
pprint(devices)
doorbells = devices["doorbots"]
doorbell = doorbells[0]


# Create base path
def make_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Only works on basement computer for onedrive make better
PATH_BASE = "/users/idvor/onedrive/ring/date/"


def upload_ring_event(idx, ring_event) -> None:
    recording_id = ring_event["id"]
    date = pendulum.instance(ring_event["created_at"]).in_tz("America/Vancouver")
    date_path_kind = f"{PATH_BASE}{date.date()}/{ring_event['kind']}/"
    make_directory_if_not_exists(date_path_kind)
    date_path_kind_id = f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
    print(f"{idx}: {date_path_kind_id}")
    if not Path(date_path_kind_id).is_file():
        print("Downloading")
        try:
            doorbell.recording_download(recording_id, date_path_kind_id)
        # except urllib.error.HTTPError as exception:
        except requests.exceptions.HTTPError as exception:
            # Skip on 404
            ic("Failure, skipping")
            ic(exception)
            time.sleep(1)
            return


    else:
        print("Already Present")


def getAllEvents() -> List:
    events = []
    oldest_id = 0
    while True:
        tmp = doorbell.history(older_than=oldest_id)
        if not tmp:
            break
        events.extend(tmp)
        oldest_id = tmp[-1]["id"] # last element's id
    return events


def downloadAll() -> None:
    events = getAllEvents()
    ic (len(events))
    for idx,event in enumerate(reversed(events)):
        upload_ring_event(idx, event)
        # ic(event)
        # time.sleep(1)


def printTimeStampAndDownload() -> None:
    for retry in range(5):
        try:
            print(f"Downloading @ {pendulum.now()}")
            downloadAll()
            print(f"Done @ {pendulum.now()}")
            return
        except:
            ic(sys.exc_info()[0])
            traceback.print_exc()
            seconds = 10
            print(f"sleeping {seconds} seconds before retry: {retry}")
            time.sleep(seconds)


def main() -> None:
    nightly_execution_tame = "02:00"
    print(f"Download scheduled every day @ {nightly_execution_tame}")
    schedule.every().day.at(nightly_execution_tame).do(printTimeStampAndDownload)
    printTimeStampAndDownload()
    while True:
        schedule.run_pending()
        time.sleep(1)


main()
