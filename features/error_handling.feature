Feature: Tacosbot handles errors gracefully
    Background:
        Given a configuration file with projects

    Scenario: missing github token
        Given the GitHub token is missing
        When an engineer opened a pull request
        Then an error should be raised indicating "GitHub token not found"
    
    Scenario: unsupported event type
        Given a configuration file at features/.tacosbot.yaml
        And an unsupported event type "push"
        When the TacosBot processes the event
        Then an error should be raised indicating "Unknown or unsupported event type: push"

    Scenario: missing project configuration
        Given a configuration file at doesnt_exist/.tacosbot.yaml
        When an engineer opened a pull request
        Then an error should be raised indicating "No such file"

    @wip
    Scenario: no configuration file provided to GitHub Action
        Given no configuration file is specified
        When an engineer opened a pull request
        Then an error should be raised indicating "No configuration file specified"