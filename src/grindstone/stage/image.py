from dataclasses import dataclass
import numpy as np
import os
from PIL import Image

from src.grindstone.types import GreyscaleSlice

@dataclass
class FramesFromTimestampsBig:
    dirname: str
    invert: bool
    ext: str
    i: int = 0

    def __init__(self, *, dirname: str, width: int, height: int, invert: bool = False, ext: str = "jpeg") -> None:
        self.dirname = dirname
        self.invert = invert
        self.buf_i = 0
        self.out_i = 0
        self.width = width
        self.height = height
        self.ext = ext
        if width > 65535 and (ext.lower() == "jpg" or ext.lower() == "jpeg"):
            raise ValueError(f"width {width} is too big for JPEG (max 65,535)")
        self.out = np.zeros((width, height), dtype=np.uint8)

    def reset(self) -> None:
        self.buf_i = 0
        self.out_i = 0
        self.out = np.zeros((self.width, self.height), dtype=np.uint8)

    def accumulate(self, slice: GreyscaleSlice) -> None:
        do_invert = -1 if self.invert else 1
        self.out[self.buf_i] = slice[::do_invert] # if it's upside down
        self.buf_i += 1

        if self.buf_i == self.width:
            # TODO callback shenanigans
            print(f"wrote {self.out_i}")
            img = Image.fromarray(self.out.T).convert("RGB")
            img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.{self.ext}"))
            self.out_i += 1
            self.out = np.zeros((self.width, self.height), dtype=np.uint8)
            self.buf_i = 0

    def finalize(self):
        img = Image.fromarray(self.out.T).convert("RGB")
        img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.{self.ext}"))
        print(f"wrote {self.out_i} (partial; {self.buf_i}/{self.width} lines)")

class FramesFromTimestampsSquare(FramesFromTimestampsBig):
    def __init__(self, *, dirname: str, width: int, invert: bool = False, ext: str = "jpeg"):
        FramesFromTimestampsBig.__init__(self, dirname=dirname, width=width, height=width, invert=invert, ext=ext)

class ColorFramesFromTimestampsBig:
    dirname: str
    invert: bool
    i: int = 0
    ext: str

    def __init__(self, *, dirname: str, width: int, height: int, invert: bool = False, ext: str = "jpeg") -> None:
        self.dirname = dirname
        self.invert = invert
        self.buf_i = 0
        self.out_i = 0
        self.width = width
        self.height = height
        self.ext = ext
        if width > 65535 and (ext.lower() == "jpg" or ext.lower() == "jpeg"):
            raise ValueError(f"width {width} is too big for JPEG (max 65,535)")
        self.out = np.zeros((width, height, 3), dtype=np.uint8)


    def reset(self) -> None:
        self.buf_i = 0
        self.out_i = 0
        self.out = np.zeros((self.width, self.height, 3), dtype=np.uint8)

    def accumulate(self, slice: ColorSlice) -> None:
        do_invert = -1 if self.invert else 1
        self.out[self.buf_i] = slice[::do_invert] # if it's upside down
        self.buf_i += 1

        if self.buf_i == self.width:
            # TODO callback shenanigans
            print(f"wrote {self.out_i}")
            contig = np.ascontiguousarray(self.out.transpose(1, 0, 2))
            img = Image.fromarray(contig, "RGB")
            img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.{self.ext}"))
            self.out_i += 1
            self.out = np.zeros((self.width, self.height, 3), dtype=np.uint8)
            self.buf_i = 0

    def finalize(self):
        contig = np.ascontiguousarray(self.out.transpose(1,0,2))
        img = Image.fromarray(contig, "RGB")
        img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.{self.ext}"))
        print(f"wrote {self.out_i} (partial; {self.buf_i}/{self.width} lines)")

class ColorFramesFromTimestampsSquare(ColorFramesFromTimestampsBig):
    def __init__(self, *, dirname: str, width: int, invert: bool = False, ext: str = "jpeg"):
        ColorFramesFromTimestampsBig.__init__(self, dirname=dirname, width=width, height=width, invert=invert, ext=ext)