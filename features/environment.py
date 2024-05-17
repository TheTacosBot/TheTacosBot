import requests_mock


def before_all(context):
    context.m = requests_mock.Mocker()

    context.m.post("https://api.github.com/repos/Codertocat/Hello-World/actions/workflows/tacosbot_production_plan.yaml/dispatches")
    context.m.post("https://api.github.com/repos/Codertocat/Hello-World/actions/workflows/tacosbot_production_apply.yaml/dispatches")
    context.m.get(
        "https://api.github.com/repos/Codertocat/Hello-World/pulls/2/files?per_page=100",
        json=[{'filename': "examples/gh_dir0/main.tf"}])

    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=examples/gh_dir0:tacosbot_production', json=[])
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments', json={'id': '1234'})
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses', json={'id': '1234'})
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?environment=foo', json=[{'id': '1234', 'payload': {'pr_number': 2}}])
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses', json=[{'state': 'pending'}])
    context.m.delete('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234')
    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/pulls/2', json={'head': {'sha': '1234', 'ref': 'main'}})