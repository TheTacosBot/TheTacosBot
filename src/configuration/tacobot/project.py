import re
import os
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

@dataclass
class Project:
    dir: str
    workflow: str
    plan_path: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        # Add validation if necessary, for example:
        if not self.dir:
            raise ValueError("Directory cannot be empty")
        if not self.workflow:
            raise ValueError("Workflow cannot be empty")

    @property
    def name(self):
        if self.dir == '.':
            return "root"
        else:
            return f"{self.dir}:{self.workflow}"

    def regex_projects(self, files_changed: List[str]):
        projects = []
        for file in files_changed:
            if re.compile(f'^{self.dir}').match(file):
                dir = os.path.dirname(file) if os.path.dirname(file) != '' else '.'
                projects.append(Project(dir=dir, workflow=self.workflow, plan_path=self.plan_path))
        return projects