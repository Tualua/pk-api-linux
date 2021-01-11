# pk-api-linux
PK API Linux Port

I did't change Perl API, just wrote `ctladm` to `targetcli` commands translator and configs for `uwsgi`

I didn't find ctld's Port Number in LIO so I used backstores names (only numeric names)

Tested on Ubuntu 20.04.1 and Oracle Linux 8.3

Installation manual: [Ubuntu 20.04](INSTALL-UBUNTU20.04.md), [Oracle Linux 8.3](INSTALL-OL8.3.md)

# Known bugs

- No pool auto import on Ubuntu 20.04
https://github.com/openzfs/zfs/issues/11450
    
# TODO

- Scripts to create initial clones, luns and initiators
