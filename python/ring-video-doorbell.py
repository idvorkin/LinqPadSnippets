#!uv run


# Ring Video Downloader.
#
# Ring is a subscription service, which only stores your videos for 90 days. This script will download all videos from ring into OneDrive
# so they will be saved for ever.

 # /// script
 # requires-python = ">=3.12"
 # dependencies = [
 #     "pendulum",
 #     "ring-doorbell",
 #     "schedule",
 #     "icecream",
 #     "pydantic"
 # ]
 # ///


import json
import os
import schedule
import time
import itertools
import pendulum
from pathlib import Path
from ring_doorbell import Ring, Auth, Requires2FAError
from ring_doorbell.exceptions import RingError
import sys
import pdb, traceback, sys
from icecream import ic
from typing import List
import asyncio

class RingDownloader:
    def __init__(self, username: str, password: str, app_name: str, cache_file: Path, base_path: Path):
        self.username = username
        self.password = password
        self.app_name = app_name
        self.cache_file = cache_file
        self.base_path = base_path

    async def _initialize_ring(self):
        """Initialize Ring authentication and device setup. Can be called again during retries."""
        self.auth = await self._setup_auth()
        self.ring = Ring(self.auth)
        await self.ring.async_update_data()
        self.doorbell = await self._get_doorbell()

    async def _setup_auth(self):
        if self.cache_file.is_file():
            return Auth(self.app_name, json.loads(self.cache_file.read_text()), self._token_updated)

        auth = Auth(self.app_name, None, self._token_updated)
        try:
            await auth.async_fetch_token(self.username, self.password)
        except Requires2FAError:
            await auth.async_fetch_token(self.username, self.password, self._otp_callback())
        return auth

    def _token_updated(self, token):
        self.cache_file.write_text(json.dumps(token))

    def _otp_callback(self):
        auth_code = input("2FA code: ")
        return auth_code

    async def _get_doorbell(self):
        devices = self.ring.devices()
        doorbells = devices["doorbots"]
        return doorbells[0]

    def make_directory_if_not_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    async def upload_ring_event(self, idx: int, ring_event: dict, total_events: int) -> None:
        recording_id = ring_event["id"]
        date = pendulum.instance(ring_event["created_at"]).in_tz("America/Vancouver")
        date_path_kind = f"{self.base_path}/{date.date()}/{ring_event['kind']}/"
        self.make_directory_if_not_exists(date_path_kind)
        date_path_kind_id = f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
        print(f"{idx}/{total_events}: {date_path_kind_id}")
        if not Path(date_path_kind_id).is_file():
            print("Downloading")
            max_retries = 4
            for attempt in range(max_retries):
                try:
                    await self.doorbell.async_recording_download(recording_id, date_path_kind_id)
                    break
                except RingError as exception:
                    is_404 = "404" in str(exception)
                    if is_404:
                        if attempt < max_retries - 1:  # Don't sleep on last attempt
                            seconds_to_sleep = 1.5
                            ic("404 Failure, waiting before retry", attempt, seconds_to_sleep)
                            await asyncio.sleep(seconds_to_sleep)
                        else:
                            raise exception
                    else:
                        ic({
                            'exception_type': type(exception).__name__,
                            'message': str(exception),
                            'attributes': {attr: getattr(exception, attr) for attr in dir(exception) if not attr.startswith('_')},
                        })
                        raise exception
        else:
            print("Already Present")

    async def get_all_events(self) -> List:
        events = []
        oldest_id = 0
        while True:
            tmp = await self.doorbell.async_history(older_than=oldest_id)
            if not tmp:
                break
            events.extend(tmp)
            oldest_id = tmp[-1]["id"]
        return events

    async def download_all(self) -> None:
        events = await self.get_all_events()
        total_events = len(events)
        ic(total_events)
        # Download in reverse order to make sure we get the old events
        # before they are expired
        for idx, event in enumerate(reversed(events)):
            await self.upload_ring_event(idx, event, total_events)

    async def print_timestamp_and_download(self) -> None:
        for retry in range(1000):
            try:
                print(f"Downloading @ {pendulum.now()}")
                await self.download_all()
                print(f"Done @ {pendulum.now()}")
                return
            except:
                ic(sys.exc_info()[0])
                seconds = 1
                print(f"sleeping {seconds} seconds before retry: {retry}")
                await asyncio.sleep(seconds)
                await self._initialize_ring()

async def main() -> None:
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

    await downloader._initialize_ring()
    nightly_execution_time = "02:00"
    print(f"Download scheduled every day @ {nightly_execution_time}")
    await downloader.print_timestamp_and_download()

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
