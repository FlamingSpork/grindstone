import click
import csv
import sys
import os.path
import numpy as np

# import scipy
from PIL import Image

from src.grindstone import consts
from .consts import AccelDirection, Gravity

import warnings
from numpy.lib._iotools import ConversionWarning

from .stage import adjust, load, parse, process
from .stage import render as rendering
from .stage.render import ColorImageSource, GreyscaleImageSource

# TODO remove PIL.image so we don't have this annoying name collision
from .stage.image import (
    FramesFromTimestampsBig, FramesFromTimestampsSquare,
    ColorFramesFromTimestampsBig, ColorFramesFromTimestampsSquare,
)
from .pipeline import Pipeline

@click.group
def app():
    pass


@click.argument('dirname')
@click.option("--argdir", "-d", type=click.Choice(AccelDirection))
@click.option("--unitspersample", "-u", type=float)
@click.option("--big", "-b", is_flag=True)
@click.option("--velocity", "-v", type=float)
@click.option("--upsidedown", "-U", is_flag=True)
@click.option("--outformat", "-f", type=str, default="jpeg")
@app.command
def render(dirname, argdir = 0, unitspersample = 100.0, big = False, velocity = 0.0, upsidedown= False, outformat="jpeg"):
    # pick which data we're using
    if unitspersample == None:
        unitspersample = 100.0
    if velocity == None:
        velocity = 0.0
    if big == None:
        big = False

    meta = load.read_metadata(os.path.join(dirname, "meta.csv"))
    width = int(meta["camera.Width"])
    is_color = meta.get("camera.PixelFormat") == "RGB8Packed"

    # argument passed at CLI takes precedence
    if argdir is None:
        try:
            if meta.get("accelerometer.Direction") is not None:
                # the names of enum values can be used with operator[], but it throws AttributeError if it isn't valid
                argdir = consts.AccelDirection[meta.get("accelerometer.Direction")]
                print("read acceleration direction:", argdir)
            else:
                argdir = consts.AccelDirection.X
                print("warning: undefined accelerometer direction, using", argdir)
        except AttributeError:
            argdir = consts.AccelDirection.X
            print("warning: undefined accelerometer direction, using", argdir)

    if is_color:
        image_stage = load.MmapColorImage(dirname)
        source = ColorImageSource()
    else:
        image_stage = load.MmapGreyscaleImage(dirname)
        source = GreyscaleImageSource()

    if big:
        if is_color:
            accum_strategy = ColorFramesFromTimestampsBig(invert=upsidedown, dirname=dirname, width=10000, height=width, ext=outformat)
        else:
            accum_strategy = FramesFromTimestampsBig(invert=upsidedown, dirname=dirname, width=10000, height=width, ext=outformat)
    else:
        if is_color:
            accum_strategy = ColorFramesFromTimestampsSquare(invert=upsidedown, dirname=dirname, width=width, ext=outformat)
        else:
            accum_strategy = FramesFromTimestampsSquare(invert=upsidedown, dirname=dirname, width=width, ext=outformat)

    render_stage = rendering.SelectFramesFromTimestamps(
        accum_strategy=accum_strategy,
        distance = 1.0/unitspersample,
        image_source = source,
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
        image_stage,
        render_stage,
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
