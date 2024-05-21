import os
from behave import given

@given('the GitHub token is missing')
def step_impl(context):
    os.environ['INPUT_GITHUB_TOKEN'] = ''
    os.environ['GITHUB_EVENT_PATH'] = ''

@given('no configuration file is specified')
def step_impl(context):
    os.environ['INPUT_CONFIG_FILE'] = ''

@given('the GitHub dispatch API is down')
def step_impl(context):
    context.dispatched_events = context.m.post("https://api.github.com/repos/Codertocat/Hello-World/dispatches", status_code=500)

@given('the GitHub files changed API is down')
def step_impl(context):
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/pulls/2/files?per_page=100', status_code=500)