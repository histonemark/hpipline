import os, sys

# check for proper invocation
if len(sys.argv) < 2 :
    print "Usage: gather_integrations <hpip_root>"
    sys.exit(1)

# get arguments from invocation
hpip_root = sys.argv[1]

# datadir
triplibs_dir = '%s/data/triplibs'%(hpip_root)

# scan the whole "triplibs_dir" directory tree and look for our integrations
# files. Note that I search this way because in the future we could add more
# replicates and more libraries, so this way I keep it general.
with open('hpip-integrations.txt', 'w') as f :
    for root, subs, files in os.walk(triplibs_dir) :

        # scan the file names
        for fname in files :

            # pick only the files that end with "-integrations.txt", which are the
            # ones that interest us
            if fname.endswith('-integrations.txt') :
                _, rep, lib = root.split(triplibs_dir)[1].split('/')

                # open the file
                with open('%s/%s'%(root, fname), 'r') as fin :
                    for line in fin :
                        curatedline = line.strip('\n').split('\t')
                        bcd, chrom, pos, strand, iPCR, cDNA, gDNA = curatedline[:7]
                        proms = curatedline[7:]
                        outline = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(bcd, chrom,
                                                                    pos, strand,
                                                                    lib, rep,
                                                                    iPCR, cDNA,
                                                                    gDNA)
                        for prom in proms :
                            outline += '\t%s'%(prom)
                        outline += '\n'
                        f.write(outline)
