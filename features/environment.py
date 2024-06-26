import requests_mock
import os
from src.main import run

def before_scenario(context, scenario):
    os.environ['INPUT_GITHUB_TOKEN'] = 'fake_token'
    os.environ['GITHUB_EVENT_PATH'] = 'features/example_events/pull_request.json'
    os.environ['INPUT_CONFIG_FILE'] = 'features/.tacosbot.yaml'

    context.m = requests_mock.Mocker()

    context.dispatched_events = context.m.post("https://api.github.com/repos/Codertocat/Hello-World/dispatches")

    context.m.get(
        "https://api.github.com/repos/Codertocat/Hello-World/pulls/2/files?per_page=100",
        json=[{'filename': "examples/gh_dir0/main.tf"}])

    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=examples/gh_dir0:tacosbot_production', json=[])
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments', json={'id': '1234'})
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses', json={'id': '1234'})
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=foo', json=[{'id': '1234', 'payload': {'pr_number': 2}}])
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses', json=[{'state': 'pending'}])
    context.m.delete('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234')
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?sha=ec26c3e57ca3a959ca5aad62de7213c562f8c821', json=[{'id': '1234'}])


    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/pulls/2', json={'head': {'sha': '1234', 'ref': 'main'}})
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/statuses/ec26c3e57ca3a959ca5aad62de7213c562f8c821', json={'id': '1234'})

    def run_tacosbot():
        with context.m:
            try:
                run()
            except Exception as e:
                context.exception = e
    context.run = run_tacosbot
def after_scenario(context, scenario):
    os.environ['INPUT_GITHUB_TOKEN'] = ''
    os.environ['INPUT_DRIFT_DETECTION'] = ''
    os.environ['INPUT_CONFIG_FILE'] = ''