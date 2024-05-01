import os
import argparse
from src.github import GitHub

def comment_handler(config):
    assert 'INPUT_COMMENT' in os.environ, 'INPUT_COMMENT not found in environment variables'
    comment = os.environ.get("INPUT_COMMENT")
    token = os.environ.get("INPUT_GITHUB_TOKEN")
    github = GitHub(token)

    assert 'tacosbot' in comment, 'TacosBot not found in comment'
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
        print(f"Applying changes to project: {args.project}")
        github.invoke_workflow_dispatch(f"{workflow}_apply", github.default_branch, {'project_name': args.project})
    elif args.command == 'unlock':
        print(f"Unlocking project: {args.project}")
        (deployment, _) = github.project_has_pending_deployment(args.project)
        github.delete_deployment(deployment_id=deployment)
    elif args.command == 'plan':
        print(f"Planning changes for project: {args.project}")
        (project, workflow) = args.project.split(":")
        project = config.get_matching_project(project)
        inputs = {
            'name': project.name,
            **project.dict(),
        }
        github.invoke_workflow_dispatch(f"{project.workflow}_plan", github.head_branch, inputs)