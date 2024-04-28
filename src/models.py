from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Lock(BaseModel):
    start_at: str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    pull_request_number: int


class ActionEnum(str, Enum):
    apply = 'apply'
    plan = 'plan'
    unlock = 'unlock'
    drift_detection = 'drift_detection'
