import os
from behave import given
from src.main import run

@given("a configuration file at {path}")
def step_impl(context, path):
    os.environ['INPUT_CONFIG_FILE'] = path

@when("a pull request is opened")
def step_impl(context):
    os.environ['GITHUB_EVENT_NAME'] = 'pull_request'
    os.environ['INPUT_GITHUB_TOKEN'] = 'foo'
    os.environ['GITHUB_EVENT_PATH'] = "features/example_events/pull_request.json"
    with context.m:
        context.result = run()

@then("TacoBot fails gracefully")
def step_impl(context):
    assert context.m.called is False

@then("TacoBot triggers jobs")
def step_impl(context):
    print(context.m.last_request)
    assert 'dispatches' in context.m.last_request.url, context.m.last_request