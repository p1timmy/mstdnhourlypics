from dataclasses import dataclass
from functools import lru_cache

import tyaml
from enforce_typing import enforce_types

SETTINGS_FILE = "settings.yaml"
SECRETS_FILE = "secrets.yaml"


@enforce_types
@dataclass
class Settings:
    instance_url: str
    images_path: str
    minute: int = 0
    recents_file: str = "recent_files.txt"

    image_queue_size: int = 12
    """
    The number of images to queue at a time. Setting this to 1 will allow images to be
    sent more than once in a row
    """

    def __post_init__(self):
        assert 0 <= self.minute < 60, "minute must be between 0 and 59"
        assert self.image_queue_size > 0, "image_queue_size must be at least 1"


@enforce_types
@dataclass
class Secrets:
    client_key: str
    client_secret: str
    access_token: str


@lru_cache()
def get_settings() -> Settings:
    with open(SETTINGS_FILE) as settings_file:
        settings = tyaml.load(settings_file.read(), Settings)
        if settings is None:
            raise TypeError(f"{SETTINGS_FILE} is empty")
        return settings


@lru_cache()
def get_secrets() -> Secrets:
    with open(SECRETS_FILE) as secrets_file:
        secrets = tyaml.load(secrets_file.read(), Secrets)
        if secrets is None:
            raise TypeError(f"{SECRETS_FILE} is empty")
        return secrets
