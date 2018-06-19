from __future__ import division
import string
import sys

def reverse_complement(seq) :
    """A function to reverse complement a sequence"""
    trans_table = string.maketrans('ATCG','TAGC')
    return seq.translate(trans_table)[::-1]

# check for proper invocation
if len(sys.argv) < 4 :
    print "Usage: make_new_sample_sheet <hpip_root> <rep> <run>"
    sys.exit(1)

# get arguments from invocation
hpip_root = sys.argv[1]
rep = sys.argv[2]
run = sys.argv[3]

# build directory names
raw_datadir = '%s/data/raw/%s/HPIP_%s_%s'%(hpip_root, run, run, rep)
noDNA_datadir = '%s/data/triplibs/%s/%s_noDNA'%(hpip_root, rep, run)
out_datadir = '%s/data/triplibs/%s/%s'%(hpip_root, rep, run)

# build file names
idx_starcoded_fname = '%s/idx_starcoded.txt'%(noDNA_datadir)
old_ss = '%s/SampleSheet.csv.Marc'%(raw_datadir)
new_ss = '%s/SampleSheet.csv'%(out_datadir)

# extract indices from old Sample Sheet and reverse complement them, and we save
# all of the information to a dictionary
rev_idx = {}
with open(old_ss, 'r') as f :
    print "Marc's sample sheet"

    # we read from line 2 to line 14 (all the lanes)
    lineno = 0
    for line in f :
        lineno += 1

        # parse the line and save data to the dictionary, which contains the
        # reverse-complemented index as key, and candidate library as value
        if lineno > 2 and lineno < 14 :
            lane, sampleID, sampleName, idx = line.strip('\n').split(',')
            idx = idx.strip()
            print "Lib %s: %s [rev: %s]"%(sampleID, idx,
                                          reverse_complement(idx))
            rev_idx[reverse_complement(idx)] = int(sampleID)

# now we parse the starcoded indices file, and we calculate the probability that
# the given read index 
idx_starcoded = {}
tot_counts = 0
N = 20
with open(idx_starcoded_fname, 'r') as f :

    print "Most frequent indices"
    for lineno, line in enumerate(f) :
        candidate,counts = line.strip('\n').split()
        counts = int(counts)
        tot_counts += counts
        if candidate in rev_idx.keys() :
            sampleID = rev_idx[candidate]
            idx_starcoded[sampleID] = (candidate, counts)
        if lineno < N :
            if candidate in rev_idx :
                s = 'was found    '
            else :
                s = 'was not found'
            print "Candidate %d: %s %s in Marc's sample sheet"%(lineno+1, candidate, s)


# get sorted sample ids
sampleIDs = idx_starcoded.keys()
sampleIDs.sort()

# print the indices that we attribute to the libraries
print "Our best guess:"
for sampleID in sampleIDs :
    p = idx_starcoded[sampleID][1]/tot_counts
    print "Lib %d best candidate: %s (%.5f %% of the reads)"%(sampleID,
                                                              idx_starcoded[sampleID][0],p)

# write new Sample Sheet
nlanes = 4
with open(new_ss, 'w') as f :

    # write sample sheet header
    f.write('[Data]\n')
    f.write('Lane,SampleID,SampleName,index,index2\n')

    # write lanes
    for lane in range(1,nlanes+1) :
        for sampleID in sampleIDs :
            f.write('%d,%s,%s%s,%s\n'%(lane, sampleID, run, sampleID,
                                       idx_starcoded[sampleID][0]))
        f.write('%d,%s,noDNA,GGGGGG\n'%(lane, sampleID+1))
