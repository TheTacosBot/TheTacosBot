from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
from src.logger import logger


class LockAlreadyExists(Exception):
    def __init__(self, org, repo, project_name, pr_number):
        logger.debug(
            f"A lock already exists on {org}/{repo} for {project_name} and {pr_number}")


class Lock(BaseModel):
    start_at: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    pull_request_number: int


class ActionEnum(str, Enum):
    apply = 'apply'
    plan = 'plan'
    unlock = 'unlock'
    drift_detection = 'drift_detection'
