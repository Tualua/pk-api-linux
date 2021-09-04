#!/bin/bash
for ((h = $1; h <= $2; h++ ))
do
    echo "Removing OS clones for vm$h"
    zfs destroy -r data2/kvm/desktop/desktop-vm$h
done