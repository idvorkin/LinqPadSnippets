#!uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pendulum",
#     "ring-doorbell",
#     "schedule",
#     "icecream",
#     "pydantic",
#     "tenacity",
#     "rich"
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
from tenacity.asyncio import AsyncRetrying  # Only import AsyncRetrying
import logging
import time
import datetime
from rich.console import Console
from rich.theme import Theme

# Create a custom theme for rich
custom_theme = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "retry": "magenta",
    "timestamp": "white dim"
})

console = Console(theme=custom_theme)
logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def custom_before_sleep_callback(retry_state):
    """Custom before_sleep callback that logs detailed timing information and ensures sleep."""
    exception = retry_state.outcome.exception()
    if exception:
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        sleep_time = retry_state.next_action.sleep
        
        # Capture detailed retry state information for debugging
        console.print(f"[timestamp][{now}][/timestamp] [retry]RETRY ATTEMPT {retry_state.attempt_number}/{retry_state.retry_object.stop.max_attempt_number} - SLEEPING for {sleep_time:.2f}s[/retry]")
        console.print(f"[timestamp][{now}][/timestamp] [retry]EXCEPTION TYPE: {type(exception).__name__}[/retry]")
        console.print(f"[timestamp][{now}][/timestamp] [retry]EXCEPTION MESSAGE: {str(exception)}[/retry]")
        console.print(f"[timestamp][{now}][/timestamp] [retry]RETRY OBJECT: {retry_state.retry_object.__class__.__name__}[/retry]")
        
        # Print the retry predicate result explicitly
        if retry_state.retry_object.retry:
            predicate_result = retry_state.retry_object.retry(exception)
            console.print(f"[timestamp][{now}][/timestamp] [retry]RETRY PREDICATE RESULT: {predicate_result}[/retry]")

        # Log the expected wake-up time
        wake_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime('%H:%M:%S.%f')[:-3]
        console.print(f"[timestamp][{now}][/timestamp] [info]Expected wake-up time: {wake_time}[/info]")

        # For certain errors, provide specific messages
        if isinstance(exception, RingError) and "401" in str(exception):
            console.print(f"[timestamp][{now}][/timestamp] [warning]Unauthorized error detected, reinitializing Ring connection[/warning]")
        elif "404" in str(exception) or (isinstance(exception, RingError) and "not found" in str(exception).lower()):
            console.print(f"[timestamp][{now}][/timestamp] [warning]🔄 RETRYING: 404/Not Found error detected, will retry after sleep[/warning]")
            
            # If this is a RingError with a ClientResponseError cause, print the cause details
            if hasattr(exception, "__cause__") and exception.__cause__ is not None:
                cause = exception.__cause__
                console.print(f"[timestamp][{now}][/timestamp] [warning]CAUSE: {type(cause).__name__}: {str(cause)}[/warning]")
                if hasattr(cause, "status"):
                    console.print(f"[timestamp][{now}][/timestamp] [warning]STATUS CODE: {cause.status}[/warning]")

        # Add explicit sleep to ensure the callback doesn't return before logging is complete
        time.sleep(0.1)

