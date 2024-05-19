import os
from src.handlers.pull_request import pull_request_handler
from src.handlers.drift_detection import drift_detection_handler
from src.handlers.comments import comment_handler
from src.configuration.tacobot.configuration import Config
from src.custom_exceptions import *

def validate_inputs():
    if 'INPUT_GITHUB_TOKEN' not in os.environ or not os.environ['INPUT_GITHUB_TOKEN']:
        raise GitHubTokenNotFoundError()
    if 'INPUT_CONFIG_FILE' not in os.environ or not os.environ['INPUT_CONFIG_FILE']:
        raise ConfigurationError("No configuration file specified")

    event = os.environ.get("GITHUB_EVENT_NAME")

    if event == 'issue_comment' and 'INPUT_COMMENT' not in os.environ:
        raise CommentNotFoundError()

def load_config():
    config_file = os.environ.get("INPUT_CONFIG_FILE")
    try:
        # Load the configuration from the specified YAML file.
        return Config.load(config_file)
    except Exception as e:
        raise ConfigurationError(config_file, str(e))
def run():
    """
    Main function to handle different GitHub events triggered by actions.

    This function reads the GitHub event type from the environment and dispatches
    the event to its respective handler based on the configuration provided by the user.
    """

    validate_inputs()
    config = load_config()

    # Dispatch the event to the appropriate handler.
    event = os.environ.get("GITHUB_EVENT_NAME")
    if os.getenv("INPUT_DRIFT_DETECTION") == "true":
        drift_detection_handler(config)
    elif event == "pull_request":
        pull_request_handler(config)
    elif event == "issue_comment":
        comment_handler(config)
    else:
        raise UnsupportedEventError(event)

if __name__ == "__main__": # pragma: no cover
    try:
        run()
    except GitHubTokenNotFoundError:
        print("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        exit(1)
    except ConfigurationError as e:
        print(f"Error loading configuration file: {e}")
        exit(1)
    except UnsupportedEventError as e:
        print(f"Unsupported event type: {e}")
        exit(1)
    except TooManyDispatchKeysError as e:
        print("Too many dispatch keys provided. Please provide fewer than 10 dispatch keys. See GitHub documentation for more info: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#create-a-repository-dispatch-event")
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)