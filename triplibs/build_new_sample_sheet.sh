#!/bin/bash
# make a bcl2fastq run with a sample sheet that contains only the
# information on how to detect a no-DNA case

# check proper invocation
if [ $# -ne 1 ]; then
  echo "Usage: build_new_sample_sheet <rep_name>" 1>&2
  exit 1
fi

# get replicate name and cd to the corresponding directory
rep_name=$1
root_dir=$(pwd)
mc_datadir="/mnt/ant-login/mcorrales/HPIP"
datadir="$mc_datadir/iPCR/HPIP_iPCR_$rep"
cd $datadir

# build new sample sheet
ss_noDNA="SampleSheet.csv.noDNA"
rm -rf $ss_noDNA
echo "[Data]" >> $ss_noDNA
echo "Lane,SampleID,SampleName,index,index2" >> $ss_noDNA
echo "1,1,noDNA,GGGGGG" >> $ss_noDNA
echo "2,1,noDNA,GGGGGG" >> $ss_noDNA
echo "3,1,noDNA,GGGGGG" >> $ss_noDNA
echo "4,1,noDNA,GGGGGG" >> $ss_noDNA

# make the noDNA sample sheet the "current" one
cp $ss_noDNA SampleSheet.csv

# invoke bcl2fastq
bcl2fastq --no-lane-splitting

# once that is done, process the output file and build the noDNA-starcode.txt
# table
fastq_in="Data/Intensities/BaseCalls/Undetermined_S0_R1_001.fastq.gz"
zcat $fastq_in | sed -n '1~4p' | grep -o '[GATC]*$' | starcode -d0 > noDNA-starcode.txt

# now we can build the new Sample Sheet
python make_new_sample_sheet.py

# return to original directory
cd $root_dir
