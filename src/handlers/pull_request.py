import os
import requests
from src.github import GitHub


def pull_request_handler(config):
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)
    files_changed = github.pull_request_files_changed(False)

    projects_to_run = config.get_projects_to_run(files_changed)

    # TODO: how to notify user if no projects have changed

    # TODO: create a deployment for each project and check if a deployment "lock" already exists
    # if so, don't create a new deployment

    # TODO: add ability to trigger plans for modules (i.e. atlantis autoplan feature)
    # Iterate over the projects and execute them
    for _, project in projects_to_run.items():
        url = f"https://api.github.com/repos/{github.org}/{github.repo}/actions/workflows/{project.workflow}_plan.yaml/dispatches"
        resp = requests.post(
            url,
            headers=github.request_header,
            json={
                'ref': github.head_branch,
                'inputs': {
                    'name': project.name,
                    **project.dict(),
                }
            }
        )

        if resp.status_code >= 400:
            print(resp.json())
        resp.raise_for_status()
