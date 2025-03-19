#!uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pendulum",
#     "ring-doorbell",
#     "schedule",
#     "icecream",
#     "pydantic",
#     "tenacity"
# ]
# ///

# Ring Video Downloader.
#
# Ring is a subscription service, which only stores your videos for 90 days. This script will download all videos from ring into OneDrive
# so they will be saved for ever.


import json
import os
import schedule
import pendulum
from pathlib import Path
from ring_doorbell import Ring, Auth, Requires2FAError
from ring_doorbell.exceptions import RingError
from icecream import ic
from typing import List, Dict, Any, TypeVar
import asyncio
from pydantic import BaseModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryCallState,
)
import logging
import time
import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def custom_before_sleep_callback(retry_state):
    """Custom before_sleep callback that logs detailed timing information and ensures sleep."""
    exception = retry_state.outcome.exception()
    if exception:
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        sleep_time = retry_state.next_action.sleep
        
        print(f"[{now}] Retry {retry_state.attempt_number}/{retry_state.retry_object.stop.max_attempt_number} - SLEEPING for {sleep_time:.2f}s due to: {type(exception).__name__}: {str(exception)}")
        
        # Log the expected wake-up time
        wake_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] Expected wake-up time: {wake_time}")
        
        # For certain errors, reinitialize the connection
        if isinstance(exception, RingError) and "401" in str(exception):
            print(f"[{now}] Unauthorized error detected, reinitializing Ring connection")
        elif isinstance(exception, RingError) and "404" in str(exception):
            print(f"[{now}] Transient 404 error detected, will retry after sleep")

def retry_ring_or_404(exception):
    """Retry if exception is RingError or contains '404' in the error message."""
    if isinstance(exception, RingError):
        # Always retry for 404 errors as they are transient
        if "404" in str(exception):
            logger.info("Retrying due to 404 error")
            return True
        # Otherwise, retry for any RingError
        return True
    return False

T = TypeVar("T")


class RetryConfig(BaseModel):
    max_attempts: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retry_on_exceptions: List[type] = [RingError]
    retry_on_status_codes: List[str] = ["404"]
    skip_after_max_attempts: bool = (
        False  # New flag to determine if we should skip or raise after max attempts
    )


class RingDownloader:
    def __init__(
        self,
        username: str,
        password: str,
        app_name: str,
        cache_file: Path,
        base_path: Path,
    ):
        self.username = username
        self.password = password
        self.app_name = app_name
        self.cache_file = cache_file
        self.base_path = base_path


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type(RingError),
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    async def _initialize_ring(self):
        """Initialize Ring authentication and device setup. Can be called again during retries."""
        self.auth = await self._setup_auth()
        self.ring = Ring(self.auth)
        await self.ring.async_update_data()
        self.doorbell = await self._get_doorbell()

    async def _setup_auth(self):
        if self.cache_file.is_file():
            return Auth(
                self.app_name,
                json.loads(self.cache_file.read_text()),
                self._token_updated,
            )

        auth = Auth(self.app_name, None, self._token_updated)
        try:
            await auth.async_fetch_token(self.username, self.password)
        except Requires2FAError:
            await auth.async_fetch_token(
                self.username, self.password, self._otp_callback()
            )
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

    @retry(
        stop=stop_after_attempt(6),  # Increase max attempts
        wait=wait_exponential(multiplier=2.0, max=120.0, exp_base=2),  # Longer waits
        retry=retry_ring_or_404,
        before_sleep=custom_before_sleep_callback,
        reraise=True,  # Changed to True to ensure exceptions are properly propagated
    )
    async def upload_ring_event(
        self, idx: int, ring_event: dict, total_events: int
    ) -> None:
        recording_id = ring_event["id"]
        date = pendulum.instance(ring_event["created_at"]).in_tz("America/Vancouver")
        date_path_kind = f"{self.base_path}/{date.date()}/{ring_event['kind']}/"
        self.make_directory_if_not_exists(date_path_kind)
        date_path_kind_id = (
            f"{date_path_kind}{date.hour}-{date.minute}-{recording_id}.mp4"
        )
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] {idx}/{total_events}: {date_path_kind_id}")
        if not Path(date_path_kind_id).is_file():
            print(f"[{now}] Downloading")
            # Let the retry decorator handle exceptions
            await self.doorbell.async_recording_download(
                recording_id, date_path_kind_id
            )
        else:
            print(f"[{now}] Already Present")

    @retry(
        stop=stop_after_attempt(6),  # Increase max attempts
        wait=wait_exponential(multiplier=2.0, max=120.0, exp_base=2),  # Longer waits
        retry=retry_ring_or_404,
        before_sleep=custom_before_sleep_callback,
        reraise=True,  # Changed to True to ensure exceptions are properly propagated
    )
    async def get_history_batch(self, oldest_id: int = 0) -> List[Dict[str, Any]]:
        """Get a batch of history events with proper retry handling"""
        return await self.doorbell.async_history(older_than=oldest_id)
        
    async def get_all_events(self) -> List[Dict[str, Any]]:
        """Collect all events using the retryable history batch function"""
        events = []
        oldest_id = 0
        
        while True:
            tmp = await self.get_history_batch(oldest_id)
            if not tmp:
                break
            events.extend(tmp)
            oldest_id = tmp[-1]["id"]
        
        return events

    async def download_all(self) -> None:
        events = await self.get_all_events()
        total_events = len(events)
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] Total events to process: {total_events}")
        # Download in reverse order to make sure we get the old events
        # before they are expired
        
        for idx, event in enumerate(reversed(events)):
            await self.upload_ring_event(idx, event, total_events)

    @retry(
        stop=stop_after_attempt(12),  # Increase max attempts
        wait=wait_exponential(multiplier=3.0, max=180.0, exp_base=2),  # Even longer waits for the full operation
        retry=retry_ring_or_404,
        before_sleep=custom_before_sleep_callback,
        reraise=True,
    )
    async def print_timestamp_and_download(self) -> None:
        """Execute the download process with retries for the entire operation."""
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] Downloading @ {pendulum.now()}")
        await self.download_all()
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] Done @ {pendulum.now()}")


async def main() -> None:
    with open(Path.home() / "gits/igor2/secretBox.json") as json_data:
        secrets = json.load(json_data)
        password = secrets["RingAccountPassword"]

    downloader = RingDownloader(
        username="idvorkin@gmail.com",
        password=password,
        app_name="PleaseForTheLoveOfferAnOfficialAPI/1.0",
        cache_file=Path("test_token.cache"),
        base_path=Path.home() / "onedrive/ring/date/",
    )

    await downloader._initialize_ring()
    nightly_execution_time = "02:00"
    print(f"Download scheduled every day @ {nightly_execution_time}")
    await downloader.print_timestamp_and_download()
    # Schedule daily execution
    schedule.every().day.at(nightly_execution_time).do(
        lambda: asyncio.create_task(downloader.print_timestamp_and_download())
    )

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
