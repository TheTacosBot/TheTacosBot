Feature: TacosBot GitHub Actions Handling
    As a user of TacosBot
    I want to trigger workflows based on GitHub events
    So that I can manage Terraform infrastructure effectively through GitHub comments and pull requests

    Background:
        Given a configuration file at features/.tacosbot.yaml

    Scenario Outline: Handling pull request events
        When an engineer <event_type> a pull request
        Then TacosBot creates 1 plan

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
    
    Scenario: project locked by the same pull request
        Given a project is planned for the existing pull request
        When the pull request is updated
        Then the "plan" is triggered for projects affected by the changes

    
    Scenario: project locks are deleted when pull request is closed
        When an engineer closed a pull request
        Then TacosBot deletes the locks for the project