#!/usr/bin/env python3

import sys
import os
import math

# two args: directory and percentage through to start (0-100)
# output: full paths of all files in the dir

directory = sys.argv[1]
percent = int(sys.argv[2]) / 100.0

fnames = os.listdir(directory)
fnames.sort()
l = len(fnames)
idx = math.floor(percent * l)

for f in fnames[idx:]:
    print(os.path.join(directory, f))