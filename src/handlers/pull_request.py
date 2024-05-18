import os
from dataclasses import asdict
from src.github import GitHub
from src.logger import logger
from src.configuration.tacobot.configuration import Config
from src.handlers.locking import handle_locks
from src.custom_exceptions import ProjectLockedError


def pull_request_handler(config: Config):
    """
    Handles pull request events by determining which projects are affected and managing their deployments.

    Args:
        config (Config): The configuration object containing project rules and paths.

    This function checks which files have been changed in the pull request, identifies the affected projects, and manages deployments and workflow invocations based on the current state of deployments associated with those projects.
    """
    token = os.environ.get("INPUT_GITHUB_TOKEN")

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
        try:
            handle_locks(project.name, github)
        except ProjectLockedError as e:
            logger.info(f"Project {project.name} is locked. Skipping.")
            continue
    
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