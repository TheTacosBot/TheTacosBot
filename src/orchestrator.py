import re
from src.models import Conclusion, VCSStatus
from src.logger import logger
from src.constants import no_plans, message_to_pr_creator
from src.configuration.atlantis.configuration import Config
from src.configuration.formatter import Formatter
from src.comment_command import CommentCommand


class Orchestrator:
    def __init__(
            self,
            repo_location: str,
            vcs,
            lock_client=OrchestratorLocksFactory.get()):
        self.repo_location = repo_location
        self.vcs = vcs
        self.lock_client = lock_client
        self.subscription_level = self.get_org_subscription_level(self.vcs.org)

        self.config = None
        if repo_location is not None:
            self.config = Config.load(self.repo_location)
        self.client_factory = WorkerClientFactory


    def closed_pull_request(self):
        raise Exception("TODO: Implement closed_pull_request and clear locks")
        self.lock_client.unlock_for_pull_request(
            self.vcs.org, self.vcs.repo, self.vcs.pull_request_number)

    def worker_callback(self, response, original_request):
        output_manager = WorkerOutputFactory.get()
        output_manager.save(response, original_request)
        output = Formatter.markdown(response.steps)

        signed_url = output_manager.signed_url(original_request)
        log_url = f"https://logs.terrahaxs.com?load_url={signed_url}"
        if len(output) > self.vcs.max_output_text_size:
            output = f"""The output for this job is too long to display. You can view it [here]({log_url})"""

        if original_request.action == 'plan':
            actions = None

            workflow_completed_successfully = response.conclusion == Conclusion.success

            conclusion = None

            plan_step = list(
                filter(
                    lambda x: x.slug == 'terraform_plan',
                    response.steps))
            plan_had_changes = len(
                plan_step) > 0 and plan_step[0].exit_code == 2
            plan_had_no_changes = len(
                plan_step) > 0 and plan_step[0].exit_code == 0

            if workflow_completed_successfully and plan_had_changes:
                actions = [self.vcs.apply_action]

            if plan_had_changes:
                conclusion = Conclusion.success
            elif plan_had_no_changes:
                conclusion = Conclusion.success
            else:
                conclusion = Conclusion.failure
                actions = [self.vcs.plan_action]
            self.vcs.update_status(VCSStatus(
                title="Plan Output",
                text=output,
                summary='',
                conclusion=conclusion
            ), actions=actions)

        elif original_request.action == 'apply':
            if response.conclusion != Conclusion.success:
                logger.debug("Updating status for failed apply")
                actions = [self.vcs.plan_action, self.vcs.unlock_action]
                current_check_run = self.vcs.get_check_run()

                status = VCSStatus(
                    title=original_request.project_name,
                    summary="Apply Failed",
                    text=output,
                    conclusion=Conclusion.failure,
                )
                self.vcs.update_status(status, actions=actions)
            else:
                logger.debug("Updating status for success apply")
                current_check_run = self.vcs.get_check_run()

                self.lock_client.unlock(
                    org=self.vcs.org,
                    repo=self.vcs.repo,
                    pr_number=self.vcs.pull_request_number,
                    project_name=self.vcs.project_name
                )

                status = VCSStatus(
                    title="Applied Successfully!",
                    summary=f'The plan below has been applied successfully.\n\nYou can view your [deployment log](https://github.com/{original_request.org}/{original_request.repo}/deployments) and [log output]({log_url}).',
                    text=current_check_run['output']['text'],
                    conclusion=Conclusion.success)
                self.vcs.update_status(status, actions=None)
                id = self.vcs.create_deployment(original_request.project_name)
                self.vcs.update_deployment(id, log_url)


        terrahaxs_command_prefix = '^terrahaxs (plan|apply).*'
        if not re.compile(terrahaxs_command_prefix).match(
                self.vcs.user_comment):
            logger.debug(
                f'Comment {self.vcs.user_comment} was not a terrahaxs command')
            return None

        check_runs = self.vcs.get_check_runs_for_sha(self.vcs.sha)

        projects_to_run = {}
        for check_run in check_runs:
            cc = CommentCommand(self.vcs.user_comment)
            if re.compile(cc.project).match(check_run['name']):
                project = self.config.get_matching_project(check_run['name'])
                if project is not None:
                    projects_to_run[check_run['id']] = (project)

        for check_run_id, project in projects_to_run.items():
            try:
                if project.worker_hosting is not None:
                    hosting_type = project.worker_hosting.type
                    logger.debug(f"Using project hosting type {hosting_type}")
                    project.worker_hosting.validate_self_hosted_worker()
                else:
                    hosting_type = self.config.defaults.worker_hosting.type
                    logger.debug(f"Using default hosting type {hosting_type}")
                    self.config.defaults.worker_hosting.validate_self_hosted_worker()

                logger.info("Creating pending check run")

                plan_path = f"{self.vcs.name}/{self.vcs.org}/{self.vcs.repo}/{project.name}/{self.vcs.sha}"
                worker_invoker = self.client_factory.get_client(
                    subscription_level=self.subscription_level,
                    hosting_type=hosting_type,
                    config=self.config,
                    project=project,
                    vcs=self.vcs,
                    check_run_id=check_run_id,
                    plan_path=plan_path)
                worker_invoker.invoke()
            except VCSException as e:
                self.vcs.quick_status(
                    name=e.name,
                    conclusion=e.conclusion,
                    title=e.title,
                    summary=e.summary,
                    text=e.text
                )
                continue