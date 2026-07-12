#!/usr/bin/env python3

# yes, I know this is crude and I will eventually make this a part of the pipeline
# but I don't have the time to do so now, so it's its own script
# it's also exceedingly slow and I'm not sure why

import numpy as np
import scipy as sp
from PIL import Image
import sys

path = sys.argv[1]
shiftVal = int(sys.argv[2])
save = (len(sys.argv) == 4)

print(f"shifting {path} by {shiftVal} px")

img = Image.open(path)
arr = np.asarray(img, dtype=np.uint8)
print(arr.shape)
r = arr[:, :, 0]
g = arr[:, :, 1]
b = arr[:, :, 2]

rS = sp.ndimage.shift(r, [0,-1 * shiftVal])
gS = sp.ndimage.shift(g, [0,0])
bS = sp.ndimage.shift(b, [0,shiftVal])

stacked = np.stack([rS, gS, bS], axis=-1)
stackedImg = Image.fromarray(stacked, "RGB")
if save:
    print(f"overwriting {path}")
    stackedImg.save(path)  # we overwrite in this web zone
else:
    stackedImg.show()