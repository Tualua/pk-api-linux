#!/bin/sh

SCST_CFG=/etc/scst.conf
SCST_SYSCFG=/etc/sysconfig/scst

[ ! -e $SCST_SYSCFG ] || . $SCST_SYSCFG

SCST_MODULES="scst"

[ -e $SCST_CFG ] || return 0

_nonblanks="[^[:blank:]]\{1,\}"
_blanks="[[:blank:]]\{1,\}"
_optblanks="[[:blank:]]*"

SCST_MODULES="$SCST_MODULES `sed -n -e 's/^HANDLER'"${_blanks}"'\('"${_nonblanks}"'\)'"${_blanks}"'{'"${_optblanks}"'$/\1/p' \
                     -e 's/^\[HANDLER'"${_blanks}"'\('"${_nonblanks}"'\)\]$/\1/p' $SCST_CFG \
    | while read h; do
        case "$h" in
            dev_cdrom)      echo scst_cdrom;;
            dev_changer)    echo scst_changer;;
            dev_disk*)      echo scst_disk;;
            dev_modisk*)    echo scst_modisk;;
            dev_processor)  echo scst_processor;;
            dev_raid)       echo scst_raid;;
            dev_tape*)      echo scst_tape;;
            dev_user)       echo scst_user;;
            vdisk*|vcdrom)  echo scst_vdisk;;
            *)              echo "$h";;
        esac
    done | sort -u` \
    `sed -n 's/^TARGET_DRIVER'"${_blanks}"'\('"${_nonblanks}"'\)'"${_blanks}"'{'"${_optblanks}"'$/\1/p' $SCST_CFG | while read d; do
        case "$d" in
            iscsi)    echo iscsi_scst;;
            qla2x00t) echo qla2x00tgt;;
            copy_manager) ;;
            *)        echo "$d";;
        esac
    done | sort -u` \
    $SCST_TARGET_MODULES"

/sbin/modprobe -a $SCST_MODULES > /dev/null 2>&1
