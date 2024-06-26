import os
import requests
import json
from dataclasses import asdict
from src.logger import logger
from src.custom_exceptions import TooManyDispatchKeysError, TriggerWorkflowError, RetrieveChangedFilesError

token_cache = {}


class GitHub:
    def __init__(self, token: str):
        self.request_header = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

        event_path = os.getenv("GITHUB_EVENT_PATH")

        with open(event_path, 'r') as file:
            self.event = json.load(file)


    @property
    def org(self):
        return self.event['repository']['owner']['login']

    @property
    def repo(self):
        return self.event['repository']['name']

    @property
    def action(self):
        return self.event['action']

    @property
    def sha(self):
        return self.event['pull_request']['head']['sha']
    @property
    def pull_request_number(self):
        if 'pull_request' in self.event:
            return self.event['pull_request']['number']

    @property
    def head_branch(self):
        return self.event['pull_request']['head']['ref']

    def pull_request_files_changed(self):
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}/files?per_page=100",
            headers=self.request_header)

        try:
            resp.raise_for_status()
        except Exception as e:
            raise RetrieveChangedFilesError(f"Failed to retrieve changed files: {e}")

        files_changed = resp.json()

        while 'next' in resp.links.keys():  # pragma: no cover
            resp = requests.get(
                resp.links['next']['url'],
                headers=self.request_header)
            files_changed.extend(resp.json())

        file_names = [f['filename'] for f in files_changed]
        return file_names

    def create_locked_status_check(self, context, pr_number):
        resp = requests.post(
            f'https://api.github.com/repos/{self.org}/{self.repo}/statuses/{self.sha}',
            headers=self.request_header,
            json={
                'state': 'error',
                'description': 'TheTacosBot is currently running a plan for this PR. Please wait for it to complete.',
                'target_url': f"https://github.com/{self.org}/{self.repo}/pull/{pr_number}",
                'context': context
            }
        )

        resp.raise_for_status()
    def create_deployment(self, project, head_branch=None, sha=None, pr_number=None):
        resp = requests.post(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments',
            headers=self.request_header,
            json={
                'task': 'plan',
                'ref': self.head_branch if head_branch is None else head_branch,
                'environment': project.name,
                'description': f'Terraform for {project.name}',
                'auto_merge': os.getenv('AUTO_MERGE', 'false') == 'true',
                'required_contexts': [],
                'payload': {
                    'project': asdict(project),
                    'sha': self.sha if sha is None else sha,
                    'pr_number': self.pull_request_number if pr_number is None else pr_number,
                    'project_name': project.name,
                }
            }
        )

        resp.raise_for_status()
        print(f"Created deployment for {project.name}. ID: {resp.json()['id']}")
        return resp.json()['id']
    
    def delete_deployment(self, deployment_id):
        resp = requests.delete(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments/{deployment_id}',
            headers=self.request_header
        )
        resp.raise_for_status()

    def update_deployment_status(self, deployment_id, state, description):
        requests.post(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments/{deployment_id}/statuses',
            headers=self.request_header,
            json={
                'state': state,
                'description': description,
            }
        )

    def project_has_pending_deployment(self, project_name):
        logger.debug(f"Getting deployments for {project_name}")
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments?environment={project_name}',
            headers=self.request_header
        )

        resp.raise_for_status()
        deployments = resp.json()

        if len(deployments) == 0:
            return None, 0

        latest_deployment = deployments[0]
        assert 'id' in latest_deployment, "Deployment ID not found in deployment"
        assert 'payload' in latest_deployment, "Payload not found in deployment"
        assert 'pr_number' in latest_deployment['payload'], "PR Number not found in deployment payload"

        deployment_status = self.get_deployment_status(latest_deployment['id'])
        # Can be one of error, failure, inactive, in_progress, queued pending, or success
        if deployment_status is not None and deployment_status['state'] in ['queued', 'pending', 'in_progress']:
            return latest_deployment['id'], latest_deployment['payload']['pr_number']
        return None, 0

    def get_deployment_status(self, deployment_id):
        resp = requests.get(f"https://api.github.com/repos/{self.org}/{self.repo}/deployments/{deployment_id}/statuses", headers=self.request_header)
        resp.raise_for_status()

        if len(resp.json()) == 0:
            return None
        return resp.json()[0]

    def invoke_workflow_dispatch(self, event_type, inputs):
        if len(inputs.keys()) > 10:
            raise TooManyDispatchKeysError("Too many keys in the dispatch payload")

        url = f"https://api.github.com/repos/{self.org}/{self.repo}/dispatches"
        resp = requests.post(
            url,
            headers=self.request_header,
            json={
                'event_type': event_type,
                'client_payload': inputs
            }
        )

        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to trigger the workflow: {e}")
            raise TriggerWorkflowError(f"Failed to trigger the workflow: {e}")

    def get_pr_information(self):
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}",
            headers=self.request_header
        )

        resp.raise_for_status()
        return resp.json()
    
    def clear_deployments(self):
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/deployments?sha={self.sha}",
            headers=self.request_header
        )

        resp.raise_for_status()
        deployments = resp.json()
        for deployment in deployments:
            status = self.get_deployment_status(deployment['id'])

            if status is not None and status['state'] in ['queued', 'pending', 'in_progress']:
                self.delete_deployment(deployment['id'])
                logger.info(f"Deleted deployment {deployment['id']}")