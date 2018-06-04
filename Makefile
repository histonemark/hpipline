SHELL:=/bin/bash

# SPIKE
SPIKE=CATGATTACCCTGTTATC

# input files
prom_bcd_dict=/users/gfilion/mcorrales/HPIP/libraries/prom_bcd.p
genome=/users/gfilion/mcorrales/HPIP/dm4R6/dmel-all-chromosome-r6.15.fasta
iPCR_basename=@iPCR_basename@
cDNA_basename=@cDNA_basename@
gDNA_basename=@gDNA_basename@

# build file names based on base names
iPCR_fwd=$(iPCR_basename)_fwd.fastq
iPCR_rev=$(iPCR_basename)_Rev.fastq
cDNA_fastq=$(cDNA_basename).fastq
gDNA_fastq=$(gDNA_basename).fastq

# intermediate files
iPCR_starcode=$(iPCR_basename)_starcode.txt
iPCR_counts_dict=$(iPCR_basename)_counts_dict.p
iPCR_sam=$(iPCR_basename).sam
cDNA_starcode=$(cDNA_basename)_starcode.txt
cDNA_spikes_starcode=$(cDNA_basename)_spikes_starcode.txt
gDNA_starcode=$(gDNA_basename)_starcode.txt
gDNA_spikes_starcode=$(gDNA_basename)_spikes_starcode.txt

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

# final target
iPCR_insertions=$(iPCR_basename)_insertions.txt

# program names
hpipline=python hpipline.py
starcode=starcode -t4
seeq=seeq
extract_reads_from_fastq=sed -n '2~4p'
extract_bcd=grep -o '^.\{20\}'

.PHONY : all spikes clean cleanintermediate cleanlog cleanall

all : $(iPCR_insertions) spikes

spikes : $(cDNA_spikes_starcode) $(gDNA_spikes_starcode)

cleanlog :
	rm -rf *.log

cleanintermediate :
	rm -rf \
	  $(INTERMEDIATE_IPCR)\
	  $(INTERMEDIATE_CDNA)\
	  $(INTERMEDIATE_GDNA)

clean : cleanintermediate cleanlog

cleanall : clean
	rm -rf $(iPCR_insertions)

####################################
# MAP READS
####################################
$(iPCR_sam) : $(iPCR_fwd) $(iPCR_rev) $(genome)
	paste -d"\n" \
	  <($(extract_reads_from_fastq) $(iPCR_fwd) | $(extract_bcd) | sed 's/^/>/')\
	  <($(extract_reads_from_fastq) $(iPCR_rev)) |\
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
	$(extract_reads_from_fastq) $(gDNA_fastq) |\
	  $(seeq) -i -d2 $(SPIKE) |\
	  $(extract_bcd) |\
	  $(starcode) -d2 --print-clusters 1> $(gDNA_starcode) 2> $(subst .txt,.log,$@)

$(gDNA_spikes_starcode) : $(gDNA_fastq)
	$(extract_reads_from_fastq) $(gDNA_fastq) |\
	  $(seeq) -rd2 $(SPIKE) $(gDNA_fastq) |\
	  $(starcode) -d2 1> $(gDNA_spikes_starcode) 2> $(subst .txt,.log,$@)

$(cDNA_starcode) : $(cDNA_fastq)
	$(extract_reads_from_fastq) $(cDNA_fastq) |\
	  $(seeq) -i -d2 $(SPIKE) |\
	  $(extract_bcd) |\
	  $(starcode) -d2 --print-clusters 1> $(cDNA_starcode) 2> $(subst .txt,.log,$@)

$(cDNA_spikes_starcode) : $(cDNA_fastq)
	$(extract_reads_from_fastq) $(cDNA_fastq) |\
	  $(seeq) -rd2 $(SPIKE) $(cDNA_fastq) |\
	  $(starcode) -d2 1> $(cDNA_spikes_starcode) 2> $(subst .txt,.log,$@)

####################################
# COLLECT INTEGRATIONS
####################################
$(iPCR_counts_dict) : $(iPCR_starcode) $(iPCR_sam) $(prom_bcd_dict)
	@$(hpipline) generate_counts_dict $^ 2> $(subst .p,.log,$@)

$(iPCR_insertions) : $(iPCR_counts_dict) $(cDNA_starcode) $(gDNA_starcode)
	@$(hpipline) collect_integrations $^ 2> collect_integrations.log
