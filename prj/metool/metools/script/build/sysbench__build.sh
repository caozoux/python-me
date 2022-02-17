#!/bin/bash

cd ./work/sysbench-master/
./autogen.sh
./configure
make -j16
