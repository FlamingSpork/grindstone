from dataclasses import dataclass
import numpy as np
import pandas as pd
import datetime

import math

from ..types import Payload, TimedSpeed, TimedPosition, FrameTimeData
from ..consts import Gravity

@dataclass
class GenerateSpeedsFromAccelerometer:
    def process(self, payload: Payload) -> None:
        print(f"accel={payload.accel_data.accel}")
        payload.speed_data = TimedSpeed(
            time = payload.accel_data.time,
            speed = np.cumsum(payload.accel_data.accel),
        )

@dataclass
class GeneratePositionsFromSpeed:
    def process(self, payload: Payload) -> None:
        payload.position_data = TimedPosition(
            time = payload.accel_data.time,
            pos = np.cumsum(payload.speed_data.speed),
        )

@dataclass
class GenerateTimestampsPerFrame:
    metersPerPixel: float


    def process(self, payload: Payload) -> None:
        eps = payload.camera_metadata.exposures_per_sec
        frame_count = payload.image_metadata.frames
        image_time = frame_count / eps
        image_distance = payload.position_data.pos[-1]

        # TODO pos is all zeros
        posSeries = pd.Series(
            payload.position_data.time,
            # omghax: 1 meter = 1 second
            # because resample() wants times only??
            index = pd.to_timedelta(payload.position_data.pos, unit='s'),
        )
        # TODO linear interpolation is lame
        # we should instead assume constant acceleration

        posSeries = posSeries[~posSeries.index.duplicated(keep='first')]

        print(posSeries)

        resampledPos = posSeries.resample(
            datetime.timedelta(seconds=self.metersPerPixel),
        ).interpolate(method='linear')

        payload.frame_times = FrameTimeData(time=resampledPos.to_numpy())
