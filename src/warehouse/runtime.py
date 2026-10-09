"""A small registry for explicitly declared workflows."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Step:
    name: str
    function: Callable[[Any], Any]
    after: tuple[str, ...] = ()


@dataclass(frozen=True)
class Workflow:
    name: str
    steps: tuple[Step, ...]


class Registry:
    def __init__(self) -> None:
        self.workflows: dict[str, Workflow] = {}

    def register(self, name: str, steps: Iterable[Step]) -> Workflow:
        workflow = Workflow(name, tuple(steps))
        names = {step.name for step in workflow.steps}
        if any(set(step.after) - names for step in workflow.steps):
            raise ValueError("workflow contains an unknown dependency")
        self.workflows[name] = workflow
        return workflow
