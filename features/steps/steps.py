import os
from behave import given
from src.main import run


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