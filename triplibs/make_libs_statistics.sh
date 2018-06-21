#!/bin/bash

# check for proper invocation
if [ $# -ne 2 ]; then
  echo "Usage: make_libs_statistics <hpip_root> <rep>" 1>&2
  exit 1
fi

# get parameters from command line
hpip_root=$1
rep=$2

# build directory name
rep_datadir=$hpip_root/data/triplibs/$rep

# output file name
out_fname=$rep_datadir/libs_statistics.txt
rm -f $out_fname

# write header of file
echo "# n_iPCR cDNA gDNA both" >> $out_fname

# cycle on all the libraries
root_dir=$(pwd)
for libdir in $(find $rep_datadir -mindepth 1 -maxdepth 1 -type d -name "lib*"); do
  cd $libdir

  # build lib number based on the library directory name
  lib=${libdir#$rep_datadir/lib}

  # reset counters
  let n=0
  let cDNA=0
  let gDNA=0
  let both=0

  # read the iPCR barcodes and evaluate whether those barcodes were found in the
  # cDNA and gDNA experiments, and increment counters
  for bcd in $(awk '{ print $1 }' iPCR-starcode.txt); do
    grep -q $bcd cDNA-starcode.txt
    isincDNA=$?
    grep -q $bcd gDNA-starcode.txt
    isingDNA=$?
    # echo $isincDNA $isingDNA
    if [ "$isincDNA" = 0 ]; then let cDNA=cDNA+1; fi
    if [ "$isingDNA" = 0 ]; then let gDNA=gDNA+1; fi
    if [ "$isingDNA" = 0 ] && [ "$isincDNA" = 0 ]; then let both=both+1; fi
    let n=n+1
  done
  echo $n $cDNA $gDNA $both >> $out_fname
  cd $root_dir
done
