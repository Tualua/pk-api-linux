#!/bin/bash
for ((h = $1; h <= $2; h++ ))
do
    echo "Creating OS clones for vm$h"
    zfs clone data/reference@ver2_14430 data/kvm/desktop/games-vm$h
done