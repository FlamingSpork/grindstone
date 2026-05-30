from dataclasses import dataclass
import numpy as np
import os
from PIL import Image

class FramesFromTimestampsSquare:
    dirname: str
    invert: bool
    i: int = 0

    def __init__(self, *, dirname: str, width: int, invert: bool = False) -> None:
        self.dirname = dirname
        self.invert = invert
        self.buf_i = 0
        self.out_i = 0
        self.width = width
        self.out = np.zeros((width, width))


    def reset(self) -> None:
        self.buf_i = 0
        self.out_i = 0
        self.out = np.zeros((width, width))

    def accumulate(self, slice: GreyscaleSlice) -> None:
        do_invert = -1 if self.invert else 1
        self.out[self.buf_i] = slice[::do_invert] # if it's upside down
        self.buf_i += 1

        if self.buf_i == self.width:
            # TODO callback shenanigans
            print(f"wrote {self.out_i}")
            img = Image.fromarray(self.out.T).convert('RGB')
            img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.jpeg"))
            self.out_i += 1
            self.out = np.zeros((self.width, self.width))
            self.buf_i = 0

    def finalize(self):
        # TODO flush partial frame at the end
        pass

@dataclass
class FramesFromTimestampsBig:
    pass

class ColorFramesFromTimestampsSquare:
    dirname: str
    invert: bool
    i: int = 0

    def __init__(self, *, dirname: str, width: int, invert: bool = False) -> None:
        self.dirname = dirname
        self.invert = invert
        self.buf_i = 0
        self.out_i = 0
        self.width = width
        self.out = np.zeros((width, width, 3), dtype=np.uint8)


    def reset(self) -> None:
        self.buf_i = 0
        self.out_i = 0
        self.out = np.zeros((self.width, self.width, 3), dtype=np.uint8)

    def accumulate(self, slice: ColorSlice) -> None:
        do_invert = -1 if self.invert else 1
        self.out[self.buf_i] = slice[::do_invert] # if it's upside down
        self.buf_i += 1

        if self.buf_i == self.width:
            # TODO callback shenanigans
            print(f"wrote {self.out_i}")
            contig = np.ascontiguousarray(self.out.transpose(1, 0, 2))
            img = Image.fromarray(contig, "RGB")
            img.save(os.path.join(self.dirname, f"out-{self.out_i:04d}.jpeg"))
            self.out_i += 1
            self.out = np.zeros((self.width, self.width, 3), dtype=np.uint8)
            self.buf_i = 0

    def finalize(self):
        # TODO flush partial frame at the end
        pass