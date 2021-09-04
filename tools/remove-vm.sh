#!/bin/bash
# ./remove-vm.sh <from> <to> <OS pool> <Games pool>
for ((h = $1; h <= $2; h++ ))
do
    echo "Removing clones for vm$h"
    zfs destroy -r $3/kvm/desktop/desktop-vm$h
    zfs destroy -r $4/kvm/desktop/games-vm$h
done