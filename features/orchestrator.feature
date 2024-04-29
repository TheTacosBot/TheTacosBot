Feature: TacoBot Orchestrator

    Scenario: Handles Missing Configuration File
        Given a configuration file at .doesnt_exist
        When a pull request is opened
        Then TacosBot fails gracefully

    Scenario: Triggers Jobs Correctly
        Given a configuration file at .tacobot.yaml
        When a pull request is opened
        Then TacosBot triggers jobs
    
    Scenario: Project Locking
        Given a configuration file at .tacobot.yaml
        And a pre-existing deployment for the project
        When a pull request is opened
        Then TacosBot doesn't trigger jobs