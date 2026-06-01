from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np

from ..types import Payload, GreyscaleImage, ColorImage


class ImageSource(ABC):
    @abstractmethod
    def get(self, p: Payload) -> GreyscaleImage | ColorImage:
        ...

class GreyscaleImageSource(ImageSource):
    def get(self, p: Payload) -> GreyscaleImage:
        return p.image_greyscale

class ColorImageSource(ImageSource):
    def get(self, p: Payload) -> ColorImage:
        return p.image_color


@dataclass
class SelectFramesFromTimestamps:
    accum_strategy: AccumStrategy
    distance: float
    image_source: ImageSource

    def process(self, p: Payload):
        image = self.image_source.get(p)
        eps = p.camera_metadata.exposures_per_sec

        for ftime in p.frame_times.time:
            # locate the frame at the index
            i = int(eps * ftime)
            # TODO possibly skew it to adjust for funny camera angle?
            self.accum_strategy.accumulate(image[i])

        self.accum_strategy.finalize()
