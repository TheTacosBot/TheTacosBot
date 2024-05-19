Feature: Tacosbot handles errors gracefully
    Background:
        Given a configuration file with projects

    Scenario: missing github token
        Given a "opened" event for pull request
        When the TacosBot processes the event
        Then an error should be raised indicating "GitHub token not found"
    
    Scenario: unsupported event type
        Given a configuration file at features/.tacosbot.yaml
        And an unsupported event type "push"
        And the GitHub token is available
        When the TacosBot processes the event
        Then an error should be raised indicating "Unknown or unsupported event type: push"

    Scenario: missing project configuration
        Given a "opened" event for pull request
        And the GitHub token is available
        When the TacosBot processes the event
        Then an error should be raised indicating "No such file"