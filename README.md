# pk-api-linux
PK API Linux Port

I did't change Perl API, just wrote `ctladm` to `targetcli` commands translator and configs for `uwsgi`

I didn't find ctld's Port Number in LIO so I used backstores names (only numeric names)

Tested on Ubuntu 20.04.1

Installation manual is in INSTALL.md

# Known bugs

- No pool auto import
https://github.com/openzfs/zfs/issues/11450
    
# TODO

- Test Oracle Linux 8.3
- Scripts to create initial clones, luns and initiators
