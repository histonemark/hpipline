import gzip

def parse_bcd(line) :
    """
    Parses a line of the pbd and returns a dictionary of candidate promoters,
    with their probabilities
    """
    bcd,all_candidates = line.strip().split('\t')
    d = {}
    for candidates in all_candidates.split(';') :
        for candidate in candidates.split(',') :
            prom_name,p = candidate.split(':')
            d[prom_name] = p
    return d

def parse_fastq(fastq_fname) :
    """
    Parses a FASTQ.GZ file, returning a dictionary that contains the barcodes
    (cowboy-mode) as keys, and the index of the read as value
    """

    # open file with gzip.open
    with gzip.open(fastq_fname, 'r') as f :

        # init the dictionary that will contain the barcode and its
        # corresponding index
        d = {}

        # iterate over the lines in the file
        for lineno, line in enumerate(f) :

            # read only the lines that correspond to the first and second in
            # each block
            if lineno%4 == 0 :

                # get the index of the read by taking the last 6 characters of
                # the line
                idx = line[-7:].strip()

            elif lineno%4 == 1 :

                # extract the barcode in cowboy-mode (that is, get the first 20
                # nucleotides of the sequence, regardless of whether the rest of
                # the read is random stuff or meaningful stuff)
                bcd = line[:20]
                d[bcd] = idx
            else :
                continue
    return d

def parse_starcode(starcode_fname, inverse=False) :
    """
    Parses the output of a starcode run that was run with --print-clusters.
    Returns two dictionaries: `counts`, which contains the number of reads
    associated to a particular canonical, and `canonical`, which associates each
    barcode to its canonical
    """

    # init the dictionaries that will contain the number of counts associated to
    # the canonical, and the barcode->canonical association
    counts = {}
    canonical = {}

    # open file
    with open(starcode_fname, 'r') as f:

        for line in f:

            # extract the information from each line of the file: the canonical,
            # its counts, and the list of barcodes that are associated to that
            # canonical
            can, cnts, bcds = line.strip().split()

            # fill in the 'canonical' dictionary
            if inverse :
                canonical[can] = []
            for bcd in bcds.split(','):
                if inverse :
                    canonical[can].append(bcd)
                else :
                    canonical[bcd] = can

            # fill in the 'counts' dictionary
            counts[can] = cnts

    return canonical, counts

def parse_mapped(mapped_fname) :
    """
    Parses a .sam file, returning a dictionary that contains a barcode as key,
    and the mapping information as value. The function outputs also the total
    number of reads in the sam file, and the number of mapped reads.
    """

    # this is a bitwise comparison flag that allows to tell whether the flag
    # that bwa outputs as second field in the file corresponds to 'reverse
    # strand' mapping
    ISREV = 0b10000

    # init the dictionary that will contain all the info
    mapped = {}

    # init number of mapped integrations
    nmapped = 0

    # open file
    with open(mapped_fname) as f:

        # iterate over all lines of the file
        for N, line in enumerate(f):

            # skip the first lines that start with @
            if line[0] == '@':
                continue

            # get the fields we are interested in from splitting the line and
            # getting the first four fields
            bcd, flag, chrom, pos  = line.split()[:4]

            # if the 'chrom' field (the third in the mapped file) is an
            # asterisk, then it means that bwa was not able to find a mapping
            # for the integration, and we skip this integration
            if chrom != '*':

                # increment the number of mapped reads
                nmapped += 1

                # get the strand
                strand = '-' if int(flag) & ISREV else '+'
                pos = int(pos)

                # fill the dictionary with the information
                ident = (chrom, pos, strand)
                if not mapped.has_key(bcd) :
                    mapped[bcd] = [ident]
                else :
                    mapped[bcd].append(ident)
    return mapped, N, nmapped
