@comments
Feature: TacosBot responds and handles Pull Request Comments

    @plan
    Scenario: developer triggers plan via comment
        When an engineer triggers a plan via comment
        Then TacosBot creates 1 plan

    @apply
    Scenario: developer triggers apply via comment
        When an engineer triggers an apply via comment
        Then TacosBot performs 1 apply


    Scenario: Ignores comments that do not match the expected format
        Given a comment "apply --project gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot doesn't trigger jobs

    @lock
    Scenario: project locked by a different pull request and user tries to apply
        Given a pre-existing deployment for the project
        And a comment "tacosbot plan --project examples/gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot doesn't trigger jobs

    @lock
    Scenario: handles unlock comment
        Given the user has already created a deployment for the project
        And a comment "tacosbot unlock --project examples/gh_dir0:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then TacosBot unlocks the project
    
    @plan
    Scenario: attempt to plan project that does not exist
        Given a comment "tacosbot plan --project gh_dirx:tacosbot_production" on the pull request
        When the comment is processed by the TacosBot
        Then an error should be raised indicating "No project found"