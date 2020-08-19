#!/bin/bash

set -e
cd $S2EDIR
#SPECBINS=$HOME/recovered-spec-bins-newIMGnewS2E
#RECOVEREDDIRS=$HOME/recovered-spec-dirs-newIMGnewS2E
#mkdir -p $SPECBINS
#mkdir -p $RECOVEREDDIRS

#bash ./docker/run 'export MEM_AMOUNT=64; echo $MEM_AMOUNT; lscpu'

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
specBin=mcf_base.amd64-m32-gcc42-nn
input=input/mcf/inp.in
lift $specBin $input

