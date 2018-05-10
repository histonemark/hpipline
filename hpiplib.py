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

# utility functions
def time_string () :
    return time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime ())

def error_message(program_name, message) :
    full_message = "%s %s:   ERROR: %s"%(time_string(), program_name, message)
    print(full_message, file=sys.stderr)

def log_message(program_name, message) :
    full_message = "%s %s:    INFO: %s"%(time_string(), program_name, message)
    print(full_message)

def warn_message(program_name, message) :
    full_message = "%s %s: WARNING: %s"%(time_string(), program_name, message)
    print(full_message)

class gzopen(object):
    def __init__(self, fname):
        f = open(fname)
        magic_number = f.read(2)
        f.seek(0)
        if magic_number == '\x1f\x8b':
            self.f = gzip.GzipFile(fileobj=f)
        else:
            self.f = f
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        try:
            self.f.fileobj.close()
        except AttributeError:
            pass
        finally:
            self.f.close()
    def __getattr__(self, name):
        return getattr(self.f, name)
    def __iter__(self):
        return iter(self.f)
    def next(self):
        return next(self.f)

class FormatException(Exception):
    pass

def extract_reads_from_PE_fastq(fname_iPCR_PE1, fname_iPCR_PE2):
    """This function takes the 2 pair-end sequencing files and extracts the
    barcode making sure that the other read contains the transposon."""
    MIN_BRCD = 15
    MAX_BRCD = 25
    MIN_GENOME = 15

    # The known parts of the sequences are matched with a Levenshtein
    # automaton. On the reverse read, the end of the transposon
    # corresponds to a 34 bp sequence ending as shown below. We allow
    # up to 5 mismatches/indels. On the forward read, the only known
    # sequence is the CATG after the barcode, which is matched exactly.

    # Open a file to write
    fname_fasta = fname_iPCR_PE1.split('_fwd.fastq')[0] + '.fasta'

    # Substitution failed, append '.fasta' to avoid name collision.
    if fname_fasta == fname_iPCR_PE1:
        fname_fasta = fname_iPCR_PE1 + '.fasta'

    with gzopen(fname_iPCR_PE1) as f, gzopen(fname_iPCR_PE2) as g, \
            open(fname_fasta, 'w') as outf:
        # Aggregate iterator of f,g iterators -> izip(f,g).
        for lineno, (line1, line2) in enumerate(izip(f, g)):
            # Take sequence only.
            if lineno % 4 != 1:
                continue
            brcd = line1[:20]
            if not MIN_BRCD < len(brcd) < MAX_BRCD:
                continue
            # Lets relie on bwa mapping results to decide
            genome = line2.rstrip()
            if len(genome) < MIN_GENOME:
                continue
            outf.write('>%s\n%s\n' % (brcd, genome))

def call_bwa_mapper_on_fasta_file(fname_fasta, fname_genome_index):
    """This function takes the barcodes and sequence extracted from the
    sequencing files and calls bwa-mem to do the mapping with default
    settings to the Drosophila R6 reference genome"""

    outfname_mapped = re.sub(r'\.fasta', '.sam', fname_fasta)

    # System call to `bwa mem` with arguments and check the exit code.
    with open(outfname_mapped, 'w') as f:
        map_process = subprocess.Popen(['bwa', 'mem', '-t4','-L0,0',
                                        fname_genome_index,
                                        fname_fasta], stdout=f).wait()
        if int(map_process) < 0:
            sys.stderr.write("Error during the mapping\n")

def filter_mapped_reads(fname_mapped):
    """ This fuctions extracts the barcodes from the mapped file to feed
        them to starcode"""

    outfname_filtered = re.sub(r'\.sam', '_filtered.txt', fname_mapped)


    with open(fname_mapped) as f, open(outfname_filtered, 'w') as g:
        for line in f:
            if line[0] == '@':
                continue  # Get rid of header
            items = line.split()
            g.write('%s\n' % items[0])

def call_starcode_on_filtered_file(fname_filtered):
    """This function takes the barcodes contained in the first column of
    the mapped file and feed's them to starcode that clusters them."""

    fname_starcode = re.sub(r'_filtered.txt', '_starcode.txt', fname_filtered)

    # Substitution failed, append '_starcode.txt' to avoid name collision.
    if fname_filtered == fname_starcode:
        fname_starcode = fname_filtered + '_starcode.txt'

    # Call starcode (qsub-it?)
    if os.path.exists(fname_starcode):
        return fname_starcode
    starcode_process = subprocess.call([
          'starcode',
          '-t4',
          '--print-clusters',
          '-i', fname_filtered,
          '-o', fname_starcode,
          ])
    
    if int(starcode_process) < 0:
            sys.stderr.write("Error during Starcode call on: %s\n"
                             % fname_starcode)

