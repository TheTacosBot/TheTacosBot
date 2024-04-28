Feature: TacoBot Orchestrator

    Scenario: Handles Missing Configuration File
        Given a configuration file at .doesnt_exist
        When a pull request is opened
        Then TacoBot fails gracefully

    Scenario: Triggers Jobs Correctly
        Given a configuration file at .tacobot.yaml
        When a pull request is opened
        Then TacoBot triggers jobs