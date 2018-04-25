#!/usr/bin/env python
# coding: utf-8
import pdb
import os
import re
import sys
from gzopen import gzopen

data_path = os.path.abspath(sys.argv[1])
SUBDIR = "/Data/Intensities/BaseCalls"
fn_re = re.compile(r"Undetermined_S[0-9]_L00[1-4]_R1_[0-9]+.fastq.gz")
seq_fnames = [''.join([data_path, SUBDIR, "/", fname]) for fname
              in os.listdir(data_path + SUBDIR) if fn_re.match(fname)]

# Merge the reads coming from the 4 Miseq Lanes
outfname = ''.join([data_path, "/", sys.argv[1].split("/")[-2], ".fastq"])

for fname in seq_fnames:
    with gzopen(fname) as f, open(outfname, "a") as g:
        for lineno, line in enumerate(f):
            if lineno % 4 != 1:
                continue
            g.write(line)
            
