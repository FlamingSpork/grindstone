from dataclasses import dataclass
from ..types import Payload

@dataclass
class InitialVelocity:
    initialVelocity: float

    def process(self, payload: Payload) -> None:
        payload.speed_data.speed += self.initialVelocity
