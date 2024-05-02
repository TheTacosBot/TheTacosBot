import yaml
import re
import copy
from dataclasses import dataclass, field
from typing import Optional, List
from src.configuration.tacobot.project import Project

def load_yaml(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

@dataclass
class Config:
    projects: Optional[List[Project]] = field(default_factory=list)

    @staticmethod
    def load(path):
        loaded_config = load_yaml(path)
        # Validate loaded_config if necessary, here assume it's correct
        if 'projects' in loaded_config:
            projects = [Project(**proj) for proj in loaded_config['projects']]
            return Config(projects=projects)
        return Config()

    def get_matching_project(self, project_name: str):
        """
        Returns the last project where the dir matches the regex pattern
        """
        matching_project = None
        dir, workflow = project_name.split(':')

        print(f"Search for matching project: {project_name} with workspace: {workflow} in dir: {dir}")
        for project in self.projects:
            print(f"Checking project: {project.name}")
            print(f"Project dir: {project.dir}")
            if re.compile(f'^{project.dir}$').match(dir) and project.workflow == workflow:
                matching_project = copy.deepcopy(project)
                matching_project.dir = dir
                setattr(matching_project, 'name', project_name)
        return matching_project

    def get_projects_to_run(self, list_of_changed_files):
        projects_to_run = {}
        for config_project in self.projects:
            for project in config_project.regex_projects(list_of_changed_files):
                projects_to_run[project.name] = project
        return projects_to_run