def retry_ring_or_404(exception):
    """Retry if exception is RingError or contains '404' in the error message.
    
    404 errors are considered transient network issues and MUST always be retried
    as they typically resolve on subsequent attempts. All RingErrors are also retried.
    """
    # Skip silently for RetryCallState objects which aren't real errors
    error_str = str(exception)
    if "RetryCallState" in error_str:
        return False
        
    now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
    console.print(f"[timestamp][{now}][/timestamp] [info]Retry predicate evaluating exception: {type(exception).__name__}[/info]")
    console.print(f"[timestamp][{now}][/timestamp] [info]Exception details: {str(exception)}[/info]")
    
    # Track reason for not retrying for better debugging
    non_retriable_reason = "Unknown error type that doesn't match retry criteria"
    
    # Check for ClientResponseError with 404 status directly
    if hasattr(exception, "__cause__") and exception.__cause__ is not None:
        cause = exception.__cause__
        console.print(f"[timestamp][{now}][/timestamp] [info]Checking cause: {type(cause).__name__}: {str(cause)}[/info]")
        
        # Check if the cause is a ClientResponseError with 404 status
        if hasattr(cause, "status") and cause.status == 404:
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ 404 ClientResponseError detected, will retry[/success]")
            return True
        elif hasattr(cause, "status"):
            non_retriable_reason = f"ClientResponseError with non-404 status: {cause.status}"
    
    # More precise check for 404 in the error message - look for HTTP status code patterns
    if " 404 " in error_str or "status=404" in error_str or "status: 404" in error_str or "HTTP 404" in error_str or "code 404" in error_str:
        console.print(f"[timestamp][{now}][/timestamp] [success]✅ 404 HTTP status code detected, will retry[/success]")
        return True
        
    # Check if it's a RingError (which might wrap other exceptions)
    if isinstance(exception, RingError):
        # First check if this RingError contains a 404 message 
        if "404" in error_str or "not found" in error_str.lower():
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ RingError with 404/Not Found detected, will retry[/success]")
            return True
        # Only retry RingErrors that don't contain permanent failure indicators
        elif "resource unavailable" in error_str.lower():
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ RingError with resource not found detected, will retry[/success]")
            return True
        elif "unauthorized" in error_str.lower() or "401" in error_str:
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ RingError with authorization issue detected, will retry[/success]")
            return True
        elif "timeout" in error_str.lower() or "connection" in error_str.lower():
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ RingError with connection issue detected, will retry[/success]")
            return True
        else:
            console.print(f"[timestamp][{now}][/timestamp] [success]✅ General RingError detected, will retry[/success]")
            return True
    elif isinstance(exception, Exception):
        non_retriable_reason = f"Non-RingError exception type: {type(exception).__name__}"
    
    # Print detailed information about why this error isn't retriable
    console.print(f"[timestamp][{now}][/timestamp] [error]❌ Not a retriable error - REASON: {non_retriable_reason}[/error]")
    console.print(f"[timestamp][{now}][/timestamp] [error]❌ ERROR TYPE: {type(exception).__name__}[/error]")
    console.print(f"[timestamp][{now}][/timestamp] [error]❌ ERROR MESSAGE: {str(exception)}[/error]")
    
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
        wait=wait_exponential(multiplier=2.0, min=1.0, max=15.0, exp_base=2),
        retry=retry_ring_or_404,
        before_sleep=custom_before_sleep_callback,
        reraise=True,
    )
    async def _initialize_ring(self):
        """Initialize Ring authentication and device setup. Can be called again during retries."""
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        print(f"[{now}] Initializing Ring connection")
        self.auth = await self._setup_auth()
        self.ring = Ring(self.auth)
        await self.ring.async_update_data()
        self.doorbell = await self._get_doorbell()
        print(f"[{now}] Successfully initialized Ring connection")

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
        console.print(f"[timestamp][{now}][/timestamp] {idx}/{total_events}: {date_path_kind_id}")
        
        if not Path(date_path_kind_id).is_file():
            console.print(f"[timestamp][{now}][/timestamp] [success]Downloading[/success]")
            
            # Manual retry logic with explicit exception handling
            attempt_count = 1
            max_attempts = 3
            
            while attempt_count <= max_attempts:
                try:
                    now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    console.print(f"[timestamp][{now}][/timestamp] [retry]⏱ ATTEMPT {attempt_count}/{max_attempts}[/retry]")
                    
                    await self.doorbell.async_recording_download(
                        recording_id, date_path_kind_id
                    )
                    
                    now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    console.print(f"[timestamp][{now}][/timestamp] [success]Successfully downloaded {recording_id}[/success]")
                    break  # Exit loop on success
                    
                except Exception as e:
                    now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
                    console.print(f"[timestamp][{now}][/timestamp] [warning]🛑 Download failed with: {type(e).__name__}: {str(e)}[/warning]")
                    
                    # Check if this is a 404 error
                    if "404" in str(e) or (hasattr(e, "__cause__") and e.__cause__ and hasattr(e.__cause__, "status") and e.__cause__.status == 404):
                        console.print(f"[timestamp][{now}][/timestamp] [warning]🔄 Detected 404 error, will retry...[/warning]")
                        
                        if attempt_count < max_attempts:
                            # Calculate wait time with exponential backoff
                            wait_time = min(2 ** (attempt_count - 1) * 3, 15)
                            console.print(f"[timestamp][{now}][/timestamp] [info]Waiting {wait_time} seconds before next attempt...[/info]")
                            await asyncio.sleep(wait_time)
                            attempt_count += 1
                        else:
                            console.print(f"[timestamp][{now}][/timestamp] [error]⚠️ Maximum retry attempts ({max_attempts}) reached. Giving up on this recording.[/error]")
                            break
                    else:
                        # For non-retriable errors, just break the loop
                        console.print(f"[timestamp][{now}][/timestamp] [error]❌ Non-retriable error. Skipping this recording.[/error]")
                        break
        else:
            console.print(f"[timestamp][{now}][/timestamp] [info]Already Present[/info]")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=3.0, min=1.0, max=15.0, exp_base=2),
        retry=retry_ring_or_404,
        before_sleep=custom_before_sleep_callback,
        reraise=True,
    )
    async def get_history_batch(self, oldest_id: int = 0) -> List[Dict[str, Any]]:
        """Get a batch of history events with proper retry handling"""
        result = await self.doorbell.async_history(older_than=oldest_id)
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        console.print(f"[timestamp][{now}][/timestamp] [success]Successfully retrieved history batch[/success]")
        return result

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
        console.print(f"[timestamp][{now}][/timestamp] [info]Total events to process: {total_events}[/info]")
        # Download in reverse order to make sure we get the old events
        # before they are expired

        for idx, event in enumerate(reversed(events)):
            await self.upload_ring_event(idx, event, total_events)

    # Removed retry decorator since we're handling retries in upload_ring_event
    async def print_timestamp_and_download(self) -> None:
        """Execute the download process with retries for the entire operation."""
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        console.print(f"[timestamp][{now}][/timestamp] [info]Downloading @ {pendulum.now()}[/info]")
        await self.download_all()
        now = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]
        console.print(f"[timestamp][{now}][/timestamp] [success]Done @ {pendulum.now()}[/success]")


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
    console.print(f"[info]Download scheduled every day @ {nightly_execution_time}[/info]")
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
