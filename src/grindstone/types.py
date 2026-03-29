from dataclasses import dataclass
import numpy as np
import numpy.typing as npt
from typing import Protocol


@dataclass
class RawTimed3DIMU:
    # quick load from stringz
    # contains a bunch of quasi-parsed lines
    # such that, if time[i][0] == 'A',
    # then [xyz]accel[i] is a valid sample
    time: np.array[npt.str_]
    xaccel: np.array[npt.str_]
    yaccel: np.array[npt.str_]
    zaccel: np.array[npt.str_]

@dataclass
class Timed1DIMU:
    # (seconds since capture start)
    time: np.array[npt.float_]
    accel: np.array[npt.float_] # in G

@dataclass
class TimedSpeed:
    time: np.array[npt.float_]
    speed: np.array[npt.float_]

@dataclass
class TimedPosition:
    # position 0 = capture start
    time: np.array[npt.float_]
    pos: np.array[npt.float_]

@dataclass
class CameraMetadata:
    width: int
    exposures_per_sec: float

@dataclass
class ImageMetadata:
    frames: int

@dataclass
class FrameTimeData:
    time: np.array[npt.float_]

@dataclass
class RMCData:
    time: np.array[npt.float_]
    latitude: np.array[npt.float_]
    longitude: np.array[npt.float_]
    speed: np.array[npt.float_]

    # direction of travel (NOT heading)
    track: np.array[npt.float_]
    mode: np.array[npt.int_]


    MODE_AUTO = 0
    MODE_DIFF = 1
    MODE_EST = 2
    MODE_MANUAL = 3
    MODE_INVALID = 4

    pass

class AccumStrategy(Protocol):
    def process(self, slice: GreyscaleImage) -> None:
        pass

type GreyscaleImage = np.ndarray[tuple[int, int], np.uint8]
type GreyscaleSlice = np.array[np.uint8]

# (big fat union class we build up over the pipeline)
class Payload:
    # type checking here is kind of just a
    # Keep Track Of What I'm Doing kinda thing
    # because using a big fat union class like this
    # where everything's optional isn't very Type-y
    #
    # but it's nice to be able to refer somewhere
    # and figure out what the heck this field is
    raw: Optional[RawTimed3DIMU]

    # all _data fields should have (time, value) sub-arrays
    accel_data: Optional[Timed1DIMU]
    speed_data: Optional[TimedSpeed]

    gps_data: Optional[RMCData]

    raw_metadata: Optional[Dict[str, Any]]
    camera_metadata: Optional[CameraMetadata]
    image_metadata: Optional[ImageMetadata]
    # TODO process GPS data


    # sample index -> {positions, times}
    position_data: Optional[TimedPosition]

    # col in final image -> time since capture start (seconds/float)
    frame_times: Optional[FrameTimeData]

    # input image
    image_greyscale: Optional[GreyscaleImage]
