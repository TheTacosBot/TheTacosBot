import os
import argparse
from dataclasses import asdict
from src.github import GitHub
from src.custom_exceptions import CommentNotFoundError, ProjectLockedError
from src.logger import logger
from src.handlers.locking import handle_locks

def comment_handler(config):
    """
    Handles comments on pull requests to trigger specific project workflows based on the commands provided in the comment.

    Args:
        config (Config): The configuration object containing project rules and paths.

    Raises:
        AssertionError: If the expected environment variables or command prefixes are missing.
    """

    if 'INPUT_COMMENT' not in os.environ:
        raise CommentNotFoundError
    
    comment = os.environ.get("INPUT_COMMENT")
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)

    if not comment.lower().startswith('tacosbot'):
        logger.info("Skipping comment, it does not contain a tacosbot command")
        return

    parser = argparse.ArgumentParser(prog='tacosbot', description='TacosBot command line interface.')

    # Create a subparser object
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Subparser for the 'apply' command
    apply_parser = subparsers.add_parser('apply', help='Apply changes to a project')
    apply_parser.add_argument('--project', required=True, help='Project name to apply changes to')

    # Subparser for the 'unlock' command
    unlock_parser = subparsers.add_parser('unlock', help='Unlock a project')
    unlock_parser.add_argument('--project', required=True, help='Project name to unlock')

    # Subparser for the 'plan' command
    plan_parser = subparsers.add_parser('plan', help='Plan changes for a project')
    plan_parser.add_argument('--project', required=True, help='Project name to plan changes for')

    args = parser.parse_args(comment.replace('tacosbot ', '').split())

    if args.command == 'apply':
        (project, workflow) = args.project.split(":")
        logger.info(f"Applying changes to project: {args.project}")
        github.invoke_workflow_dispatch(workflow, {'project_name': args.project})
    elif args.command == 'unlock':
        logger.info(f"Unlocking project: {args.project}")
        (deployment, _) = github.project_has_pending_deployment(args.project)
        github.delete_deployment(deployment_id=deployment)
    elif args.command == 'plan':
        logger.info(f"Planning changes for project: {args.project}")
        project = config.get_matching_project(args.project)
        logger.info(f"Matching project: {project}")

        pull_request_info = github.get_pr_information()

        try:
            handle_locks(project.name, github)
        except ProjectLockedError as e:
            logger.info(f"Project {project.name} is locked. Skipping.")
            return

        deployment_id = github.create_deployment(
            project,
            head_branch=pull_request_info['head']['ref'],
            sha=pull_request_info['head']['sha'],
            pr_number=github.pull_request_number
        )
        github.update_deployment_status(deployment_id, 'pending', f'Creating deployment for {project.name}')
        inputs = {
            'name': project.name,
            'sha': pull_request_info['head']['sha'],
            **asdict(project),
        }

        github.invoke_workflow_dispatch(project.workflow, inputs)