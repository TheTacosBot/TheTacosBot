Feature: TacosBot responds and handles Pull Request Comments

    Background:
        Given the GitHub token is available
        And a configuration file at features/.tacosbot.yaml

    Scenario Outline: Handling comments to trigger workflows
        Given a comment "<comment>" on the pull request
        When the comment is processed by the TacosBot
        Then the "<expected_workflow>" workflow should be triggered for the specified project

        Examples:
            | comment                                                       | expected_workflow |
            | tacosbot apply --project examples/gh_dir0:tacosbot_production | apply             |
            | tacosbot plan --project examples/gh_dir0:tacosbot_production  | plan              |

    Scenario: Ignores comments that do not match the expected format
        Given a comment "apply --project gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot doesn't trigger jobs

