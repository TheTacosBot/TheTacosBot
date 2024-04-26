import requests_mock

def before_all(context):
    context.m = requests_mock.Mocker()

    context.m.post(
        "https://api.github.com/repos/Codertocat/Hello-World/actions/workflows/tacobot_production_plan.yaml/dispatches"
    )
    context.m.get(
        "https://api.github.com/repos/Codertocat/Hello-World/pulls/2/files?per_page=100",
        json=[{'filename': "examples/gh_dir0/main.tf"}])