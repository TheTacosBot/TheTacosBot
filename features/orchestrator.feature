Feature: TacosBot GitHub Actions Handling
    As a user of TacosBot
    I want to trigger workflows based on GitHub events
    So that I can manage Terraform infrastructure effectively through GitHub comments and pull requests

    Background:
        Given the GitHub token is available

    Scenario Outline: Handling pull request events
        Given a "<event_type>" event for pull request
        And the pull request contains changes to files
        When the TacosBot processes the pull request
        Then the "<expected_workflow>" is triggered for projects affected by the changes

        Examples:
            | event_type  | expected_workflow |
            | opened      | plan              |
            | synchronize | plan              |
            | edited      | plan              |
            | reopened    | plan              |

    Scenario Outline: Handling comments to trigger workflows
        Given a pull request with id "<pr_id>"
        And a comment "<comment>" on the pull request
        When the comment is processed by the TacosBot
        Then the "<expected_workflow>" workflow should be triggered for the specified project

        Examples:
            | pr_id | comment                                                       | expected_workflow |
            | 101   | tacosbot apply --project examples/gh_dir0:tacosbot_production | apply             |
            | 102   | tacosbot plan --project examples/gh_dir0:tacosbot_production  | plan              |