class ConfigurationError(Exception):
    """Exception raised for errors in loading or parsing the configuration file."""
    def __init__(self, config_file, message="Failed to load or parse configuration file"):
        self.config_file = config_file
        self.message = f"{message}: {config_file}"
        super().__init__(self.message)

class UnsupportedEventError(Exception):
    """Exception raised for handling unsupported GitHub event types."""
    def __init__(self, event_type, message="Unknown or unsupported event type"):
        self.event_type = event_type
        self.message = f"{message}: {event_type}"
        super().__init__(self.message)

class GitHubTokenNotFoundError(Exception):
    def __init__(self, message="GitHub token not found in the environment"):
        self.message = message
        super().__init__(self.message)

class CommentNotFoundError(Exception):
    def __init__(self, message="Comment not found in the environment"):
        self.message = message
        super().__init__(self.message)

class ProjectNotFoundError(Exception):
    def __init__(self, message="No project found matching the provided name"):
        self.message = message
        super().__init__(self.message)

class ProjectLockedError(Exception):
    def __init__(self, message="Project is locked and cannot be deployed"):
        self.message = message
        super().__init__(self.message)

class TooManyDispatchKeysError(Exception):
    def __init__(self, message="Too many dispatch keys provided"):
        self.message = message
        super().__init__(self.message)

class TriggerWorkflowError(Exception):
    def __init__(self, message="Failed to trigger the workflow"):
        self.message = message
        super().__init__(self.message)