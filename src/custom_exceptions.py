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
    pass

class CommentNotFoundError(Exception):
    pass

class ProjectNotFoundError(Exception):
    pass