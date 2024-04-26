import os
from src.handlers.pull_request import pull_request_handler
from src.configuration.tacobot.configuration import Config

if __name__ == "__main__":
    print(os.environ)
    event = os.environ.get("GITHUB_EVENT_NAME")
    config = Config.load(os.environ.get("INPUT_CONFIG_FILE"))

    if event == "pull_request":
        pull_request_handler(config)
    elif event == "check_run":
        pass
    elif event == "issue_comment":
        pass
    else:
        raise Exception("Unknown event type.")