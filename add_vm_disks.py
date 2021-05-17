#!/usr/bin/python3
import argparse
import subprocess


# Wrapper for shell command excecution
def exec_shell_command(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    return stdout.decode().split('\n')


def get_last_snapshot(dataset):
    zfs_cmd = "zfs list -t snap -H -o name {}".format(dataset)
    data = exec_shell_command(zfs_cmd)[:-1]
    result = data[-1]
    return result


def create_vm_clones(vm, os, games):
    os_dataset = "data/kvm/desktop/desktop-vm{}".format(vm)
    games_dataset = "data/kvm/desktop/games-vm{}".format(vm)
    zfs_cmd = "zfs list -H -o name {}".format(os_dataset)
    check = exec_shell_command(zfs_cmd)[:-1]
    if "dataset does not exist" in check[0]:
        zfs_cmd = "zfs clone {} {}".format(os, os_dataset)
        os_result = exec_shell_command(zfs_cmd)[:-1]
        if len(os_result) > 0:
            print("Error creating clone desktop-vm{}!\n\t{}".format(vm, os_result))
    else:
        print("Clone desktop-vm{} already exists!".format(vm))
    zfs_cmd = "zfs list -H -o name {}".format(games_dataset)
    check = exec_shell_command(zfs_cmd)[:-1]
    if "dataset does not exist" in check[0]:
        zfs_cmd = "zfs clone {} {}".format(games, games_dataset)
        games_result = exec_shell_command(zfs_cmd)[:-1]
        if len(games_result) > 0:
            print("Error creating clone games-vm{}!\n\t{}".format(vm, games_result))
    else:
        print("Clone games-vm{} already exists!".format(vm))


def read_scst_config(path):
    file_scst_config = open(path, "r")
    scst_config = file_scst_config.read()  # .replace("\t", "").split("\n")
    file_scst_config.close()
    return scst_config


def write_scst_config(config, path):
    file_scst_config = open(path, "w")
    file_scst_config.write(config)
    file_scst_config.close()


def add_device_config(config, name):
    filename = "/dev/zvol/data/kvm/desktop/{}".format(name)
    if config.find(filename) <= 0:
        dev_config = "\tDEVICE {} {{\n" \
                    "\t\tfilename {}\n" \
                    "\t\tnv_cache 1\n" \
                    "\t\trotational 0\n" \
                    "\t\tt10_vend_id FREE_TT\n" \
                    "\t}}\n".format(name, filename, bs)
        # print(dev_config)
        pos1 = config.find("TARGET_DRIVER")
        pos2 = config.rfind("}", 0, pos1)-1
        result = config[:pos2] + dev_config + config[pos2:]
        # print(result)
    else:
        print("Device {} already defined in config!".format(name))
        result = config
    return result


def add_target_config(config, device, host, portal_addr):
    iqn = "iqn.2016-04.net.playkey.iscsi:{}".format(device)
    if config.find(iqn) <= 0:
        iscsi_initiator = "iqn.2020-09.io.minecolo.iscsi:hv:{}".format(host)
        tgt_config = "\tTARGET {} {{\n" \
                     "\t\tQueuedCommands 128\n" \
                     "\t\tallowed_portal {}\n" \
                     "\t\tenabled 1\n" \
                     "\t\tGROUP allowed_ini {{\n" \
                     "\t\t\tLUN 0 {}\n" \
                     "\t\t\tINITIATOR {}\n" \
                     "\t\t}}\n" \
                     "\t}}\n".format(iqn, portal_addr, device, iscsi_initiator)
        # print(tgt_config)
        pos = config.rfind("}")-1
        result = config[:pos] + tgt_config + config[pos:]
        # print(result)
    else:
        print("Target {} already defined in config!".format(iqn))
        result = config
    return result


def main(args):
    scst_config = read_scst_config(args.scst_config)
    snap_games = get_last_snapshot("data/reference")
    snap_os = get_last_snapshot("data/kvm/desktop/{}".format(args.os))
    create_vm_clones(args.vm, snap_os, snap_games)
    scst_config = add_device_config(scst_config, "desktop-vm{}".format(args.vm))
    scst_config = add_device_config(scst_config, "games-vm{}".format(args.vm))
    scst_config = add_target_config(scst_config, "desktop-vm{}".format(args.vm), args.kvm_host, args.portal_addr)
    scst_config = add_target_config(scst_config, "games-vm{}".format(args.vm), args.kvm_host, args.portal_addr)
    write_scst_config(scst_config, args.scst_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PlayKey SDS VM disks config manager')
    parser.add_argument('--vm', type=int, action='store', dest='vm', help='VM number')
    parser.add_argument('--os', type=str, action='store', dest="os", help='Windows snapshot name')
    parser.add_argument('--host', type=str, action='store', dest="kvm_host", help='KVM host name')
    parser.add_argument('--portal', type=str, action='store', dest="portal_addr", help='iSCSI portal address')
    parser.add_argument('--config', type=str, action='store', dest="scst_config", default="/etc/scst.conf",
                        help='SCST config path')
    args = parser.parse_args()
    main(args)
