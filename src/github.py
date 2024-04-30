import os
import requests
import time
from datetime import datetime
import json
import subprocess

token_cache = {}


class GitHub:
    def __init__(self, token: str):
        self.request_header = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

        event_path = os.getenv("GITHUB_EVENT_PATH")

        try:
            with open(event_path, 'r') as file:
                self.event = json.load(file)
        except FileNotFoundError:
            raise Exception("Event file not found")
        except json.JSONDecodeError:
            raise Exception("Could not parse event file.")

    @property
    def org(self):
        return self.event['repository']['owner']['login']

    @property
    def repo(self):
        return self.event['repository']['name']

    @property
    def sha(self):
        return self.event['pull_request']['head']['sha']
    @property
    def pull_request_number(self):
        return self.event['pull_request']['number']

    @property
    def head_branch(self):
        return self.event['pull_request']['head']['ref']

    def pull_request_files_changed(self, drift_detection):
        if drift_detection is False:
            resp = requests.get(
                f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}/files?per_page=100",
                headers=self.request_header)

            resp.raise_for_status()

            files_changed = resp.json()

            while 'next' in resp.links.keys():  # pragma: no cover
                resp = requests.get(
                    resp.links['next']['url'],
                    headers=self.request_header)
                files_changed.extend(resp.json())

            file_names = [f['filename'] for f in files_changed]
            return file_names

    def comment(self, comment):
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/issues/{self.pull_request_number}/comments",
            headers=self.request_header,
            json={
                'body': comment})
        resp.raise_for_status()

    def apply_requirements_errors(self, apply_requirements):
        errors = []

        if len(apply_requirements) == 0:
            return errors

        pr = None
        try:
            pr = self.get_pr_information()
        except Exception as e:  # pragma: no cover
            return [str(e)]

        if 'approved' in apply_requirements:
            reviews = self._get_reviews()
            has_one_approval = any(
                [review['state'] == 'APPROVED' for review in reviews])

            if not has_one_approval:
                logger.debug("Did not find at least one approval for PR")
                errors.append(
                    "Pull Request must have one approval before applying.")

        if 'mergeable' in apply_requirements:
            if pr['mergeable'] is not True:
                logger.debug("Mergeable is not True")
                errors.append(
                    f"Pull Request must be mergeable to Apply and is currently: {pr['mergeable']}")

            if pr['mergeable_state'] in [
                    'blocked', 'dirty', 'draft', 'unknown']:
                logger.debug("Mergeable state is not valid to apply")
                errors.append(
                    f"Pull Request must be in a mergeable state to apply and is currently: {pr['mergeable_state']}")

        for requirement in apply_requirements:
            if 'project:' in requirement:
                logger.debug('Found project')
                check_run_name = requirement.split('project:')[1]
                logger.debug(check_run_name)
                check_run = self._get_check_run(check_run_name)
                logger.debug(check_run)

                # If there is no change to a project requirement within the same PR
                # then there are no apply errors.
                if check_run['total_count'] == 0:
                    continue

                if check_run['check_runs'][0]['status'] != 'completed' or check_run['check_runs'][0]['conclusion'] != 'success':
                    errors.append(
                        f'Project {check_run_name} must be applied first.')

        return errors

    def get_pr_information(self):
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}",
            headers=self.request_header)
        resp.raise_for_status()

        return resp.json()

    def _get_reviews(self):
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}/reviews",
            headers=self.request_header)
        resp.raise_for_status()

        return resp.json()

    def get_check_runs_for_sha(self, sha):
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/commits/{sha}/check-runs',
            headers=self.request_header)
        resp.raise_for_status()
        check_runs = resp.json()['check_runs']

        while 'next' in resp.links.keys():  # pragma: no cover
            resp = requests.get(
                resp.links['next']['url'],
                headers=self.request_header)
            check_runs.extend(resp.json()['check_runs'])

        return check_runs

    def create_deployment(self, project):
        # TODO: create plan path uuid
        resp = requests.post(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments',
            headers=self.request_header,
            json={
                'ref': self.head_branch,
                'environment': project.name,
                'description': f'Terraform for {project.name}',
                'auto_merge': False,
                'required_contexts': [],
                'payload': {
                    'project': project.dict(),
                    'sha': self.sha,
                    'pr_number': self.pull_request_number,
                    'project_name': project.name,
                }
            }
        )

        resp.raise_for_status()
        print(f"Created deployment for {project.name}. ID: {resp.json()['id']}")
        print(resp.status_code)
        print(resp.json())
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
        print(f"Getting deployments for {project_name}")
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/deployments?enviroment={project_name}',
            headers=self.request_header
        )

        print(deployments)
        resp.raise_for_status()
        deployments = resp.json()

        if len(deployments) == 0:
            return None, False

        latest_deployment = deployments[0]
        assert 'id' in latest_deployment, "Deployment ID not found in deployment"
        assert 'payload' in latest_deployment, "Payload not found in deployment"
        assert 'pr_number' in latest_deployment['payload'], "PR Number not found in deployment payload"

        deployment_status = self.get_deployment_status(latest_deployment['id'])
        # Can be one of error, failure, inactive, in_progress, queued pending, or success
        if deployment_status is not None and deployment_status['state'] in ['queued', 'pending', 'in_progress']:
            return latest_deployment['id'], latest_deployment['payload']['pr_number'] == self.pull_request_number
        return None, False

    def get_deployment_status(self, deployment_id):
        resp = requests.get(f"https://api.github.com/repos/{self.org}/{self.repo}/deployments/{deployment_id}/statuses", headers=self.request_header)
        resp.raise_for_status()

        if len(resp.json()) == 0:
            return None
        return resp.json()[0]

    def invoke_workflow_dispatch(self, workflow, ref, inputs):
        url = f"https://api.github.com/repos/{self.org}/{self.repo}/actions/workflows/{workflow}_plan.yaml/dispatches"
        resp = requests.post(
            url,
            headers=self.request_header,
            json={
                'ref': ref,
                'inputs': inputs
            }
        )

        if resp.status_code >= 400:
            print(resp.json())
        resp.raise_for_status()
    
    def _get_check_run(self, name):
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/commits/{self.sha}/check-runs?check_name={name}'
        )
        resp.raise_for_status()

        return resp.json()