from typing import List, Protocol, TypeVar
from dataclasses import dataclass
from .types import Payload

class PipelineStage:
    def process(self, payload: Payload) -> None:
        pass


@dataclass
class Pipeline:
    stages: List[PipelineStage]

    def run(self) -> None:
        payload = Payload()
        for stage in self.stages:
            print(f"entering {stage}")
            stage.process(payload)
