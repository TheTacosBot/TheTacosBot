import os
import requests
from src.github import GitHub


def pull_request_handler(config):
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)
    files_changed = github.pull_request_files_changed(False)

    projects_to_run = config.get_projects_to_run(files_changed)

    # TODO: how to notify user if no projects have changed

    # TODO: add ability to trigger plans for modules (i.e. atlantis autoplan feature)
    # Iterate over the projects and execute them
    for _, project in projects_to_run.items():

        if not github.project_has_pending_deployment(project.name):
            inputs = {
                'name': project.name,
                **project.dict(),
            }
            deployment_id = github.create_deployment(project)
            github.update_deployment_status(deployment_id, 'pending', f'Creating deployment for {project.name}')
            github.invoke_workflow_dispatch(project.workflow, github.head_branch, inputs)
        else:
            print(f'Project {project.name} has a pending deployment. Skipping...')