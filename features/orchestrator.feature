Feature: TacosBot GitHub Actions Handling
    As a user of TacosBot
    I want to trigger workflows based on GitHub events
    So that I can manage Terraform infrastructure effectively through GitHub comments and pull requests

    Background:
        Given the GitHub token is available
        And a configuration file at features/.tacosbot.yaml

    Scenario Outline: Handling pull request events
        Given a "<event_type>" event for pull request
        When the TacosBot processes the pull request
        Then the "<expected_workflow>" is triggered for projects affected by the changes

        Examples:
            | event_type  | expected_workflow |
            | opened      | plan              |
            | synchronize | plan              |
            | edited      | plan              |
            | reopened    | plan              |

    Scenario: project locked by a different pull request
        Given a pre-existing deployment for the project
        When a pull request is opened
        Then TacosBot doesn't trigger jobs
    
    Scenario: project locks are deleted when pull request is closed
        Given a "closed" event for pull request
        When the TacosBot processes the pull request
        Then TacosBot deletes the locks for the project