import os
from behave import given, when, then
from src.main import run


# Mock the GitHub and config modules
from src.configuration.tacobot.configuration import Config
from src.configuration.tacobot.project import Project

@given('the GitHub token is available')
def step_impl(context):
    os.environ['INPUT_GITHUB_TOKEN'] = 'fake_token'
    os.environ['GITHUB_EVENT_PATH'] = "features/example_events/pull_request.json"

@given('a configuration file with projects')
def step_impl(context):
    context.tacosbot_config = Config(
        projects=[
            Project(dir='examples/gh_dir0', workflow='tacosbot_production'),
            Project(dir='examples/gh_dir1', workflow='tacosbot_production'),

        ]
    )

@given("drift detection is enabled")
def step_impl(context):
    os.environ['INPUT_DRIFT_DETECTION'] = "true"
    os.environ['INPUT_FILES'] = "examples/gh_dir0/main.tf"

@given("the user has already created a deployment for the project")
def step_impl(context):
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=examples/gh_dir0:tacosbot_production', json=[{'id': '1234', 'payload': {'pr_number': 2}}])
    
@given('a "{event_type}" event for pull request')
def step_impl(context, event_type):
    context.event_type = event_type
    if event_type == "closed":
        os.environ['GITHUB_EVENT_PATH'] = "features/example_events/pull_request_closed.json"
    os.environ['GITHUB_EVENT_NAME'] = "pull_request"

@when('the pull request is updated')
def step_impl(context):
    with context.m:
        os.environ['GITHUB_EVENT_NAME'] = "pull_request"
        run()

@given('an unsupported event type "{event_type}"')
def step_impl(context, event_type):
    os.environ['GITHUB_EVENT_NAME'] = event_type

@when('the TacosBot processes the event')
def step_impl(context):
    with context.m:
        try:
            run()
        except Exception as e:
            context.exception = e

@then('the "{expected_workflow}" workflow should be triggered for the specified project')
@then('the "{expected_workflow}" is triggered for projects affected by the changes')
def step_impl(context, expected_workflow):
    # Assert that the appropriate workflow was triggered based on the event type
    # This would require the mock to have a record of the invoked workflows
    try:
        context.exception
        assert False, context.exception
    except AttributeError:
        pass
    assert 'dispatches' in context.m.last_request.url, context.m.last_request.url
    assert 'event_type' in context.m.last_request.json(), context.m.last_request.json()

@given('a comment "{comment}" on the pull request')
def step_impl(context, comment):
    os.environ['INPUT_COMMENT'] = comment

@when('the comment is processed by the TacosBot')
def step_impl(context):
    with context.m:
        os.environ['GITHUB_EVENT_NAME'] = "issue_comment"
        try:
            run()
        except Exception as e:
            context.exception = e

@given('an unsupported event type is triggered')
def step_impl(context):
    os.environ['GITHUB_EVENT_NAME'] = 'unsupported_event'

@then('an error should be raised indicating "{message}"')
def step_impl(context, message):
    assert message in str(context.exception), str(context.exception)

@given("a configuration file at {path}")
def step_impl(context, path):
    os.environ['INPUT_CONFIG_FILE'] = path

@given("a pre-existing deployment for the project")
def step_impl(context):
    context.m.get(
        'https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=examples/gh_dir0:tacosbot_production',
        json=[
            {
                'statuses_url': 'https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses',
                'payload': {'pr_number': 0},
                'id': '1234',
                
            }
        ]
    )
    context.m.get(
        'https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses',
        json=[{'state': 'pending'}])

@given("a project is planned for the existing pull request")
def step_impl(context):
    context.m.get(
        'https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=examples/gh_dir0:tacosbot_production',
        json=[
            {
                'statuses_url': 'https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses',
                'payload': {'pr_number': 2},
                'id': '1234',
                
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


@then("TacosBot triggers jobs")
def step_impl(context):
    assert 'dispatches' in context.m.last_request.url, context.m.last_request

@then("TacosBot doesn't trigger jobs")
def step_impl(context):
    assert context.m.last_request is None or 'dispatches' not in context.m.last_request.url, context.m.last_request

@then("TacosBot deletes the locks for the project")
def step_impl(context):
    assert context.m.last_request.method == 'DELETE', context.m.last_request

@then("TacosBot unlocks the project")
def step_impl(context):
    assert context.m.last_request.method == 'DELETE', context.m.last_request