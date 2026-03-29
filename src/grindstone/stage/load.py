import os

from dataclasses import dataclass
import warnings
from ..types import CameraMetadata, Payload, RawTimed3DIMU, ImageMetadata
from ..pipeline import PipelineStage
from numpy.lib._iotools import ConversionWarning
import numpy as np
import csv

@dataclass
class DirectoryLoad(PipelineStage):
    dirname: str

    def process(self, payload: Payload) -> None:
        # this is a log file
        # it contains a bunch of lines.

        # accelerometer data will be the lines
        # that start with an A

        if not os.path.isdir(self.dirname):
            click.echo("bad directory")
            sys.exit(1)


        serialfile = os.path.join(self.dirname, "serial.txt")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ConversionWarning)
            timedata, xaccel, yaccel, zaccel = np.array(np.genfromtxt(
                serialfile, delimiter=',',
                invalid_raise=False, loose=True,
                unpack=True,
                dtype="S32,f8,f8,f8",
                names=['timestamp', 'x', 'y', 'z'],
            ))

        payload.raw = RawTimed3DIMU(timedata, xaccel, yaccel, zaccel)

@dataclass
class MetadataCSV:
    dirname: str

    def process(self, payload: Payload) -> None:
        metafile = os.path.join(self.dirname, "meta.csv")
        payload.raw_metadata = m = read_metadata(metafile)
        payload.camera_metadata = CameraMetadata(
            width=int(m["camera.Width"]),
            exposures_per_sec = 1000 / float(m["camera.ExposureTimeAbs"])
        )
        payload.image_metadata = ImageMetadata(
            frames=int(m["capture.LineCount"]),
        )

def read_metadata(filename: str) -> dict[str, str]:
    config = {}
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        reader.__next__() # discard header
        for row in reader:
            config[row[0]] = row[1]
    return config


@dataclass
class MmapGreyscaleImage:
    dirname: str
    def process(self, payload: Payload) -> None:
        camerafile = os.path.join(self.dirname, "cam.data")
        payload.image_greyscale = np.memmap(
            camerafile, dtype=np.uint8, mode="r",
            shape=(
                payload.image_metadata.frames,
                payload.camera_metadata.width,
            )
        )
