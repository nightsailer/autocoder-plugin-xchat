# -*- coding:utf-8 -*-
from pydantic import BaseModel
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Task(BaseModel):
    """Task model for the codebook"""

    name: str
    command: str
    content: str
    args: str
    output: str
    status: TaskStatus
    duration: float
    token_usage: dict[str, int]

    def __init__(self, **data):
        super().__init__(**data)
        self.status = TaskStatus.PENDING
        self.duration = 0
        self.token_usage = {}
