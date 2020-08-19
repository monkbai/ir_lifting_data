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

#recoverFBOffO0(){
#    command="cd $S2EDIR/s2e-out-$1 &&  ../scripts/doNotOptimize.sh -f none captured.bc $1-recovered-FBOff-O0-$2.bc"
#    bash ./docker/run $command
#    cp $S2EDIR/s2e-out-$1/$1-recovered-FBOff-O0-$2 $SPECBINS    
#    cp -r $S2EDIR/s2e-out-$1 $RECOVEREDDIRS/s2e-out-$1-recovered-FBOff-O0-$2
#}

recoverFBOnO0(){
    command="cd $S2EDIR/s2e-out-$1-$3 &&  ../scripts/doNotOptimize.sh captured.bc $1-recovered-FBOn-O0-$2.bc"
    bash ./docker/run $command
    cp $S2EDIR/s2e-out-$1-$3/$1-recovered-FBOn-O0-$2 $SPECBINS
    cp -r $S2EDIR/s2e-out-$1-$3 $RECOVEREDDIRS/s2e-out-$1-recovered-FBOn-O0-$2
}

#recoverFBOffO3(){
#    command="cd $S2EDIR/s2e-out-$1 &&  ../scripts/optimize.sh -f none captured.bc $1-recovered-FBOff-O3-$2.bc"
#    bash ./docker/run $command
#    cp $S2EDIR/s2e-out-$1/$1-recovered-FBOff-O3-$2 $SPECBINS
#    cp -r $S2EDIR/s2e-out-$1 $RECOVEREDDIRS/s2e-out-$1-recovered-FBOff-O3-$2
#}

#recoverFBOnO3(){
#    command="cd $S2EDIR/s2e-out-$1 &&  ../scripts/optimize.sh captured.bc $1-recovered-FBOn-O3-$2.bc"
#    bash ./docker/run $command
#    cp $S2EDIR/s2e-out-$1/$1-recovered-FBOn-O3-$2 $SPECBINS
#    cp -r $S2EDIR/s2e-out-$1 $RECOVEREDDIRS/s2e-out-$1-recovered-FBOn-O3-$2
#}

# TEST 1
specBin=gcc_base.amd64-m32-gcc42-nn
input=input/gcc/cp-decl.i
lift $specBin $input 280

# TEST 2
specBin=gcc_base.amd64-m32-gcc42-nn
input=input/gcc/166.i
lift $specBin $input

# TEST 3
specBin=gcc_base.amd64-m32-gcc42-nn
input=input/gcc/c-typeck.i
lift $specBin $input

# TEST 4
specBin=gcc_base.amd64-m32-gcc42-nn
input=input/gcc/expr.i
lift $specBin $input

# TEST 5
specBin=gcc_base.amd64-m32-gcc42-nn
input=input/gcc/g23.i
lift $specBin $input

