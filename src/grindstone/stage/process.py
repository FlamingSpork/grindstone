from dataclasses import dataclass
import numpy as np

from ..types import Payload, TimedSpeed, TimedPosition, FrameTimeData

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
        time = payload.accel_data.time
        # (delta-time)
        dt = np.diff(time, prepend=time[0])
        payload.position_data = TimedPosition(
            time=time,
            pos=np.cumsum(payload.speed_data.speed * dt),
        )

@dataclass
class GenerateTimestampsPerFrame:
    metersPerPixel: float

    def process(self, payload: Payload) -> None:
        pos = payload.position_data.pos
        time = payload.position_data.time

        # if the acceleration is shaky, a given position (and thus index) may be less than the previous one,
        # resulting in the wrong line (or burst of lines depending on how long the positions are wrong for) being placed
        # in the output image, looking almost like a barcode
        # because of how we're using position as the index, I don't know how we'd even go about fixing it
        # so far, this has only happened in one capture (05-29_14-41), so I'm inclined not to fix it unless it happens again
        monotonic = np.concatenate([[True], np.diff(pos) > 0])
        count = (~monotonic).sum()
        if count > 0:
            print(f"wrong-way position samples dropped: {count}")
        pos = pos[monotonic]
        time = time[monotonic]

        # (clamp to actual sample length)
        max_time = (payload.image_metadata.frames - 1) / payload.camera_metadata.exposures_per_sec

        # For each output `p` at spatial position `p * metersPerPixel`,
        # interpolate a camera timestamp
        n_pixels = int(pos[-1] / self.metersPerPixel)
        desired = np.arange(n_pixels) * self.metersPerPixel
        timestamps = np.interp(desired, pos, time)

        payload.frame_times = FrameTimeData(time=timestamps[timestamps <= max_time])
