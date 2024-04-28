#!/bin/bash

mkdir -p masks
rm -f masks/*.txt
touch masks/ref-plane0.txt masks/ref-plane1.txt  masks/ref-plane2.txt  masks/dut-plane3.txt  masks/ref-plane4.txt  masks/ref-plane5.txt  masks/ref-plane6.txt masks/dut.txt

corry -c configs/createmask.conf
corry -c configs/prealign.conf
corry -c configs/align.conf
corry -c configs/analyse.conf