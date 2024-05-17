import os
from dataclasses import asdict
from src.github import GitHub
from src.logger import logger
from src.custom_exceptions import GitHubTokenNotFoundError
from src.configuration.tacobot.configuration import Config


def pull_request_handler(config: Config):
    """
    Handles pull request events by determining which projects are affected and managing their deployments.

    Args:
        config (Config): The configuration object containing project rules and paths.

    This function checks which files have been changed in the pull request, identifies the affected projects, and manages deployments and workflow invocations based on the current state of deployments associated with those projects.
    """
    token = os.environ.get("INPUT_GITHUB_TOKEN")

    if token is None:
        raise GitHubTokenNotFoundError
    
    github = GitHub(token)

    try:
        files_changed = github.pull_request_files_changed()
    except Exception as e:
        print(f"Failed to retrieve files changed due to: {e}")
        raise e

    projects_to_run = config.get_projects_to_run(files_changed)
    logger.debug(f"Projects to run: {projects_to_run}")

    # TODO: add ability to trigger plans for modules (i.e. atlantis autoplan feature)
    # Iterate over the projects and execute them
    for _, project in projects_to_run.items():
        (deployment_id, blocking_pr) = github.project_has_pending_deployment(project.name)

        if deployment_id is not None and blocking_pr != github.pull_request_number:
            logger.info(f"Found previously existing deployment for {project.name} associated with a different pull request. Skipping.")
            logger.info(f"Deployment ID: {deployment_id}")
            github.create_locked_status_check(project.name, blocking_pr)
            continue
        
        # We need to replace the existing deployment with a new one since the
        # sha and information changes.
        if deployment_id is not None and blocking_pr == github.pull_request_number:
            logger.info(f"Found previously existing deployment with ID {deployment_id} for this PR. Removing it.")
            github.delete_deployment(deployment_id)
    
        inputs = {
            'name': project.name,
            'sha': github.sha,
            **asdict(project),
        }

        # We use github deployments to keep track of projects that are "locked"
        # or in the process of being planned. Here we create the deployment
        # and update the status
        logger.info(f"Creating Deployment for {project.name}")
        deployment_id = github.create_deployment(project)
        github.update_deployment_status(deployment_id, 'pending', f'Creating deployment for {project.name}')

        # Invoke the github action workflow for this project.
        logger.info(f"Invoking {project.workflow} for project: {project.name}")
        github.invoke_workflow_dispatch(f"{project.workflow}_plan", github.head_branch, inputs)