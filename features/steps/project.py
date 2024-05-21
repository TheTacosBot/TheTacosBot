from behave import given, when, then
from src.configuration.tacobot.project import Project

@given('a project without a directory')
def step_impl(context):
    try:
        context.project = Project(workflow='tacosbot_production')
    except Exception as e:
        context.exception = e

@given('a project without a workflow')
def step_impl(context):
    try:
        context.project = Project(dir='gh_dir0')
    except Exception as e:
        context.exception = e