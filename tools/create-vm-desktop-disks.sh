#!/bin/bash
for ((h = $1; h <= $2; h++ ))
do
    echo "Creating OS clones for vm$h"
    zfs clone data2/kvm/desktop/desktop-MCIO@7 data2/kvm/desktop/desktop-vm$h
done