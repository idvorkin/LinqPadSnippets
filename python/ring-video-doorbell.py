# Ring Video Downloader.
#
# Ring is a subscription service, which only stores your videos for 90 days. This script will download all videos from ring into OneDrive 
# so they will be saved for ever.

from ring_doorbell import Ring
import json
import pendulum
import os
from pathlib import Path
import schedule
import time

PASSWORD = "replaced_from_secret_box"
with open('/gits/igor2/secretBox.json') as json_data:
    SECRETS = json.load(json_data)
    PASSWORD = SECRETS["RingAccountPassword"]

ring = Ring('idvorkin@gmail.com', PASSWORD)

def downloadAll():
    print(f"Connected Success:{ring.is_connected}")
    doorbell = ring.doorbells[0]

    library_limits_to_100 = 100
    es = [e for e in doorbell.history(limit=library_limits_to_100)]


    # create base path
    def make_directory_if_not_exists(path):
        if not os.path.exists(path):
            os.makedirs(path)


    # Only works on basement computer for onedrive make better
    path_base = "/users/idvor/onedrive/ring/date/"

    for e in es:
        recording_id = e['id']
        date = pendulum.instance(e["created_at"]).in_tz("America/Vancouver")
        date_path_kind = f"{path_base}{date.date()}/{e['kind']}/"
        make_directory_if_not_exists(date_path_kind)
        date_path_kind_id = f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
        print(date_path_kind_id)
        if not Path(date_path_kind_id).is_file():
            # download write file.
            print("Downloading")
            doorbell.recording_download(recording_id, date_path_kind_id)
        else:
            print("Already Present")


def printTimeStampAndDownload():
    print (f"Downloading @ {pendulum.now()}")
    downloadAll()
    print (f"Done @ {pendulum.now()}")

nightlyExecutionTime = "2:00"
print(f"Download scheduled every day @ {nightlyExecutionTime}")
schedule.every().day.at(nightlyExecutionTime).do(printTimeStampAndDownload)
printTimeStampAndDownload()
while True:
    schedule.run_pending()
