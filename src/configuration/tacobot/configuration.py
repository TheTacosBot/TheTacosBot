import yaml
import re
import copy
from pydantic import BaseModel, ValidationError, Field
from typing import Optional, List
from src.configuration.tacobot.project import Project


class Config(BaseModel):
    projects: Optional[List[Project]] = Field(
        [],
        description="Lists the projects in this repo.",
    )

    @staticmethod
    def load(path):
        try:
            loaded_config = None

            with open(path) as stream:
                loaded_config = yaml.safe_load(stream)

            config = Config(**loaded_config)
            return config

        except ValidationError as e:
            raise Exception("Invalid configuration")

    def get_matching_project(self, project_name):
        """
        Returns the last project where the dir matches the regex pattern
        """
        matching_project = None

        if '/' in project_name:
            # NOTE: the project name replaces `/` with `-` to eliminate confusion
            # between what is part of the project path and the workspace.
            # To improve this project name should probably use `|` to delineate the
            # dir from the workspace
            dir = project_name.split('/')[0].replace('-', '/')
            workspace = project_name.split('/')[1]
        else:
            dir = '.'
            workspace = project_name

        for project in self.projects:
            if re.compile(f'^{project.dir}$').match(
                    dir) and project.workspace == workspace:
                # NOTE: it is VERY important to deepcopy the project here
                # so the original configuration is not modified
                matching_project = copy.deepcopy(project)
                matching_project.dir = dir
                matching_project.name = project_name
        return matching_project

    def get_projects_to_run(self, list_of_changed_files):
        # NOTE: we want to build a list of projects that we are going to execute.
        # Because we support regular expressions for directory matching a project
        # could be triggered twice, with different configurations, in the same
        # PR.
        # To solve this problem we use a last one in wins approach.
        projects_to_run = {}
        for config_project in self.projects:
            for project in config_project.regex_projects(
                    list_of_changed_files):
                projects_to_run[project.name] = project
        return projects_to_run