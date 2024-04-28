#!/bin/bash

rm -rf contrib/*
mkdir -p contrib/

if [ "$#" -ge 1 ] && [ "$1" == "SSH" ]
then
    git clone ssh://git@gitlab.cern.ch:7999/alice-its3-wp3/eudaq2.git                      contrib/eudaq2
    # git clone ssh://git@gitlab.cern.ch:7999/chunzhen/corryvreckan.git                      contrib/corryvreckan
    git clone ssh://git@gitlab.cern.ch:7999/alice-its3-wp3/apts-dpts-ce65-daq-software.git contrib/apts-dpts-ce65-daq-software
else
    git clone https://gitlab.cern.ch/alice-its3-wp3/eudaq2.git                      contrib/eudaq2
    # git clone https://gitlab.cern.ch/chunzhen/corryvreckan.git                      contrib/corryvreckan
    git clone https://gitlab.cern.ch/alice-its3-wp3/apts-dpts-ce65-daq-software.git contrib/apts-dpts-ce65-daq-software
fi

