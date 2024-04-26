from src.logger import logger
from src.github import GitHub
import requests

def pull_request_handler(config):
    github = GitHub()
    files_changed = github.pull_request_files_changed(False)
    logger.debug(f"Changed files: {files_changed}")


    projects_to_run = config.get_projects_to_run(files_changed)

    # TODO: how to notify user if no projects have changed

    # Iterate over the projects and execute them
    for _, project in projects_to_run.items():
        logger.debug("Invoking GitHub action")
        url = f"https://api.github.com/repos/{self.vcs.org}/{self.vcs.repo}/actions/workflows/{project.workflow}_plan.yaml/dispatches"
        logger.debug(url)
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

        resp.raise_for_status()