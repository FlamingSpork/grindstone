from dataclasses import dataclass
from ..pipeline import PipelineStage
from ..types import Payload, Timed1DIMU
import numpy as np

@dataclass
class DirectoryStringData:
    argdir: AccelDirection
    calibration: List[float]
    gravity: float

    def process(self, payload: Payload) -> None:
        data = payload.raw


        i = self.argdir.zeroXoneYtwoZ()
        accel = [data.xaccel, data.yaccel, data.zaccel][i].astype(float)
        if (self.argdir.isNegative()):
            accel = -1 * accel


        # filter the arrays to contain only valid accelerometer data
        # use mask array to look for first-character == 'A'
        isA = np.strings.slice(data.time, 0, 1) == b'A'

        accel = accel[isA]
        time = data.time[isA]
        time = np.strings.slice(data.time, 1, 32).astype(float)

        time = time - time[0]

        # before this key existed, everything was milliseconds
        if "serial.TimeUnit" in payload.raw_metadata:
            if payload.raw_metadata["serial.TimeUnit"] == "microsecond":
                print("time unit is microseconds")
                time = time / 1000.0

        payload.accel_data = Timed1DIMU(time=time, accel=accel)
