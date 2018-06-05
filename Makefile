SHELL:=/bin/bash

# SPIKE
SPIKE=CATGATTACCCTGTTATC

# input files
libname=@LIBNAME@
# prom_bcd_dict=/users/gfilion/mcorrales/HPIP/libraries/prom_bcd.p
prom_bcd_dict=/mnt/ant-login/mcorrales/HPIP/libraries/prom_bcd.p
genome=/mnt/ant-login/mcorrales/HPIP/dm4R6/dmel-all-chromosome-r6.15.fasta

# build file names based on base names
iPCR_fwd=iPCR-fwd.fastq.gz
iPCR_rev=iPCR-rev.fastq.gz
cDNA_fastq=cDNA.fastq.gz
gDNA_fastq=gDNA.fastq.gz

# intermediate files
iPCR_starcode=iPCR-starcode.txt
iPCR_counts_dict=iPCR-counts_dict.p
iPCR_sam=iPCR.sam
cDNA_starcode=cDNA-starcode.txt
cDNA_spikes_starcode=cDNA-spikes_starcode.txt
gDNA_starcode=gDNA-starcode.txt
gDNA_spikes_starcode=gDNA-spikes_starcode.txt

# groups of files
INTERMEDIATE_IPCR=\
	     $(iPCR_sam)\
	     $(iPCR_counts_dict)\
	     $(iPCR_starcode)

INTERMEDIATE_CDNA=\
	     $(cDNA_starcode)\
	     $(cDNA_spikes_starcode)

INTERMEDIATE_GDNA=\
	     $(gDNA_starcode)\
	     $(gDNA_spikes_starcode)

# program names
starcode=starcode -t4
seeq=seeq
extract_reads_from_fastq=sed -n '2~4p'
extract_bcd=grep -o '^.\{20\}'

.PHONY : all spikes clean cleanintermediate cleanlog

all : $(iPCR_starcode) $(cDNA_starcode) $(gDNA_starcode)

spikes : $(cDNA_spikes_starcode) $(gDNA_spikes_starcode)

cleanlog :
	rm -rf *.log

cleanintermediate :
	rm -rf \
	  $(INTERMEDIATE_IPCR)\
	  $(INTERMEDIATE_CDNA)\
	  $(INTERMEDIATE_GDNA)

clean : cleanintermediate cleanlog

####################################
# MAP READS
####################################
$(iPCR_sam) : $(iPCR_fwd) $(iPCR_rev) $(genome)
	paste -d"\n" \
	  <(zcat $(iPCR_fwd) | $(extract_reads_from_fastq) | $(extract_bcd) | sed 's/^/>/')\
	  <(zcat $(iPCR_rev) | $(extract_reads_from_fastq)) |\
	  bwa mem -t4 -L0,0 $(genome) - 1> $@ 2> $(subst .sam,.bwa.log,$@)

####################################
# STARCODE ON iPCR READS
####################################
$(iPCR_starcode) : $(iPCR_sam)
	grep -v '@' $(iPCR_sam) |\
	  awk '{ print $$1 }' |\
	  $(starcode) -d2 --print-clusters 1> $@ 2> $(subst .txt,.log,$@)

####################################
# STARCODE ON FASTQ
####################################
$(gDNA_starcode) : $(gDNA_fastq)
	zcat $(gDNA_fastq) |\
	  $(extract_reads_from_fastq) |\
	  $(seeq) -i -d2 $(SPIKE) |\
	  $(extract_bcd) |\
	  $(starcode) -d2 --print-clusters 1> $(gDNA_starcode) 2> $(subst .txt,.log,$@)

$(gDNA_spikes_starcode) : $(gDNA_fastq)
	zcat $(gDNA_fastq) |\
	$(extract_reads_from_fastq) |\
	  $(seeq) -rd2 $(SPIKE) $(gDNA_fastq) |\
	  $(starcode) -d2 1> $(gDNA_spikes_starcode) 2> $(subst .txt,.log,$@)

$(cDNA_starcode) : $(cDNA_fastq)
	zcat $(cDNA_fastq) |\
	$(extract_reads_from_fastq) |\
	  $(seeq) -i -d2 $(SPIKE) |\
	  $(extract_bcd) |\
	  $(starcode) -d2 --print-clusters 1> $(cDNA_starcode) 2> $(subst .txt,.log,$@)

$(cDNA_spikes_starcode) : $(cDNA_fastq)
	zcat $(cDNA_fastq) |\
	$(extract_reads_from_fastq) |\
	  $(seeq) -rd2 $(SPIKE) $(cDNA_fastq) |\
	  $(starcode) -d2 1> $(cDNA_spikes_starcode) 2> $(subst .txt,.log,$@)
