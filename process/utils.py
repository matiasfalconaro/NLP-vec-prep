import json
import logging

from typing import Any

from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


class FakeContextManager:
    """
    A fake context manager to handle the temporary directory.
    """
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return self.path

    def __exit__(self):
        pass


class MockDocument:
    """
    A mock document class to hold the text and metadata.
    """
    def __init__(self, text, metadata=None):
        self.page_content = text
        self.metadata = metadata if metadata is not None else {}


def load_config() -> Any:
    """
    Load the configuration from the config.json file.
    """
    with open('config.json', 'r') as file:
        return json.load(file)


def setup_logging() -> Any:
    """
    Setup the logging configuration.
    """
    config = load_config()
    logging_config = config.get("logging", {})

    if not logging_config.get("enabled", False):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        return logging.getLogger(__name__)

    logging.basicConfig(
        filename=logging_config.get("log_file", "default.log"),
        level=getattr(logging, logging_config.get("level", "INFO").upper()),
        format=logging_config.get("format",
                                  "%(asctime)s - %(levelname)s - %(message)s"),
        datefmt=logging_config.get("datefmt", "%Y-%m-%d %H:%M:%S")
    )

    return logging.getLogger(__name__)


def start_monitoring(path: str) -> Any:
    """
    Monitor the given path for file system events.
    """
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer
