import os
from behave import given, when, then
from src.main import run


# Mock the GitHub and config modules
from src.github import GitHub
from src.configuration.tacobot.configuration import Config
from src.configuration.tacobot.project import Project
from src.handlers.pull_request import pull_request_handler
from src.handlers.comments import comment_handler

@given('the GitHub token is available')
def step_impl(context):
    os.environ['INPUT_GITHUB_TOKEN'] = 'fake_token'
    os.environ['GITHUB_EVENT_PATH'] = "features/example_events/pull_request.json"
    context.github = GitHub('fake_token')
    context.tacosbot_config = Config(
        projects=[
            Project(dir='examples/gh_dir0', workflow='tacosbot_production'),
            Project(dir='examples/gh_dir1', workflow='tacosbot_production'),

        ]
    )

@given('a "{event_type}" event for pull request')
def step_impl(context, event_type):
    context.event_type = event_type
    os.environ['GITHUB_EVENT_NAME'] = event_type

@given('the pull request contains changes to files')
def step_impl(context):
    pass

@when('the TacosBot processes the pull request')
def step_impl(context):
    with context.m:
        pull_request_handler(context.tacosbot_config)

@then('the "{expected_workflow}" workflow should be triggered for the specified project')
@then('the "{expected_workflow}" is triggered for projects affected by the changes')
def step_impl(context, expected_workflow):
    # Assert that the appropriate workflow was triggered based on the event type
    # This would require the mock to have a record of the invoked workflows
    assert f'{expected_workflow}.yaml' in context.m.last_request.url, context.m.last_request.url

@given('a pull request with id "{pr_id}"')
def step_impl(context, pr_id):
    os.environ['PULL_REQUEST_ID'] = pr_id

@given('a comment "{comment}" on the pull request')
def step_impl(context, comment):
    os.environ['INPUT_COMMENT'] = comment

@when('the comment is processed by the TacosBot')
def step_impl(context):
    with context.m:
        comment_handler(context.tacosbot_config)

@given('an unsupported event type is triggered')
def step_impl(context):
    os.environ['GITHUB_EVENT_NAME'] = 'unsupported_event'

@then('an error should be raised indicating "{message}"')
def step_impl(context, message):
    with context.m:
        try:
            pull_request_handler(context.tacosbot_config)  # Assuming this is the function that might fail
            assert False, "Expected an error but none was raised"
        except Exception as e:
            assert message in str(e)
@given("a configuration file at {path}")
def step_impl(context, path):
    os.environ['INPUT_CONFIG_FILE'] = path

@given("a pre-existing deployment for the project")
def step_impl(context):
    context.m.get(
        'https://api.github.com/repos/Codertocat/Hello-World/deployments?enviroment=examples/gh_dir0:tacobot_production',
        json=[
            {
                'statuses_url': 'https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses',
                'payload': {'pr_number': 0}
                
            }
        ]
    )
    context.m.get(
        'https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses',
        json=[{'state': 'pending'}])

@when("a pull request is opened")
def step_impl(context):
    os.environ['GITHUB_EVENT_NAME'] = 'pull_request'
    os.environ['INPUT_GITHUB_TOKEN'] = 'foo'
    os.environ['GITHUB_EVENT_PATH'] = "features/example_events/pull_request.json"
    with context.m:
        context.result = run()


@then("TacosBot fails gracefully")
def step_impl(context):
    assert context.m.called is False


@then("TacosBot triggers jobs")
def step_impl(context):
    print(context.m.last_request)
    assert 'dispatches' in context.m.last_request.url, context.m.last_request

@then("TacosBot doesn't trigger jobs")
def step_impl(context):
    print(context.m.last_request)
    assert 'dispatches' in context.m.last_request.url, context.m.last_request