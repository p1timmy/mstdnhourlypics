import logging
import time

import schedule

from mstdnhourlypics import __version__
from mstdnhourlypics.bot import Bot

LOGFILE = "bot.log"
_logger = logging.getLogger(__name__)


def logging_setup():
    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG)
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s (%(name)s): %(message)s", "%Y-%m-%dT%H:%M:%SZ"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create file handler
    file_handler = logging.FileHandler(LOGFILE)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Silence info/debug logs from libraries
    logging.getLogger("oauthlib").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("requests_oauthlib").setLevel(logging.WARNING)
    logging.getLogger("schedule").setLevel(logging.WARNING)


def main():
    _logger.info("Mastodon Hourly Pics Bot v%s is starting up...", __version__)
    bot = Bot()
    try:
        bot.set_up()
        bot.run()
    except (KeyboardInterrupt, SystemExit):
        _logger.info("Shutting down...")
    except Exception:
        _logger.exception("Fatal error occurred, shutting down...")
    schedule.clear()


if __name__ == "__main__":
    logging_setup()
    main()
