import re
import glob
import os
from pydantic import BaseModel, Field

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
            return f"{self.dir.replace('/', '-')}:{self.workflow.replace('/', '-')}"

    def regex_projects(self, files_changed):
        projects = []
        for file in files_changed:
            if re.compile(f'^{self.dir}').match(file) is not None:
                dir = os.path.dirname(file) if os.path.dirname(file) != '' else '.'
                d = self.dict(exclude={'name'}) | {'dir': dir}
                p = Project(**d)
                projects.append(p)
        return projects