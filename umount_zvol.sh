#!/bin/bash
cd ~
/bin/umount /mnt/host/boot
/bin/umount /mnt/host/sys
/sbin/kpartx -dv /dev/loop1
/sbin/losetup -D
