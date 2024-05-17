import os
from src.handlers.pull_request import pull_request_handler
from src.handlers.drift_detection import drift_detection_handler
from src.handlers.comments import comment_handler
from src.configuration.tacobot.configuration import Config
from src.custom_exceptions import ConfigurationError, UnsupportedEventError

def run():
    """
    Main function to handle different GitHub events triggered by actions.

    This function reads the GitHub event type from the environment and dispatches
    the event to its respective handler based on the configuration provided by the user.

    Raises:
        Exception: If the configuration file cannot be loaded or an unsupported event type is triggered.
    """
    event = os.environ.get("GITHUB_EVENT_NAME")
    config_file = os.environ.get("INPUT_CONFIG_FILE")

    try:
        # Load the configuration from the specified YAML file.
        config = Config.load(config_file)
    except Exception as e:
        raise ConfigurationError(config_file, str(e))

    # Dispatch the event to the appropriate handler.
    if event == "pull_request":
        pull_request_handler(config)
    elif event == "issue_comment":
        comment_handler(config)
    elif os.getenv("INPUT_DRIFT_DETECTION") == "true":
        drift_detection_handler(config)
    else:
        raise UnsupportedEventError(event)

if __name__ == "__main__":
    run()