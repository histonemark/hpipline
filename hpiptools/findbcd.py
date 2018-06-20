#!/bin/python
import os, sys, struct

class PBD :
    def __init__(self, hpip_root) :
        # set input file names
        pbd_fname = '%s/data/pbd/pbd.txt'%(hpip_root)
        pbd_idx = '%s.idx'%(pbd_fname)
        
        # open the index and the pdb file
        self.pbd = open(pbd_fname, 'r')
        self.idx = open(pbd_idx, 'rb')

        # get the number of lines in the pbd by looking
        # at the last value stored in the index
        self.idx.seek(-8, os.SEEK_END)
        self.N = struct.unpack('Q', self.idx.read(8))[0]

    def read_nth_line(self, n) :
        # seek the index at position 'n*8', because the information
        # is stored in chunks of 8 bytes of size
        self.idx.seek(n*8, os.SEEK_SET)
        i_binary = self.idx.read(8)

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
        self.pbd.seek(i, os.SEEK_SET)
        return self.pbd.readline()
    
    def findbcd(self, bcd) :
        # open the pbd index and read the value at the last position,
        # which by convention corresponds to the number of lines in the
        # original file

        # start the iterative search
        range_hi = self.N-1
        range_lo = 0
        while range_lo < range_hi-1 :
            mid = (range_hi+range_lo)//2
            line = self.read_nth_line(mid)
            this_bcd = line[:20]
            if this_bcd < bcd :
                range_lo = mid
            elif this_bcd > bcd :
                range_hi = mid
            else :
                return line

        # if we are here, then the barcode was not found
        return None

    def __del__(self) :
        self.pbd.close()
        self.idx.close()

def read_input(fin) :
    bcd_list = []
    for line in fin :
        bcd_list.append(line.strip())
    return bcd_list

def print_bcd(bcd, pbd) :
    line = pbd.findbcd(bcd)
    if line is None :
        return
    else :
        print line.strip()

if __name__ == '__main__' :
    # check for proper invocation
    if len(sys.argv) < 2 :
        print "Usage: findbcd <bcd> <hpip_root>"
        sys.exit(1)

    # get parameters from command line and decide whether we are in "single
    # barcode mode" or the user passed a file or standard input, in which case
    # we read the barcode list (one per line) and invoke the finder for each of
    # them
    if len(sys.argv) == 2 :
        fin = sys.stdin
        hpip_root = sys.argv[1]
        single_bcd_mode = False
    elif len(sys.argv) == 3 :
        fname = sys.argv[1]
        hpip_root = sys.argv[2]
        if os.path.exists(fname) :
            fin = open(fname, 'r')
            single_bcd_mode = False
        else :
            single_bcd_mode = True

    # init the PBD
    pbd = PBD(hpip_root)

    if not single_bcd_mode :
        bcds = read_input(fin)
        for bcd in bcds :
            print_bcd(bcd, pbd)
        fin.close()
    else :
        print_bcd(bcd, pbd)
