import click
import csv
import sys
import os.path
import numpy as np

# import scipy
from PIL import Image

from .consts import AccelDirection, Gravity

import warnings
from numpy.lib._iotools import ConversionWarning

from .stage import adjust, load, parse, process
from .stage import render as rendering

# TODO remove PIL.image so we don't have this annoying name collision
from .stage.image import FramesFromTimestampsBig, FramesFromTimestampsSquare
from .pipeline import Pipeline

@click.group
def app():
    pass


@click.argument('dirname')
@click.option("--argdir", "-d", type=click.Choice(AccelDirection))
@click.option("--unitspersample", "-u", type=float)
@click.option("--big", "-b")
@click.option("--velocity", "-v", type=float)
@app.command
def render(dirname, argdir = 0, unitspersample = 100.0, big = False, velocity = 0.0):
    # pick which data we're using
    if argdir == None:
        argdir = consts.AccelDirection.X
    if unitspersample == None:
        unitspersample = 100.0
    if velocity == None:
        velocity = 0.0

    if big == True:
        accum_strategy = FramesFromTimestampsBig()
    else:
        # TODO width is hardcoded because we're constructing it here
        # before we go and do load.MetadataCsv
        accum_strategy = FramesFromTimestampsSquare(
            invert=False, width=2048, dirname=dirname,
        )


    pipe = Pipeline(stages=[
        load.DirectoryLoad(dirname=dirname),
        load.MetadataCSV(dirname=dirname),
        parse.DirectoryStringData(
            argdir=argdir,
            calibration=[0.0, 0.0, 0.0],
            gravity=Gravity,
        ),
        process.GenerateSpeedsFromAccelerometer(),
        adjust.InitialVelocity(velocity),
        process.GeneratePositionsFromSpeed(),
        process.GenerateTimestampsPerFrame(unitspersample),
        load.MmapGreyscaleImage(dirname),
        rendering.SelectGrayscaleFramesFromTimestamps(
            accum_strategy,
            1.0/unitspersample,
        ),
    ])

    pipe.run()





def old():
    elapsed = np.diff(timedata)

    camerafile = os.path.join(dirname, "cam.data")
    stat = os.stat(camerafile)
    size = stat.st_size
    frames = int(size / width)

    image_dtype = ""
    image = np.memmap(camerafile, dtype=np.uint8, mode="r", shape=(frames,width))

    exposures_per_sec = 1000 / float(metadata["camera.ExposureTimeAbs"])
    print(f"camera runs at {exposures_per_sec} frames / millisecond")
    print(timedata)

    start_offset = timedata[:-1] * width
    out = np.zeros((width, width))
    # TODO: finish implementing big image (ie paste repeatedly bc PIL)
    #big_out = np.zeroes((width,width))
    #big_i = 0

    out_i = 0
    buf_i = 0

    for idx, s in enumerate(elapsed):
        # TODO unroll more of this into matrix operations
        # TODO interpolation of speeds
        # instead of assuming constant starting speed
        s = speed[idx]
        e = elapsed[idx]
        dist = s * e
        # print(f"idx: {idx}, s: {s}, dist: {dist}")

        samples = int(dist / unitspersample)
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
                    print(f"{idx} of {len(elapsed)} ({t} µseconds)")
                    img = Image.fromarray(out.T).convert('RGB')
                    img.save(os.path.join(dirname, f"out-{out_i:04d}.jpeg"))
                    out_i += 1
                    out = np.zeros((width, width))
                    buf_i = 0
        else:
            break

    # TODO truncate
    img = Image.fromarray(out.T).convert('RGB')
    img.save(os.path.join(dirname,f"out-{out_i:04d}.jpeg"))






if __name__ == '__main__':
    app()
