import os
from src.handlers.pull_request import pull_request_handler
from src.handlers.drift_detection import drift_detection_handler
from src.configuration.tacobot.configuration import Config


def run():
    event = os.environ.get("GITHUB_EVENT_NAME")
    config_file = os.environ.get("INPUT_CONFIG_FILE")

    try:
        print(f"Loading configuration file: {config_file}")
        config = Config.load(config_file)
    except BaseException:
        raise Exception(f"Failed to load configuration file: {config_file}")

    if event == "pull_request":
        pull_request_handler(config)
    elif os.getenv("INPUT_DRIFT_DETECTION") != "":
        drift_detection_handler(config)
    else:
        raise Exception("Unknown event type.")


if __name__ == "__main__":
    run()
