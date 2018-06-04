from __future__ import print_function
import gzip
import time, sys, errno, os
import pickle
import re
import subprocess
import tempfile
from collections import defaultdict
from itertools import izip
import seeq

class FormatException(Exception):
    pass

def generate_counts_dict(fname_starcode_out, fname_mapped, fname_bcd_dictionary) :
    """ This function generates a dictionary that allows for knowing the
    integration sites of each barcode. The keys of the dictionary are the
    barcode sequences, and the values are another dictionary. The internal
    dictionary contains the (chrom, strand, coord, promoter) information as keys, and
    the number of occurrences as values."""

    # generate file name
    fname_counts_dict = re.sub(r'\.sam', '_counts_dict.p',
                                    fname_mapped)

    # open big promoter-barcode dictionary
    bcd_promd = pickle.load(open(fname_bcd_dictionary, "rb"))

    # create a dictionary of "canonical" barcodes
    canonical = dict()
    with open(fname_starcode_out) as f:
        for line in f:
            items = line.split()
            for brcd in items[2].split(','):
                canonical[brcd] = items[0]

    # generate the counts dictionary
    counts = {}
    ISREV = 0b10000
    with open(fname_mapped) as f:
        for line in f:
            if line[0] == '@':
                continue
            items = line.split()
            # fetch the canonical barcode from the output of starcode
            try:
                barcode = canonical[items[0]]
            except KeyError:
                continue
            if items[2] == '*':
                position = ('', 0)
            else:
                try:
                    # Use dictionary associates barcodes to promoters
                    # from the library sequencing.
                    promoter = bcd_promd[barcode]
                except KeyError:
                    continue
                strand = '-' if int(items[1]) & ISREV else '+'
                chrom = items[2]
                pos = int(items[3])
                ident = (chrom, pos, strand, promoter)
                if not counts.has_key(barcode) : 
                    counts[barcode] = {}
                if not counts[barcode].has_key(ident) :
                    counts[barcode][ident] = 0
                counts[barcode][ident] += 1

    # save to counts dictionary file
    pickle.dump(counts, open(fname_counts_dict,'wb'))

def collect_integrations(fname_counts_dict, fname_cDNA, fname_gDNA) :
    """This function reads the starcode output and changes all the barcodes
    mapped by their canonicals while it calculates the mapped distance
    rejecting multiple mapping integrations or unmmaped ones. It also
    counts the frequency that each barcode is found in the mapped data
    even for the non-mapping barcodes."""

    # temporary fix to work with makefile
    args = [fname_cDNA,fname_gDNA]

    # generate output file name
    fname_insertions_table = re.sub(r'\_counts_dict.p', '_insertions.txt',
                                    fname_counts_dict)

    # Substitution failed, append '_insertions.txt' to avoid name conflict.
    if fname_insertions_table == fname_counts_dict:
        fname_insertions_table = fname_counts_dict + '_insertions.txt'

    # open curated counts dictionary
    counts = pickle.load(open(fname_counts_dict, "rb"))

    def dist(intlist):
        intlist.sort()
        try:
            if intlist[0][0] != intlist[-1][0]:
                return float('inf')
            return intlist[-1][1] - intlist[0][1]
        except IndexError:
            return float('inf')

    integrations = dict()
    for brcd, hist in counts.items():
        total = sum(hist.values())
        top = [loc for loc, count in hist.items()
               if count > max(1, 0.1*total)]
        # Skip barcode in case of disagreement between top votes.
        if dist(top) > 10:
            continue
        ins = max(hist, key=hist.get)
        integrations[brcd] = (ins, total)

    # Count reads from other files.
    reads = dict()
    # First item of tuple is barcode file, second is the spike's one
    for fname in args:
        reads[fname] = defaultdict(int)
        with open(fname) as f:
            for line in f:
                items = line.split('\t')
                try:
                    reads[fname][items[0]] = int(items[1])
                except (IndexError, ValueError) as ex:
                    raise FormatException("Input file with wrong format")
    with open(fname_insertions_table, 'w') as outf:
        unmapped = 0
        mapped = 0
        outf.write('# bcd chrom strand coord mRNA prom cDNA gDNA\n')
        for brcd in sorted(integrations, key=lambda x:
                           (integrations.get(x), x)):
            (chrom, pos, strand, promoter), total = integrations[brcd]
            mapped += 1
            outf.write('%s\t%s\t%s\t%d\t%d\t%s' %
                       (brcd, chrom, strand, pos, total, promoter))
            for fname in args:
                outf.write('\t' + str(reads[fname][brcd]))
            outf.write('\n')
    print('%s: mapped:%d, unmapped:%d\n'%(fname_counts_dict, mapped, unmapped),
         file=sys.stderr)
