Feature: TacosBot responds and handles Pull Request Comments

    Background:
        Given a configuration file at features/.tacosbot.yaml

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

    Scenario: project locked by a different pull request and user tries to apply
        Given a pre-existing deployment for the project
        And a comment "tacosbot plan --project examples/gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot doesn't trigger jobs

    Scenario: handles unlock comment
        Given the user has already created a deployment for the project
        And a comment "tacosbot unlock --project examples/gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot unlocks the project
    
    Scenario: attempt to plan project that does not exist
        Given a comment "tacosbot plan --project gh_dirx:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then an error should be raised indicating "No project found"