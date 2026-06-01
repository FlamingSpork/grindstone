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

        # if the acceleration is shaky, a given position (and thus index) may be less than the previous one,
        # resulting in the wrong line (or burst of lines depending on how long the positions are wrong for) being placed
        # in the output image, looking almost like a barcode
        # because of how we're using position as the index, I don't know how we'd even go about fixing it
        # so far, this has only happened in one capture (05-29_14-41), so I'm inclined not to fix it unless it happens again
        lP = 0
        wrongWayCnt = 0
        for p in payload.position_data.pos:
            if p < lP:
                print(f"pos {p} < lP {lP}")
                wrongWayCnt += 1
            lP = p
        print(f"wrong way position movement samples: {wrongWayCnt}") # should be zero

        payload.frame_times = FrameTimeData(time=resampledPos.to_numpy())
