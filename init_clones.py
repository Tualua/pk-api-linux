#!/usr/bin/python3

import argparse
from rtslib_fb import (Target, TPG, NodeACL, FabricModule, BlockStorageObject,
                       RTSRoot, NetworkPortal, LUN, MappedLUN, RTSLibError,
                       RTSLibNotInCFS, NodeACLGroup)
from configparser import ConfigParser


def read_config(inifile="/etc/ctladm/ctladm.ini"):
    config = ConfigParser()
    ctladm_settings = {}
    config.read(inifile)
    sections = config.sections()
    if sections:
        for section in sections:
            ctladm_settings[section] = {}
            for item in config.items(section):
                ctladm_settings[section][item[0]] = item[1]
    else:
        print('ERROR: Empty config file!')
    return ctladm_settings


def create_clones(vm):
    print("Creating clones for {}".format(vm))


def create_initiators(vm):
    print("Creating initiators for {}".format(vm))


def main(args):
    print("Welcome!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PlayKey SDS initial clones and initiators creator')
    parser.add_argument('command', type=str, action='store',
                        help='ctladm command')
    args = parser.parse_args()
    main(args)