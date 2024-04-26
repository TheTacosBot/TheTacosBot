import re
import glob
import os
from pydantic import BaseModel, Field
from src.logger import logger

class Project(BaseModel):
    dir: str = Field(
        ...,
        description="The directory this project relative to the repo root. For example if the project was under `./project1` then use `project1`. Use `.` to indicate the repo root. This can also be a regular expression to capture multiple projects. Note `^` is prepended to every regular expression."
    )

    workflow: str = Field(
        ...,
        description="The name of the GitHub Action workflow to run for this project."
    )

    @property
    def name(self):
        if self.dir == '.':
            return "root"
        else:
            return f"{self.dir.replace('/', '-')}/{self.workflow.replace('/', '-')}"

    def regex_projects(self, files_changed):
        projects = []
        for file in files_changed:
            if re.compile(f'^{self.dir}').match(file) is not None:
                dir = os.path.dirname(file) if os.path.dirname(file) != '' else '.'
                d = self.dict(exclude={'name'}) | {'dir': dir}
                p = Project(**d)
                projects.append(p)
        return projects

    def should_plan(self, files_changed, repo_location, drift_detection):
        if drift_detection is True:
            return self.drift_detection_enabled

        return self.autoplan.enabled is True and self._has_changed_files(files_changed, repo_location)

    def _has_changed_files(self, files_changed, repo_location):
        watched_files = self._files_matching_glob_expression(repo_location)
        watched_files_changed = [file for file in files_changed if file in watched_files]
        logger.debug(watched_files_changed)
        return len(watched_files_changed) > 0

    def _files_matching_glob_expression(self, repo_location):
        files = []
        for glob_pattern in self.autoplan.when_modified:
            files += glob.glob(pathname=f"{repo_location}/{self.dir}/{glob_pattern}",
                            recursive=True)

        return [file.replace(f"{repo_location}/", "").replace("./", "") for file in files]