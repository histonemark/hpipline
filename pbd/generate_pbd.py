from __future__ import division
import os, sys

def calculate_rel_ps(prom_list, prom_lib, lib_counts) :
    """Compute the relative probabilities within the library"""
    ps = []
    for prom_class,bcd_count in prom_list :
        ps.append(bcd_count/lib_counts['%s%d'%(prom_class, prom_lib)])
    tot_p = sum(ps)
    rel_ps = [p/tot_p for p in ps]
    return rel_ps

def string_lib(prom_list, prom_lib, rel_ps) :
    """Generates a string for the promoter list, to output to the pbd dictionary"""
    string = ''
    for i in range(len(prom_list)) :
        prom_class,_ = prom_list[i]
        p = rel_ps[i]
        if i>0 : string += ','
        string += '%s%d:%.3f'%(prom_class,prom_lib,p)
    return string

# general variables
pbd_datadir = '/home/rcortini/work/CRG/projects/hpip/data/pbd'
libs = range(1,13)
prom_classes = ['A','B','C','D','E','F','G','H']

# STEP 1: parse all the starcoded files and collect all the barcodes, along with
# the barcode counts in that library, and compute the total number of reads per
# library, saving it in the 'lib_counts' dictionary
prom_bcd_dict = {}
lib_counts = {}
for lib in libs :

    # each library will contain its own dictionary of barcodes
    d = {}
    for prom_class in prom_classes :

        # build promoter name and file name
        prom_name = '%s%d'%(prom_class,lib)
        fname = '%s/Starcoded_proms/Promoter%s-starcoded.txt'%(pbd_datadir,prom_name)
        counts = 0
        # check if file exists, and if not skip it
        if not os.path.exists(fname) :
            continue

        # parse starcoded file
        print "Lib %d: Processing %s"%(lib, prom_name)
        with open(fname) as f:
            for lineno,line in enumerate(f):
                bcd, bcd_counts,_ = line.split()
                bcd_counts = int(bcd_counts)
                counts += bcd_counts
                # the entries of the dictionary are a tuple that contains the
                # promoter class (no need of setting promoter library: it is
                # implicit in the key of the prom_bcd_dict) and the counts that
                # starcode outputs to the file
                bcd_info = (prom_class,bcd_counts)
                if bcd in d :
                    d[bcd].append(bcd_info)
                else :
                    d[bcd] = [bcd_info]
        lib_counts[prom_name] = counts
    prom_bcd_dict[lib] = d

# STEP 2: compute the relative probabilities and output the dictionary to a file
prom_bcd_fname = '%s/pbd.txt'%(pbd_datadir)
with open(prom_bcd_fname,'w') as f :

    # iterate through all the libraries
    for lib,d in prom_bcd_dict.iteritems() :
        print "Writing library %d"%lib

        # iterate through all the barcodes in the library
        for bcd, prom_list in d.iteritems() :
            
            # get the relative probabilities by dividing the counts of the
            # barcode by the total number of counts of the library. Then sum all
            # the probabilities and get the relative amount of each promoter.
            rel_ps = calculate_rel_ps(prom_list,lib,lib_counts)

            # initiate the line that will be outputted to the file
            line = '%s\t'%(bcd)
            line += string_lib(prom_list,lib,rel_ps)

            # check if the barcode that we are currently looking at is found in
            # the other libraries
            for lib_try in libs[lib+1:] :

                if bcd in prom_bcd_dict[lib_try] :
                    
                    # if the barcode is found, then we calculate its relative
                    # probability in the other library (lib_try), and we get the
                    # corresponding string, separated by a semi-colon.
                    prom_list_lib_try = prom_bcd_dict[lib_try][bcd]
                    rel_ps = calculate_rel_ps(prom_list_lib_try,lib_try,lib_counts)
                    line += ';'
                    line += string_lib(prom_list_lib_try,lib_try,rel_ps)

                    # important: we now need to remove the barcode from the lib_try library,
                    # because otherwise we will find it again when we will parse that library,
                    # resulting in multiple entries in the output file
                    del prom_bcd_dict[lib_try][bcd]

            # finalize the line with a newline, and output to file
            line += '\n'
            f.write(line)
