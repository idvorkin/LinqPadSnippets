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

PASSWORD = "replaced_from_secret_box"
with open("/gits/igor2/secretBox.json") as json_data:
    SECRETS = json.load(json_data)
    PASSWORD = SECRETS["RingAccountPassword"]

from ring_doorbell import Ring, Auth

auth = Auth(None)
username = "idvorkin@gmail.com"
auth.fetch_token(username, PASSWORD)

ring = Ring(auth)
doorbell = ring.doorbells[0]


# Create base path
def make_directory_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Only works on basement computer for onedrive make better
PATH_BASE = "/users/idvor/onedrive/ring/date/"


def upload_ring_event(idx, ring_event) -> None:
    recording_id = ring_event["id"]
    date = pendulum.instance(
        ring_event["created_at"]).in_tz("America/Vancouver")
    date_path_kind = f"{PATH_BASE}{date.date()}/{ring_event['kind']}/"
    make_directory_if_not_exists(date_path_kind)
    date_path_kind_id = f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
    print(f"{idx}: {date_path_kind_id}")
    if not Path(date_path_kind_id).is_file():
        print("Downloading")
        doorbell.recording_download(recording_id, date_path_kind_id)
    else:
        print("Already Present")


def downloadAll() -> None:
    oldest_id, idx = None, 0
    while True:
        print(f"Downloading in history {idx}, older_then={oldest_id}")
        events = doorbell.history(older_than=oldest_id)
        for event in events:
            upload_ring_event(idx, event)
            oldest_id = event["id"]
            idx = idx + 1
        if not events:
            break


def printTimeStampAndDownload() -> None:
    for retry in range(5):
        try:
            print(f"Downloading @ {pendulum.now()}")
            downloadAll()
            print(f"Done @ {pendulum.now()}")
            return
        except:
            print(f"exception: \n {sys.exc_info()[0]}\n")
            traceback.print_exc()
            seconds = 10
            print(f"sleeping {seconds} seconds before retry: {retry}")
            time.sleep(seconds)


def main() -> None:
    nightly_execution_tame = "02:00"
    print(f"Download scheduled every day @ {nightly_execution_tame}")
    schedule.every().day.at(nightly_execution_tame).do(
        printTimeStampAndDownload)
    printTimeStampAndDownload()
    while True:
        schedule.run_pending()
        time.sleep(1)


main()
