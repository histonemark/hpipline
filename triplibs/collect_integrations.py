import os, sys, gzip
import hpiptools as ht

prog_name = 'collect_integrations'

# check for proper invocation
if len(sys.argv) < 4 :
    print "Usage: collect_integrations <hpip_root> <rep> <lib>"
    sys.exit(1)

# get data directory from command line
hpip_root = sys.argv[1]
rep = sys.argv[2]
lib = sys.argv[3]

# the library ID will allow us to assign the promoter to the barcode
lib_id = int(lib.lstrip('lib'))

# datadir
datadir = '%s/data/triplibs/%s/%s'%(hpip_root, rep, lib)

# build file names
iPCR_starcode_fname = '%s/iPCR-starcode.txt'%(datadir)
cDNA_starcode_fname = '%s/cDNA-starcode.txt'%(datadir)
gDNA_starcode_fname = '%s/gDNA-starcode.txt'%(datadir)
iPCR_sam_fname = '%s/iPCR.sam'%(datadir)

# work on the starcoded files
ht.log_message(prog_name, 'Loading starcoded files')
iPCR_canonicals, iPCR_counts = ht.parse_starcode(iPCR_starcode_fname)
cDNA_canonicals, cDNA_counts = ht.parse_starcode(cDNA_starcode_fname)
gDNA_canonicals, gDNA_counts = ht.parse_starcode(gDNA_starcode_fname)

# init promoter-barcode dictionary
pbd = ht.PBD(hpip_root)

# now we process the mapped file
ht.log_message(prog_name, 'Processing mapped file')
mapped, nmulti, nmapped, nunmapped = ht.parse_mapped(iPCR_sam_fname)

# init numbers that will allow to make statistics of the integrations
n_in_cDNA = 0
n_in_gDNA = 0
n_in_both = 0
n_in_pbd = 0
n_in_pbd_lib = 0

# open the output file
with open('%s/%s-integrations.txt'%(datadir, lib), 'w') as f :

    # iterate over all the mapped integrations
    for bcd, insertion in mapped.iteritems() :
        
        # define flags that will allow us to make some statistics
        # about how many integration get in and out of the final
        # insertion table
        in_cDNA = cDNA_counts.has_key(bcd)
        in_gDNA = gDNA_counts.has_key(bcd)
        in_both = in_cDNA and in_gDNA
        
        # interrogate the pbd to know whether the barcode that we
        # are looking at was actually known in the promoter-barcode
        # association table
        pr = pbd.findbcd(bcd)
        in_pbd = pr is not None

        # do statistics
        if in_cDNA : n_in_cDNA += 1
        if in_gDNA : n_in_gDNA += 1
        if in_both : n_in_both += 1
        if in_pbd : n_in_pbd += 1
        
        # proceed with the calculations only if the three conditions
        # are met: the mapped insertion is in the cDNA, in the gDNA, 
        # and in the pbd.
        if in_both and in_pbd :
            
            # get the list of promoters associated to the
            # barcode from the pbd
            proms = ht.parse_bcd(pr)
            in_pbd_lib = proms.has_key(lib_id)
            
            # if we find that the barcode was in the pbd, but none of
            # the candidate promoters are in the library under consideration,
            # then we need to throw this integration away because we cannot
            # know which promoter it is associated to
            if not in_pbd_lib :
                continue

            # increment counter that tells us the number of integrations that in
            # the end will enter in the integration table
            if in_pbd_lib : n_in_pbd_lib += 1

            # if we are here, everything is fine and we prepare the string
            # that we output to our final file. First, we prepare a string
            # that contains the information about the candidate promoters
            prom_string = ''
            for prom_class, p in proms[lib_id] :
                prom_string += '\t%s%d:%s'%(prom_class, lib_id, p)
            
            # we then prepare the line that contains the information about
            # the barcode, the mapping, the reads, and the promoter
            chrom, pos, strand = insertion[0]
            iPCR_counts = insertion[1]
            line = '%s\t'%(bcd)
            line += '%s\t%d\t%s'%(chrom, pos, strand)
            line += '\t%d\t%d\t%d'%(iPCR_counts,
                                   cDNA_counts[bcd],
                                   gDNA_counts[bcd])
            line += prom_string
            line += '\n'
            f.write(line)

# write statistics of the library
with open('%s/%s.stats'%(datadir, lib), 'w') as f :
    f.write("%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n"%(lib, nmapped, nunmapped, nmulti,
                                               len(iPCR_canonicals),
                                               len(mapped),
                                         n_in_cDNA, n_in_gDNA, n_in_both,
                             n_in_pbd, n_in_pbd_lib))
