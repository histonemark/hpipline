import os, struct, sys

def make_file_index(fname, idx_fname) :
    
    # open the original file normally, and the index file as a
    # binary file
    with open(fname,'r') as f_in, open(idx_fname,'wb') as f_out :

        # doing a normal iteration over the file lines
        # as in 'for line in f_in' will not work combined with
        # f_in.tell(). Therefore, we need to use this other way
        # of iterating over the file.
        # From https://stackoverflow.com/a/14145118/2312821
        lineno = 0
        for line in iter(f_in.readline, '') :
            f_out.write('%s'%(struct.pack("Q", f_in.tell())))
            lineno += 1
        f_out.seek(-8, os.SEEK_CUR)
        f_out.write('%s'%(struct.pack("Q", lineno)))

# check for proper invocation
if len(sys.argv) < 3 :
    print "Usage: make_pbd_idx <pbd_fname> <idx_fname>"
    sys.exit(1)

# file names
pbd_fname = sys.argv[1]
idx_fname = sys.argv[2]

# now invoke the file indexing method
make_file_index(pbd_fname, idx_fname)
