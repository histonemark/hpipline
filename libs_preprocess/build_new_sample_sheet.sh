#!/bin/bash

# make a bcl2fastq run with a sample sheet that contains only the
# information on how to detect a no-DNA case

ss_noDNA="SampleSheet.csv.noDNA"

echo "[Data]" >> $ss_noDNA
echo "Lane,SampleID,SampleName,index,index2" >> $ss_noDNA
echo "1,1,noDNA,GGGGGG" >> $ss_noDNA
echo "2,1,noDNA,GGGGGG" >> $ss_noDNA
echo "3,1,noDNA,GGGGGG" >> $ss_noDNA
echo "4,1,noDNA,GGGGGG" >> $ss_noDNA

# make the noDNA sample sheet the "current" one
cp $ss_noDNA SampleSheet.csv

# invoke bcl2fastq
bash bcl2fastq_invocation.sh

# once that is done, process the output file and build the noDNA-starcode.txt
# table
fastq_in="Data/Intensities/BaseCalls/Undetermined_S0_R1_001.fastq.gz"
zcat $fastq_in | sed -n '1~4p' | grep -o '[GATC]*$' | starcode -d0 > noDNA-starcode.txt

# now we can build the new Sample Sheet
python make_new_sample_sheet.py