def call_starcode_on_fastq_file(fname_fastq):
    ''' Extracts the gDNA,cDNA reads and spikes and runs stracode on them.'''
    MIN_BRCD = 15
    MAX_BRCD = 25

    brcd_outfname = re.sub(r'\.fastq.*', '_starcode.txt', fname_fastq)
    spk_outfname = re.sub(r'\.fastq.*', '_spikes_starcode.txt', fname_fastq)
    if brcd_outfname == fname_fastq:
        brcd_outfname = fname_fastq + '_starcode.txt'
    if spk_outfname == fname_fastq:
        spk_outfname = fname_fastq + '_spikes_starcode.txt'

    if os.path.exists(brcd_outfname) and os.path.exists(spk_outfname):
        return (brcd_outfname, spk_outfname)

    SPIKE = seeq.compile('CATGATTACCCTGTTATC', 2)
    barcode_tempf = tempfile.NamedTemporaryFile(delete=False)
    spike_tempf = tempfile.NamedTemporaryFile(delete=False)
    with gzopen(fname_fastq) as f:
        outf = None
        for lineno, line in enumerate(f):
            if lineno % 4 != 1:
                continue
            spike = SPIKE.match(line)
            if spike is not None:
                outf = spike_tempf
                outf.write(line[:spike.matchlist[0][0]] + '\n')
            else:
                outf = barcode_tempf
                outf.write(line[:20] + '\n')

    barcode_tempf.close()
    spike_tempf.close()

    # Call `starcode`.
    starcode_process = subprocess.call([
      'starcode',
      '-t4',
      '--print-clusters',
      '-i', barcode_tempf.name,
      '-o', brcd_outfname,
      ])

    if int(starcode_process) < 0:
        sys.stderr.write("Error during Starcode call on: %s\n"
                         % barcode_tempf.name)

    starcode_process = subprocess.call([
        'starcode',
        '-t4',
        '--print-clusters',
        '-i', spike_tempf.name,
        '-o', spk_outfname,
    ])

    if int(starcode_process) < 0:
        sys.stderr.write("Error during Starcode call on: %s\n"
                         % spk_outfname)

    # Delete temporary files.
    os.unlink(barcode_tempf.name)
    os.unlink(spike_tempf.name)

def collect_integrations(fname_starcode_out, fname_mapped, fname_bcd_dictionary,
                        fname_cDNA, fname_cDNA_spike,
                        fname_gDNA, fname_gDNA_spike):
    """This function reads the starcode output and changes all the barcodes
    mapped by their canonicals while it calculates the mapped distance
    rejecting multiple mapping integrations or unmmaped ones. It also
    counts the frequency that each barcode is found in the mapped data
    even for the non-mapping barcodes."""


    # temporary fix to work with makefile
    args = [(fname_cDNA,fname_cDNA_spike),
            (fname_gDNA,fname_gDNA_spike)]

    # First, open the barcode-promoter dictionary
    bcd_promd = pickle.load(open(fname_bcd_dictionary, "rb"))

    fname_insertions_table = re.sub(r'\.sam', '_insertions.txt',
                                    fname_mapped)
    # Substitution failed, append '_insertions.txt' to avoid name conflict.
    if fname_insertions_table == fname_mapped:
        fname_insertions_table = fname_mapped + '_insertions.txt'

    def dist(intlist):
        intlist.sort()
        try:
            if intlist[0][0] != intlist[-1][0]:
                return float('inf')
            return intlist[-1][1] - intlist[0][1]
        except IndexError:
            return float('inf')

    canonical = dict()
    with open(fname_starcode_out) as f:
        for line in f:
            items = line.split()
            for brcd in items[2].split(','):
                canonical[brcd] = items[0]

    counts = defaultdict(lambda: defaultdict(int))
    ISREV = 0b10000
    with open(fname_mapped) as f:
        for line in f:
            if line[0] == '@':
                continue
            items = line.split()
            try:
                barcode = canonical[items[0]]
            except KeyError:
                continue
            if items[2] == '*':
                position = ('', 0)
            else:
                # GTTACATCGGTTAATAGATA 16  2L  9743332 60  9S32M [...]
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
                counts[barcode][ident] += 1

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
    for (fname, ignore) in args:
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
        for brcd in sorted(integrations, key=lambda x:
                           (integrations.get(x), x)):
            (chrom, pos, strand, promoter), total = integrations[brcd]
            mapped += 1
            outf.write('%s\t%s\t%s\t%d\t%d\t%s\n' %
                       (brcd, chrom, strand, pos, total, promoter))
        for fname, ignore in args:
            outf.write('\t' + str(reads[fname][brcd]))
            outf.write('\n')

        # Now add the spikes if the experiment was spiked, otherwise continue.
        N = len(args)
        for i in range(N):
            (ignore, fname) = args[i]
            with open(fname) as f:
                for line in f:
                    try:
                        items = line.rstrip().split('\t')
                        array = ['0'] * N
                        array[i] = items[1]
                        outf.write('%s\tspike\t*\t0\t0\t' % items[0])
                        outf.write('\t'.join(array) + '\n')
                    except IndexError:
                        continue
    print('%s: mapped:%d, unmapped:%d\n'%(fname_mapped, mapped, unmapped))
