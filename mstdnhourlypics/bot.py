import logging
import os
import random
import socket
import time
from typing import Deque

import schedule
from mastodon import Mastodon, MastodonError

from mstdnhourlypics.settings import Secrets, Settings, get_secrets, get_settings
from mstdnhourlypics.utils import is_image_file


_logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        self.settings: Settings = get_settings()
        self.image_queue: Deque[str] = Deque([])
        self.recent_files: Deque[str] = Deque([], self.settings.image_queue_size)

        secrets: Secrets = get_secrets()
        self.mastodon_client = Mastodon(
            client_id=secrets.client_key,
            client_secret=secrets.client_secret,
            access_token=secrets.access_token,
            api_base_url=self.settings.api_base_url,
        )
        self.logged_in = False
        self._delay = 1

    def _update_delay(self):
        self._delay = random.randrange(1, 30)

    def load_recents_file(self):
        if self.settings.recents_file not in os.listdir():
            _logger.info(
                (
                    "Recent pics file '%s' not found in current directory, it will be"
                    " created the next time a post was successfully published"
                ),
                self.settings.recents_file,
            )
            return

        with open(self.settings.recents_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    self.recent_files.append(line)

            _logger.info(
                "Loaded %s filename%s in recents file",
                len(self.recent_files),
                "s" if len(self.recent_files) != 1 else "",
            )

    def log_in(self):
        account_info = self.mastodon_client.account_verify_credentials()
        _logger.info("Logged in as @%s", account_info["username"])
        self.logged_in = True

    def fill_queue(self):
        files = list(
            filter(lambda f: is_image_file(f), os.listdir(self.settings.images_path))
        )
        counter = 0
        while len(self.image_queue) < self.settings.image_queue_size:
            filename = random.choice(files)
            if not (filename in self.image_queue or filename in self.recent_files):
                self.image_queue.appendleft(filename)
                counter += 1
        _logger.info("Added %s image%s to queue", counter, "s" if counter != 1 else "")

    def send_post(self, media_path: str, body=""):
        media_id = ""
        while True:
            try:
                if not media_id:
                    _logger.debug("Uploading %s", media_path)
                    media_info = self.mastodon_client.media_post(media_path)
                    media_id = media_info["id"]

                _logger.debug("Sending post")
                return self.mastodon_client.status_post(body, media_ids=media_id)
            except socket.gaierror:
                # Retry if network-related issues occurred when sending data
                _logger.exception("Failed to publish post, retrying in 30 seconds")
                time.sleep(30)
            except MastodonError:
                _logger.exception("Failed to publish post")
                break

    def post_image(self, no_delay: bool = False):
        # Step 1: Fill up queue if empty
        if len(self.image_queue) < 1:
            self.fill_queue()

        # Step 2: Pull out image on front of queue
        filename = self.image_queue.pop()

        # Step 3: Wait until delay is over
        if not no_delay:
            time.sleep(self._delay)
            self._update_delay()

        # Step 4: Post the image
        response = self.send_post(f"{self.settings.images_path}/{filename}")
        if response:
            _logger.info("Post sent, view it at %s", response["url"])
            q_len = len(self.image_queue)
            _logger.debug(
                "%s image%s remaining in queue", q_len, "s" if q_len != 1 else ""
            )

        # Step 5: Update and save recent filenames
        self.recent_files.append(filename)
        with open(self.settings.recents_file, mode="w") as f:
            f.write("\n".join(self.recent_files) + "\n")
        _logger.debug(
            "Saved paths to last %s images to %s",
            len(self.recent_files),
            self.settings.recents_file,
        )

    def set_up(self):
        # Make sure the images directory exists and is accessible
        os.listdir(self.settings.images_path)

        self.load_recents_file()
        self.log_in()
        self._update_delay()

    def run(self):
        assert (
            self.logged_in
        ), "you must run 'set_up()' first before running this function"

        # Post immediately if current minute is equal to target minute
        current_min = time.localtime().tm_min
        if current_min == self.settings.minute:
            self.post_image(no_delay=True)

        schedule.every().hour.at(f":{self.settings.minute:02d}").do(self.post_image)
        _logger.info(
            (
                "Schedule set to %s minute%s past the hour, next tweet to be sent at"
                " %s:%02d"
            ),
            self.settings.minute,
            "s" if self.settings.minute != 1 else "",
            schedule.next_run().strftime("%H:%M"),
            self._delay,
        )
        print("Press Ctrl+C to exit at any time\n")

        # Main loop --- press Ctrl+C to stop
        while True:
            schedule.run_pending()
            time.sleep(1)
