import click
import csv
import sys
import os.path
import numpy as np
from enum import Enum
# import scipy
from PIL import Image

import warnings
from numpy.lib._iotools import ConversionWarning

@click.group
def cli():
    pass


class AccelDirection(Enum):
    X = 0
    PX = 1
    NX = 2
    Y = 3
    PY = 4
    NY = 5
    Z = 6
    PZ = 7
    NZ = 8



@click.argument('dirname')
@click.option("--argdir", "-d", type=click.Choice(AccelDirection))
@cli.command
def render(dirname, argdir = 0):
    if not os.path.isdir(dirname):
        click.echo("bad directory")
        sys.exit(1)
    serialfile = os.path.join(dirname, "serial.txt")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=ConversionWarning)
        timedata, xdata, ydata, zdata = np.array(np.genfromtxt(
            serialfile, delimiter=',',
            invalid_raise=False, loose=True,
            unpack=True,
            dtype="S32,f8,f8,f8",
            names=['timestamp', 'x', 'y', 'z']))

    # pick which data we're using
    if argdir == None:
        argdir = AccelDirection.X

    accel = [xdata, ydata, zdata][int(argdir.value / 3)]
    if (argdir.value % 3 == 2):
        accel = -accel

    isA = np.strings.slice(timedata, 0, 1) == b'A'
    # use mask array to look for first-character == 'A'
    accel = accel[isA].astype(float)
    timedata = timedata[isA]
    timedata = np.strings.slice(timedata, 1, 32).astype(int)
    timedata = timedata - timedata[0]

    metafile = os.path.join(dirname, "meta.csv")
    metadata = read_metadata(metafile)

    width = int(metadata["camera.Width"])

    speed = np.cumsum(accel)
    elapsed = np.diff(timedata)

    camerafile = os.path.join(dirname, "cam.data")
    stat = os.stat(camerafile)
    size = stat.st_size
    frames = int(size / width)

    image_dtype = ""
    image = np.memmap(camerafile, dtype=np.uint8, mode="r", shape=(frames,width))


    exposures_per_sec = 1000 / float(metadata["camera.ExposureTimeAbs"])
    print(f"camera runs at {exposures_per_sec} fps")
    print(timedata)

    start_offset = timedata[:-1] * width
    out = np.zeros((width, width))

    out_i = 0
    buf_i = 0


    for idx, s in enumerate(elapsed):
        # TODO unroll more of this into matrix operations
        # TODO interpolation of speeds
        # instead of assuming constant starting speed
        s = speed[idx]
        e = elapsed[idx]
        dist = s * e


        units_per_sample = 100 # TODO read from flag
        samples = int(dist / units_per_sample)
        if (samples < 0):
            continue

        t = timedata[idx]
        start_i = int(exposures_per_sec * t)
        end_i = int(exposures_per_sec * (t + e))

        if (end_i < frames):
            slice_is = np.linspace(start_i, end_i, num=samples).astype(int)

            for _, x in enumerate(slice_is):
                out[buf_i] = image[x][::-1] # it's upside down?!
                buf_i += 1

                if buf_i == width:
                    print(f"{idx} of {len(elapsed)} ({t} seconds)")
                    img = Image.fromarray(out.T).convert('RGB')
                    img.save(f"out-{out_i:04d}.jpeg")
                    out_i += 1
                    out = np.zeros((width, width))
                    buf_i = 0
        else:
            break

    # TODO truncate
    img = Image.fromarray(out.T).convert('RGB')
    img.save(f"out-{out_i:04d}.jpeg")





def read_metadata(filename: str) -> dict[str, str]:
    config = {}
    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        reader.__next__() # discard header
        for row in reader:
            config[row[0]] = row[1]
    return config

if __name__ == '__main__':
    cli()
