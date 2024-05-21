Feature: Project

    Scenario: project without directory raises an error
        Given a project without a directory
        Then an error should be raised indicating "missing 1 required positional argument: 'dir'"
    
    Scenario: project without workflow raises an error
        Given a project without a workflow
        Then an error should be raised indicating "missing 1 required positional argument: 'workflow'"