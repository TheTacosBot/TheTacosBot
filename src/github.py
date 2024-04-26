import hashlib
from hmac import HMAC
import os
import requests
import time
from datetime import datetime
import subprocess
from src.settings import settings
from src.logger import logger
from src.models import WorkerRequest, VCSStatus
from src.comment_command import CommentCommand

token_cache = {}

class GitHubVCS:
    name = 'github'
    max_output_text_size = 65535

    apply_action = {
        'label': 'Apply',
        'identifier': 'apply',
        'description': 'Apply this plan.'
    }

    plan_action = {
        'label': 'Plan',
        'identifier': 'plan',
        'description': 'Re-plan this project.'
    }

    unlock_action = {
        'label': 'Unlock',
        'identifier': 'unlock',
        'description': 'Unlock this project.'
    }

    def __init__(self, event_body: dict, event: str):
        self.event_body = event_body
        self.event = event

    @staticmethod
    def from_worker_request(request: WorkerRequest):
        # model after PR
        return GitHubVCS(
            event_body={
                'check_run': {
                    'id': request.check_run_id,
                    'name': request.project_name
                },
                'pull_request': {
                    'number': request.pull_request_number,
                    'branch': request.branch,
                    'head': {
                        'sha': request.head_sha,
                        'ref': request.branch
                    }
                },
                'repository': {
                    'name': request.repo,
                    'owner': {
                        'login': request.org
                    }
                },
                'installation': {
                    'id': request.installation_id
                }
            },
            event='pull_request'
        )

    def validate_request(self, header_signature, byte_body):
        signature = GitHubVCS.generate_signature_from_body(byte_body)

        return signature == header_signature

    @property
    def action(self):
        if self.event == 'pull_request':
            return 'plan'
        elif self.event == 'check_run':
            return self.event_body['requested_action']['identifier'] # Identifier should be plan, apply, or unlock
        elif self.event == 'issue_comment':
            cc = CommentCommand(self.user_comment)
            return cc.action


    @property
    def org(self):
        return self.event_body['repository']['owner']['login']

    @property
    def repo(self):
        return self.event_body['repository']['name']

    @property
    def sha(self):
        try:
            return self.event_body['pull_request']['head']['sha']
        except KeyError:
            return self.event_body['check_run']['pull_requests'][0]['head']['sha']

    @property
    def head_branch(self):
        try:
            return self.event_body['pull_request']['head']['ref']
        except KeyError:
            return self.event_body['check_run']['pull_requests'][0]['head']['ref']

    @property
    def base_branch(self):
        try:
            return self.event_body['pull_request']['base']['ref']
        except KeyError:
            return self.event_body['check_run']['pull_requests'][0]['base']['ref']

    @property
    def pull_request_number(self):
        if self.event == 'pull_request':
            return self.event_body['pull_request']['number']
        elif self.event == 'check_run':
            return self.event_body['check_run']['pull_requests'][0]['number']
        elif self.event == 'issue_comment':
            return self.event_body['issue']['number']
        else: # pragma: no cover
            raise Exception('Cloud not return pull request number')

    @property
    def installation_id(self):
        return self.event_body['installation']['id']

    @property
    def project_name(self):
        return self.event_body['check_run']['name']

    @property
    def author(self):
        if self.event == 'pull_request':
            return self.event_body['pull_request']['user']['login']
        elif self.event == 'check_run': # pragma: no cover
            return self.event_body['check_run']['sender']['login']
        else: # pragma: no cover
            raise Exception('Could not return author')
            
    @property
    def check_run_id(self):
        return self.event_body['check_run']['id']
        
    @property
    def user_comment(self):
        return self.event_body['comment']['body']

    @property
    def clone_url(self):
        return f"https://github.com/{self.org}/{self.repo}.git"

    @property
    def request_header(self):
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }

    def get_token(self):
        return os.getenv('GITHUB_TOKEN')

    def pending_plan_status(self, project_name):
        logger.debug("Creating pending plan status")
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/check-runs",
            headers=self.request_header,
            json={
                "name": project_name,
                "head_sha": self.sha,
                "status": "in_progress",
                "started_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "output": {
                    "title": "Planning in Progress",
                    "summary": "",
                    "text": ""
                }
            }
        )

        resp.raise_for_status()
        return resp.json()['id']

    def update_status(self, status: VCSStatus, actions=None):
        payload = {
            "completed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "completed",
            "conclusion": status.conclusion,
            "output": {
                "title": status.title,
                "summary": status.summary,
                "text": status.text
            }
        }

        if actions is not None:
            payload['actions'] = actions

        logger.debug(f"Updating status https://api.github.com/repos/{self.org}/{self.repo}/check-runs/{self.check_run_id}")
        resp = requests.patch(
            f"https://api.github.com/repos/{self.org}/{self.repo}/check-runs/{self.check_run_id}",
            headers=self.request_header,
            json=payload
        )

        resp.raise_for_status()

    def get_check_run(self):
        logger.debug(f"Getting check run https://api.github.com/repos/{self.org}/{self.repo}/check-runs/{self.check_run_id}")
        resp = requests.get(f"https://api.github.com/repos/{self.org}/{self.repo}/check-runs/{self.check_run_id}", headers=self.request_header)

        resp.raise_for_status()
        return resp.json()

    def create_deployment(self, project_name):
        logger.debug("Creating deployment")
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/deployments",
            json={'ref': self.sha, 'task': 'apply', 'auto_merge': False, 'required_contexts': [], 'environment': project_name},
            headers=self.request_header)
        resp.raise_for_status()
        return resp.json()['id']

    def update_deployment(self, deployment_id, log_url):
        logger.debug("Updating deployment")
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/deployments/{deployment_id}/statuses",
            json={'state': 'success', 'log_url': log_url},
            headers=self.request_header)
        resp.raise_for_status()
        return resp.json()['id']


    def pull_request_files_changed(self, drift_detection):
        logger.debug("Getting pull request changed files")
        if drift_detection is False:
            resp = requests.get(f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}/files?per_page=100", headers=self.request_header)

            resp.raise_for_status()

            files_changed = resp.json()

            while 'next' in resp.links.keys(): # pragma: no cover
                logger.debug("Making another request for changed files")
                resp = requests.get(resp.links['next']['url'], headers=self.request_header)
                files_changed.extend(resp.json())

            file_names = [f['filename'] for f in files_changed]
            return file_names
        else: # pragma: no cover
            files = subprocess.run(
                'git ls-tree --full-tree -r --name-only HEAD',
                shell=True,
                capture_output=True,
                cwd=self.repo_location,
                check=True).stdout.decode('utf-8').split('\n')
            return files


    def quick_status(self, name, conclusion, title, summary, text):
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/check-runs",
            headers=self.request_header,
            json={
                "name": name,
                "head_sha": self.sha,
                "status": "completed",
                "conclusion": conclusion,
                "started_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "completed_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "output": {
                    "title": title,
                    "summary": summary,
                    "text": text
                }
            }
        )

        resp.raise_for_status()
        return resp.json()

    def comment(self, comment):
        resp = requests.post(
            f"https://api.github.com/repos/{self.org}/{self.repo}/issues/{self.pull_request_number}/comments",
            headers=self.request_header,
            json={'body': comment}

        )
        resp.raise_for_status()

    def apply_requirements_errors(self, apply_requirements):
        errors = []

        if len(apply_requirements) == 0:
            return errors

        pr = None
        try:
            pr = self.get_pr_information()
        except Exception as e: # pragma: no cover
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

            if pr['mergeable_state'] in ['blocked', 'dirty', 'draft', 'unknown']:
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
                    errors.append(f'Project {check_run_name} must be applied first.')

        return errors

    def get_pr_information(self):
        logger.debug(f"Getting pull request information {self.org}/{self.repo}/pulls/{self.pull_request_number}")
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}",
            headers=self.request_header
        )
        resp.raise_for_status()

        return resp.json()

    def _get_reviews(self):
        logger.debug("Getting pull request reviews")
        resp = requests.get(
            f"https://api.github.com/repos/{self.org}/{self.repo}/pulls/{self.pull_request_number}/reviews",
            headers=self.request_header
        )
        resp.raise_for_status()

        return resp.json()

    def get_check_runs_for_sha(self, sha):
        logger.debug(f'Getting check runs for https://api.github.com/repos/{self.org}/{self.repo}/commits/{sha}/check-runs')
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/commits/{sha}/check-runs',
            headers=self.request_header
        )
        resp.raise_for_status()
        check_runs =  resp.json()['check_runs']

        while 'next' in resp.links.keys(): # pragma: no cover
            logger.debug("Making another request for check runs")
            resp = requests.get(resp.links['next']['url'], headers=self.request_header)
            check_runs.extend(resp.json()['check_runs'])

        return check_runs

    def _get_check_run(self, name):
        logger.debug(f'Getting check runs for https://api.github.com/repos/{self.org}/{self.repo}/commits/{self.sha}/check-runs?check_name={name}')
        resp = requests.get(
            f'https://api.github.com/repos/{self.org}/{self.repo}/commits/{self.sha}/check-runs?check_name={name}'
        )
        resp.raise_for_status()

        return resp.json()

def is_token_expired(installation_id):
    org_token = token_cache[installation_id]

    return org_token['expires'] < int(time.time())