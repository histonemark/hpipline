import gzip
from .utils import prom_id

def parse_bcd(line) :
    """
    Parses a line of the pbd and returns a dictionary of candidate promoters,
    with their probabilities. For the purpose of the operations that will be
    done later with this information, it is useful to return a dictionary that
    has as keys the promoter library index, and as values a list of promoters
    that are in that library.
    """

    bcd, all_candidates = line.strip().split('\t')
    d = {}
    for candidates in all_candidates.split(';') :
        proms_in_lib = []
        for candidate in candidates.split(',') :
            prom_name, p = candidate.split(':')
            prom_class, prom_lib = prom_id(prom_name)
            proms_in_lib.append((prom_class, p))
        d[int(prom_lib)] = proms_in_lib
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
            counts[can] = int(cnts)

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

    # init the dictionary that will allow us to say whether many reads pertain
    # to the same or to different integration sites
    counts = {}

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

                # let's see whether the barcode was already found in the mapping
                # file. In this case, we add a one to the counts dictionary
                ident = (chrom, pos, strand)
                if not counts.has_key(bcd) : 
                    counts[bcd] = {}
                if not counts[bcd].has_key(ident) :
                    counts[bcd][ident] = 0
                counts[bcd][ident] += 1

    # when the parsing of the file is finished, we now analyze the results and
    # establish which is the "true" integration site of the barcode

    # this is a function that evaluates what is the distance between the
    # integration sites passed to it
    def dist(intlist):

        # first, we sort the integration list
        intlist.sort()

        # then we assess whether the chromosomes of the first and last
        # integrations in the list are the same. If so, we return "infinite"
        # distance. This works because the integration list is sorted.
        try:
            chrom_first, pos_first, _ = intlist[0]
            chrom_last,  pos_last, _  = intlist[-1]
            if chrom_first != chrom_last:
                return float('inf')
            return pos_last - pos_first
        except IndexError:
            return float('inf')

    # we go through the whole integration list and calculate the distance
    # between the integration sites
    for bcd, hist in counts.items():

        # we only take into consideration the integrations that have a number of
        # counts that is at least 10% of the total number of counts
        total = sum(hist.values())
        top = [loc for loc, count in hist.items()
               if count > max(1, 0.1*total)]

        # Skip barcode if the distance between the integration sites of the top
        # insertion sites differs more than ten nucleotides (or worse: they are
        # in different chromosomes)
        if dist(top) > 10:
            continue

        # HERE
        ins = max(hist, key=hist.get)
        mapped[bcd] = (ins, total)

    return mapped, N, nmapped
