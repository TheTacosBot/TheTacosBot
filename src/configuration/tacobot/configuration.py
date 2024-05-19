import yaml
import re
import copy
from dataclasses import dataclass, field
from typing import Optional, List
from src.configuration.tacobot.project import Project
from src.custom_exceptions import ProjectNotFoundError
from src.logger import logger

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

        logger.debug(f"Search for matching project: {project_name} with workspace: {workflow} in dir: {dir}")
        for project in self.projects:
            if re.compile(f'^{project.dir}$').match(dir) and project.workflow == workflow:
                matching_project = copy.deepcopy(project)
                matching_project.dir = dir
                project.workflow = workflow

        if matching_project is None:
            raise ProjectNotFoundError

        return matching_project

    def get_projects_to_run(self, list_of_changed_files):
        """
        Returns a dictionary of projects to run based on the list of changed files.
        """
        projects_to_run = {}
        for config_project in self.projects:
            logger.debug(f"Checking project: {config_project.name}")
            for project in config_project.regex_projects(list_of_changed_files):
                logger.debug(f"Adding project: {project.name}")
                projects_to_run[project.name] = project
        return projects_to_run