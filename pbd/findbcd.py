#!/bin/python
import os, sys, struct

def file_read_nth_line(n, fname, idx_fname) :
    # Try to read the n-th index from the idx list. With an 
    # 'IndexError' it means that the original file does not have
    # that number of lines
    with open(idx_fname, 'rb') as f :
        f.seek(n*8, os.SEEK_SET)
        i_binary = f.read(8)
        
        # if 'i_binary' is an empty string, it means we reached
        # the end of the file: that is, the original file did not
        # have that number of lines
        if i_binary == '' :
            return None
        
        # if not, then we can unpack the string and convert it to a
        # python integer, which will allow us to read from the
        # correct line in the original file (i)
        i = struct.unpack('Q', i_binary)[0]
    
    # read original file and jump to the correct line
    with open(fname, 'r') as f :
        f.seek(i, os.SEEK_SET)
        return f.readline()

def findbcd(bcd, pbd_fname, pbd_idx) :
    
    # open the pbd index and read the value at the last position,
    # which by convention corresponds to the number of lines in the
    # original file
    with open(pbd_idx, 'rb') as f :
        f.seek(-8, os.SEEK_END)
        N = struct.unpack('Q', f.read(8))[0]
    
    # start the iterative search
    range_hi = N-1
    range_lo = 0
    while range_lo < range_hi-1 :
        mid = (range_hi+range_lo)//2
        line = file_read_nth_line(mid, pbd_fname, pbd_idx)
        this_bcd = line[:20]
        if this_bcd < bcd :
            range_lo = mid
        elif this_bcd > bcd :
            range_hi = mid
        else :
            return line
    
    # if we are here, then the barcode was not found
    return None

if __name__ == '__main__' :
    # check for proper invocation
    if len(sys.argv) < 2 :
        print "Usage: findbcd <bcd> <hpip_root>"

    # get parameters from command line
    bcd = sys.argv[1]
    hpip_root = sys.argv[2]

    # build file names
    pbd_fname = '%s/data/pbd/pbd.txt'%(hpip_root)
    pbd_idx = '%s.idx'%(pbd_fname)

    print findbcd(bcd, pbd_fname, pbd_idx).strip()
