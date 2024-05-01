import os
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
        (deployment_id, is_this_pr) = github.project_has_pending_deployment(project.name)

        if deployment_id is not None and not is_this_pr:
            print(f"Found previously existing deployment for {project.name} associated with a different pull request. Skipping.")
            print(f"Deployment ID: {deployment_id}")
            continue
        
        # We need to replace the existing deployment with a new one since the
        # sha and information changes.
        if deployment_id is not None and is_this_pr:
            print(f"Found previously existing deployment with ID {deployment_id} for this PR. Removing it.")
            github.delete_deployment(deployment_id)
    
        inputs = {
            'name': project.name,
            **project.dict(),
        }
        print(f"Creating Deployment for {project.name}")
        deployment_id = github.create_deployment(project)
        github.update_deployment_status(deployment_id, 'pending', f'Creating deployment for {project.name}')
        print(f"Invoking {project.workflow} for project: {project.name}")
        github.invoke_workflow_dispatch(project.workflow, github.head_branch, inputs)