import os
from src.handlers.pull_request import pull_request_handler
from src.handlers.drift_detection import drift_detection_handler
from src.configuration.tacobot.configuration import Config


def run():
    event = os.environ.get("GITHUB_EVENT_NAME")

    try:
        config = Config.load(os.environ.get("INPUT_CONFIG_FILE"))
    except BaseException:
        print("Failed to load configuration file.")
        return

    if event == "pull_request":
        pull_request_handler(config)
    elif event == "check_run":
        pass
    elif event == "issue_comment":
        pass
    elif os.getenv("INPUT_DRIFT_DETECTION") != "":
        drift_detection_handler()
    else:
        raise Exception("Unknown event type.")


if __name__ == "__main__":
    run()
