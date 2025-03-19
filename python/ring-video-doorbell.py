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
)

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
        self.total_failures = 0  # Track total failures across all files
        self.max_total_failures = 10  # Exit after this many total failures

    # Custom before_sleep callback for better logging
    def _before_sleep_callback(self, retry_state):
        exception = retry_state.outcome.exception()
        if exception:
            if isinstance(exception, RingError):
                ic(
                    {
                        "exception_type": type(exception).__name__,
                        "message": str(exception),
                        "attempt": retry_state.attempt_number,
                        "max_attempts": retry_state.retry_object.stop.max_attempt_number,
                    }
                )

                # For certain errors, reinitialize the connection
                if "401" in str(exception):
                    ic("Unauthorized error detected, reinitializing Ring connection")
                    asyncio.create_task(self._initialize_ring())
            else:
                ic(f"Exception: {type(exception).__name__}: {str(exception)}")

            ic(
                f"Retry {retry_state.attempt_number}/{retry_state.retry_object.stop.max_attempt_number} due to: {type(exception).__name__}: {str(exception)}"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type(RingError),
        before_sleep=lambda rs: rs.retry_object.kwargs["self"]._before_sleep_callback(
            rs
        ),
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
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.0, max=60.0, exp_base=2),
        retry=retry_if_exception_type(RingError),
        before_sleep=lambda rs: rs.retry_object.kwargs["self"]._before_sleep_callback(
            rs
        ),
        reraise=False,  # To enable skipping after max attempts
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
        print(f"{idx}/{total_events}: {date_path_kind_id}")
        if not Path(date_path_kind_id).is_file():
            print("Downloading")
            try:
                await self.doorbell.async_recording_download(
                    recording_id, date_path_kind_id
                )
            except Exception as e:
                print(
                    f"Skipped downloading {date_path_kind_id} after multiple failures: {str(e)}"
                )
                self.total_failures += 1
                if self.total_failures >= self.max_total_failures:
                    ic("Maximum total failures reached, exiting")
                    raise RuntimeError(
                        f"Maximum total failures ({self.max_total_failures}) reached"
                    )
        else:
            print("Already Present")

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.0, max=60.0, exp_base=2),
        retry=retry_if_exception_type(RingError),
        before_sleep=lambda rs: rs.retry_object.kwargs["self"]._before_sleep_callback(
            rs
        ),
        reraise=False,
    )
    async def get_all_events(self) -> List[Dict[str, Any]]:
        events = []
        oldest_id = 0
        while True:
            try:
                tmp = await self.doorbell.async_history(older_than=oldest_id)
                if not tmp:
                    break
                events.extend(tmp)
                oldest_id = tmp[-1]["id"]
            except Exception as e:
                ic(
                    f"Failed to get history: {str(e)}, using events collected so far: {len(events)}"
                )
                break
        return events

    async def download_all(self) -> None:
        events = await self.get_all_events()
        total_events = len(events)
        ic(total_events)
        # Download in reverse order to make sure we get the old events
        # before they are expired
        for idx, event in enumerate(reversed(events)):
            await self.upload_ring_event(idx, event, total_events)

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=2.0, max=120.0, exp_base=2),
        retry=retry_if_exception_type(RingError),
        before_sleep=lambda rs: rs.retry_object.kwargs["self"]._before_sleep_callback(
            rs
        ),
        reraise=True,
    )
    async def print_timestamp_and_download(self) -> None:
        """Execute the download process with retries for the entire operation."""
        print(f"Downloading @ {pendulum.now()}")
        await self.download_all()
        print(f"Done @ {pendulum.now()}")


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
