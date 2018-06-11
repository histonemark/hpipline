#!/bin/bash

# generate the combination of promoter names
prom_classes="A B C D E F G H"
prom_libs=$(seq 12)
mc_data_dir="/mnt/ant-login/mcorrales/HPIP"
out_dir="/home/rcortini/work/CRG/projects/hpip/data/pbd"
lib_dir=$mc_data_dir/libraries

for prom_class in $prom_classes; do

  # generate library name
  libname=HPIP_bcds_"$prom_class"1to"$prom_class"12

  # cycle on all the promoters in that library (from 1 to 12)
  for prom_lib in $prom_libs; do

    # build file names of input fastq files
    prom_name="Promoter$prom_class$prom_lib"
    datadir=$lib_dir/$libname/Data/Intensities/BaseCalls
    fastqs=$(find $datadir -name "$prom_name"*.fastq.gz)
    if [ -z "$fastqs" ]; then
      echo "$prom_name not found"
      continue
    fi

    # extract the barcodes from all lanes associated to the current promoter
    # and write them to a file that contains the name of the promoter and a 
    # "-to_starcode.txt" suffix
    to_starcode="$datadir/$prom_name-to_starcode.txt"
    rm -rf $to_starcode
    echo "Processing $prom_name"
    for fastq in $fastqs; do
      zcat $fastq | sed -n '2~4p' | grep -o '^.\{20\}'>> $to_starcode
    done

    # check if output starcode directory exists, and if not create it
    starcode_out_dir=$out_dir/Starcoded_proms
    if ! test -e $starcode_out_dir; then
      mkdir -p $starcode_out_dir
    fi

    # invoke starcode on the file kust created
    starcode_out="$starcode_out_dir/$prom_name-starcoded.txt"
    starcode -t8 -d2 --print-clusters -i $to_starcode -o $starcode_out
  done
done
