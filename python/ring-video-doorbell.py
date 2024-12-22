#!python3


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
from ring_doorbell import Ring, Auth, Requires2FAError
from ring_doorbell.exceptions import RingError
import time
import sys
import pdb, traceback, sys
from icecream import ic
import urllib
import requests
import time
from typing import List

class RingDownloader:
    def __init__(self, username: str, password: str, app_name: str, cache_file: Path, base_path: Path):
        self.username = username
        self.password = password
        self.app_name = app_name
        self.cache_file = cache_file
        self.base_path = base_path
        self._initialize_ring()

    def _initialize_ring(self):
        """Initialize Ring authentication and device setup. Can be called again during retries."""
        self.auth = self._setup_auth()
        self.ring = Ring(self.auth)
        self.ring.update_data()
        self.doorbell = self._get_doorbell()

    def _setup_auth(self):
        if self.cache_file.is_file():
            return Auth(self.app_name, json.loads(self.cache_file.read_text()), self._token_updated)
        
        auth = Auth(self.app_name, None, self._token_updated)
        try:
            auth.fetch_token(self.username, self.password)
        except Requires2FAError:
            auth.fetch_token(self.username, self.password, self._otp_callback())
        return auth

    def _token_updated(self, token):
        self.cache_file.write_text(json.dumps(token))

    def _otp_callback(self):
        auth_code = input("2FA code: ")
        return auth_code

    def _get_doorbell(self):
        devices = self.ring.devices()
        doorbells = devices["doorbots"]
        return doorbells[0]

    # Create base path
    def make_directory_if_not_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    # Only works on basement computer for onedrive make better
    PATH_BASE = Path.home()/"onedrive/ring/date/"

    def upload_ring_event(self, idx: int, ring_event: dict, total_events: int) -> None:
        recording_id = ring_event["id"]
        date = pendulum.instance(ring_event["created_at"]).in_tz("America/Vancouver")
        date_path_kind = f"{self.base_path}/{date.date()}/{ring_event['kind']}/"
        self.make_directory_if_not_exists(date_path_kind)
        date_path_kind_id = f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
        print(f"{idx}/{total_events}: {date_path_kind_id}")
        if not Path(date_path_kind_id).is_file():
            print("Downloading")
            try:
                self.doorbell.recording_download(recording_id, date_path_kind_id)
            except RingError as exception:
                is_404 = "404" in str(exception)
                if is_404:
                    # Skip on 404
                    seconds_to_sleep = 30
                    ic("404 Failure, waiting seconds inc ase I'm in timeout",seconds_to_sleep)
                    ic(exception)

                    time.sleep(seconds_to_sleep)
                    # I think the issue is some cahced token is stale - re throw
                    raise exception
                else:
                    # Print all exception attributes
                    ic({
                        'exception_type': type(exception).__name__,
                        'message': str(exception),
                        'attributes': {attr: getattr(exception, attr) for attr in dir(exception) if not attr.startswith('_')},
                    })

        else:
            print("Already Present")

    def get_all_events(self) -> List:
        events = []
        oldest_id = 0
        while True:
            tmp = self.doorbell.history(older_than=oldest_id)
            if not tmp:
                break
            events.extend(tmp)
            oldest_id = tmp[-1]["id"]
        return events

    def download_all(self) -> None:
        events = self.get_all_events()
        total_events = len(events)
        ic(total_events)
        for idx, event in enumerate(reversed(events)):
            self.upload_ring_event(idx, event, total_events)

    def print_timestamp_and_download(self) -> None:
        for retry in range(5):
            try:
                print(f"Downloading @ {pendulum.now()}")
                self.download_all()
                print(f"Done @ {pendulum.now()}")
                return
            except:
                ic(sys.exc_info()[0])
                traceback.print_exc()
                seconds = 10
                print(f"sleeping {seconds} seconds before retry: {retry}")
                time.sleep(seconds)
                # Re-initialize Ring connection before next retry
                self._initialize_ring()

def main() -> None:
    # Load secrets
    with open(Path.home()/"gits/igor2/secretBox.json") as json_data:
        secrets = json.load(json_data)
        password = secrets["RingAccountPassword"]

    downloader = RingDownloader(
        username="idvorkin@gmail.com",
        password=password,
        app_name="PleaseForTheLoveOfferAnOfficialAPI/1.0",
        cache_file=Path("test_token.cache"),
        base_path=Path.home()/"onedrive/ring/date/"
    )

    nightly_execution_time = "02:00"
    print(f"Download scheduled every day @ {nightly_execution_time}")
    schedule.every().day.at(nightly_execution_time).do(downloader.print_timestamp_and_download)
    downloader.print_timestamp_and_download()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

main()
