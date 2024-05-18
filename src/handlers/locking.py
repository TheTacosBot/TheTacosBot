from src.logger import logger
from src.custom_exceptions import ProjectLockedError

def handle_locks(project_name, github):
    (deployment_id, blocking_pr) = github.project_has_pending_deployment(project_name)

    if deployment_id is not None and blocking_pr != github.pull_request_number:
        logger.info(f"Found previously existing deployment for {project_name} associated with a different pull request. Skipping.")
        logger.info(f"Deployment ID: {deployment_id}")
        github.create_locked_status_check(project_name, blocking_pr)
        raise ProjectLockedError()
    
    # We need to replace the existing deployment with a new one since the
    # sha and information changes.
    if deployment_id is not None and blocking_pr == github.pull_request_number:
        logger.info(f"Found previously existing deployment with ID {deployment_id} for this PR. Removing it.")
        github.delete_deployment(deployment_id)