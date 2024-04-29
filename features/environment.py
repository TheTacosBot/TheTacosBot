import requests_mock


def before_all(context):
    context.m = requests_mock.Mocker()

    context.m.post(
        "https://api.github.com/repos/Codertocat/Hello-World/actions/workflows/tacobot_production_plan.yaml/dispatches"
    )
    context.m.get(
        "https://api.github.com/repos/Codertocat/Hello-World/pulls/2/files?per_page=100",
        json=[{'filename': "examples/gh_dir0/main.tf"}])

    context.m.get('https://api.github.com/repos/Codertocat/Hello-World/deployments?enviroment=examples/gh_dir0:tacobot_production', json=[])
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments', json={'id': '1234'})
    context.m.post('https://api.github.com/repos/Codertocat/Hello-World/deployments/1234/statuses', json={'id': '1234'})