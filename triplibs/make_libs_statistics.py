import os, sys

def parse_starcode(starcode_fname) :
    canonical = {}
    with open(starcode_fname, 'r') as f:
        for line in f:
            items = line.strip().split()
            for brcd in items[2].split(','):
                canonical[brcd] = items[0]
    return canonical

# check for proper invocation
if len(sys.argv) < 4 :
  print "Usage: make_libs_statistics <iPCR_fname> <cDNA_fname> <gDNA_fname> <out_fname>"
  sys.exit(1)

# get parameters from command line
iPCR_fname = sys.argv[1]
cDNA_fname = sys.argv[2]
gDNA_fname = sys.argv[3]
out_fname = sys.argv[4]

# load iPCR, gDNA and cDNA files
iPCR = parse_starcode(iPCR_fname)
cDNA = parse_starcode(cDNA_fname)
gDNA = parse_starcode(gDNA_fname)

# reset counters
in_cDNA = in_gDNA = in_both = 0

# read the iPCR barcodes and evaluate whether those barcodes were found in the
# cDNA and gDNA experiments, and increment counters
for bcd in iPCR.iterkeys() :
    is_in_cDNA = cDNA.has_key(bcd)
    is_in_gDNA = gDNA.has_key(bcd)
    if is_in_cDNA :
        in_cDNA += 1
    if is_in_gDNA :
        in_gDNA += 1
    if is_in_cDNA and is_in_gDNA :
        in_both += 1

# write output to file
with open(out_fname, 'w') as f :
    f.write("%d %d %d %d\n"%(len(iPCR), in_cDNA, in_gDNA, in_both))
