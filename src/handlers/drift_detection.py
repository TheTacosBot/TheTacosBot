import os
from src.github import GitHub
from dataclasses import asdict
from src.logger import logger


def drift_detection_handler(config):
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)
    files_changed = os.environ.get("INPUT_FILES").split('|')

    projects_to_run = config.get_projects_to_run(files_changed)

    for _, project in projects_to_run.items():
        inputs = {
            'name': project.name,
            **asdict(project),
        }
        logger.info(f"Invoking {project.workflow} for project: {project.name}")
        github.invoke_workflow_dispatch(f"{project.workflow}_plan", inputs)