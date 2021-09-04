#!/bin/bash
/sbin/losetup loop1 /dev/zvol/data/hv/$1-boot -b 4096
/sbin/kpartx -av /dev/loop1
/bin/mount /dev/mapper/loop1p1 /mnt/host/boot
/bin/mount /dev/mapper/loop1p4 /mnt/host/sys
cd /mnt
