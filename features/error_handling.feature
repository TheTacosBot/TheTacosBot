Feature: Tacosbot handles errors gracefully
    Background:
        Given a configuration file with projects

    Scenario: missing github token
        Given a "opened" event for pull request
        When the TacosBot processes the pull request
        Then an error should be raised indicating "GitHub token not found"