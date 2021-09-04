#!/bin/bash
# ./remove-vm-desktop-disks.sh <from> <to> <zfs pool>
for ((h = $1; h <= $2; h++ ))
do
    echo "Removing OS clones for vm$h"
    zfs destroy -r $3/kvm/desktop/desktop-vm$h
done