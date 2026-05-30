from dataclasses import dataclass
import numpy as np
import pandas as pd

from ..types import Payload

@dataclass
class SelectGrayscaleFramesFromTimestamps:
    accum_strategy: AccumStrategy
    distance: float

    def process(self, p: Payload):
        for ftime in p.frame_times.time:
            # locate the frame at the index
            i = int(p.camera_metadata.exposures_per_sec * ftime)
            # TODO possibly skew it to adjust for funny camera angle?

            # pass it to our image accumulator
            self.accum_strategy.accumulate(p.image_greyscale[i])

        self.accum_strategy.finalize()

@dataclass
class SelectColorFramesFromTimestamps:
    accum_strategy: AccumStrategy
    distance: float

    def process(self, p: Payload):
        for ftime in p.frame_times.time:
            # locate the frame at the index
            i = int(p.camera_metadata.exposures_per_sec * ftime)
            # TODO possibly skew it to adjust for funny camera angle?

            # pass it to our image accumulator
            self.accum_strategy.accumulate(p.image_color[i])

        self.accum_strategy.finalize()