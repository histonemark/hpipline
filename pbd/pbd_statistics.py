import numpy as np
import sys, os
import hpiptools as ht

# preliminaries
prom_classes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
prom_libs = range(1,13)
n_prom_classes = len(prom_classes)
n_prom_libs = len(prom_libs)

# this function returns the indices of the matrix that corresponds to the matrix
# of the 96-well plate, given the promoter class and the promoter library. It
# also returns the index of the row-sorted plate.
def prom_idx(p_class, p_lib) :
    i, j = prom_classes.index(p_class), prom_libs.index(p_lib)
    return i, j, n_prom_libs*i + j

# check proper invocation
if len(sys.argv) < 2 :
    print "Usage: pbd_statistics <hpip_root>"
    sys.exit(1)

# get parameters from command line
hpip_root = sys.argv[1]

# build pbd file name and check that it exists
pbd_fname = "%s/data/pbd/pbd.txt"%(hpip_root)
if not os.path.exists(pbd_fname) :
    print "PBD file %s not found"%(pbd_fname)
    sys.exit(1)

# prepare the matrices
prom_counts = np.zeros((n_prom_classes, n_prom_libs), dtype=int)
prom_collisions = np.zeros((n_prom_classes*n_prom_libs,
                            n_prom_classes*n_prom_libs), dtype=int)

# open pbd file
with open(pbd_fname, 'r') as f :

    # iterate over all the barcodes
    for lineno, line in enumerate(f) :

        # use the function from hpiptools to parse the line
        bcds = ht.parse_bcd(line)

        # collisions are found by knowing the libraries in which that particular
        # barcode was found. Therefore, we initiate an  empty list with the
        # collisions at the beginning of the iteration on the libraries.
        collisions = []

        # iterate over the libraries and classes that the barcode was found in
        for bcd_lib, proms in bcds.iteritems() :

            # increment the counts of the found barcode
            for prom in proms :
                i, j, p_idx = prom_idx(prom[0], bcd_lib)
                prom_counts[i, j] += 1
                collisions.append(p_idx)

        # if the length of the collision array is greater than one, then we
        # proceed updating the collision matrix
        if len(collisions) > 1 :
            for k, src in enumerate(collisions) :
                for dst in collisions[k+1:] :
                    prom_collisions[src, dst] += 1
                    prom_collisions[dst, src] += 1

# write the count matrix to file
counts_fname = '%s/data/pbd/pbd_counts.tsv'%(hpip_root)
with open(counts_fname, 'w') as counts :

    # write counts file header
    counts.write('\t' + '\t'.join([str(p) for p in prom_libs]) + '\n')
    for i, prom_class in enumerate(prom_classes) :

        # write promoter class name at beginning of line
        counts.write('%s\t'%(prom_class))

        # write counts
        for j, prom_lib in enumerate(prom_libs) :
            counts.write('%d\t'%(prom_counts[i, j]))

        # finalize line
        counts.write('\n')

# prepare promoter names
prom_names = []
for prom_class in prom_classes :
    for prom_lib in prom_libs :
        prom_names.append('%s%d'%(prom_class, prom_lib))

# write the collision matrix to file
collisions_fname = '%s/data/pbd/pbd_collisions.tsv'%(hpip_root)
with open(collisions_fname, 'w') as collisions :

    # write collisions file header
    collisions.write('\t' + '\t'.join(prom_names) + '\n')
    for i, prom_name in enumerate(prom_names) :

        # write promoter name at the beginning of the line
        collisions.write('%s\t'%(prom_name))

        # write collisions count
        for j in range(len(prom_names)) :
            collisions.write('%d\t'%(prom_collisions[i, j]))

        # finalize line
        collisions.write('\n')
