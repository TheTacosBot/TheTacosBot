import os
import subprocess
from src.github import GitHub


def drift_detection_handler(config):
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)
    files_changed = subprocess.run(
        'git ls-tree --full-tree -r --name-only HEAD',
        shell=True,
        capture_output=True,
        check=True).stdout.decode('utf-8').split('\n')

    projects_to_run = config.get_projects_to_run(files_changed)

    ref = os.getenv("GITHUB_REF")
    for _, project in projects_to_run.items():
        inputs = {
            'name': project.name,
            **project.dict(),
        }
        print(f"Invoking {project.workflow} for project: {project.name}")
        github.invoke_workflow_dispatch(project.workflow, ref, inputs)