#!/bin/bash

set -e
cd $S2EDIR
#SPECBINS=$HOME/recovered-spec-bins-newIMGnewS2E
#RECOVEREDDIRS=$HOME/recovered-spec-dirs-newIMGnewS2E
#mkdir -p $SPECBINS
#mkdir -p $RECOVEREDDIRS


lift(){
    echo ">> Lifting $@..."
    bash ./qemu/cmd-debian.sh --vnc 0 $@
}


recoverFBOnO0(){
    command="cd $S2EDIR/s2e-out-$1-$3 &&  ../scripts/doNotOptimize.sh captured.bc $1-recovered-FBOn-O0-$2.bc"
    bash ./docker/run $command
    cp $S2EDIR/s2e-out-$1-$3/$1-recovered-FBOn-O0-$2 $SPECBINS
    cp -r $S2EDIR/s2e-out-$1-$3 $RECOVEREDDIRS/s2e-out-$1-recovered-FBOn-O0-$2
}


# TEST 1
specBin=bzip2_base.amd64-m32-gcc42-nn
input=input/bzip2/input.source
lift $specBin $input 280
#recoverFBOnO0 $specBin input.source-280 1
# TEST 2
specBin=bzip2_base.amd64-m32-gcc42-nn
input=input/bzip2/liberty.jpg
lift $specBin $input 30
#recoverFBOnO0 $specBin liberty.jpg-30 2
# TEST 3 
specBin=bzip2_base.amd64-m32-gcc42-nn
input=input/bzip2/chicken.jpg
lift $specBin $input 30
#recoverFBOnO0 $specBin chicken.jpg-30 3



