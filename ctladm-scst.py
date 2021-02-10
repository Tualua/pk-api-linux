#!/usr/bin/python3

import argparse
from xml.dom import minidom
from collections import defaultdict
import subprocess
import os
from pathlib import Path


SYSFS_SCST_ROOT = "/sys/kernel/scst_tgt"
SYSFS_SCST_DEVICES = "{}/devices".format(SYSFS_SCST_ROOT)
SYSFS_SCST_LUNS = "/sys/kernel/scst_tgt/targets/copy_manager/"
"copy_manager_tgt/luns"
SYSFS_SCST_ISCSI_TGTS = "{}/targets/iscsi".format(SYSFS_SCST_ROOT)
SYSFS_SCST_LUN0_DEV = "ini_groups/allowed_ini/luns/0/device"
SYSFS_SCST_LUNS_MGMT = "ini_groups/allowed_ini/luns/mgmt"


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def get_iscsi_wwn(link):
    a = link.find("iqn", 0)
    if a > -1:
        b = link.find("/", a+1)
        if b > 0:
            return link[a:b]
        else:
            return link[a:]
    else:
        return None


def scst_get_devices():
    devices = [device for device in os.listdir(SYSFS_SCST_DEVICES)
               if os.path.isdir(os.path.join(SYSFS_SCST_DEVICES, device))]
    return devices


def scst_get_iscsi_targets():
    targets = [target for target in os.listdir(SYSFS_SCST_ISCSI_TGTS)
               if os.path.isdir(os.path.join(SYSFS_SCST_ISCSI_TGTS, target))]
    return targets


def scst_get_target_sessions(target):
    sessions_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target, "sessions")
    sessions = [session for session in os.listdir(sessions_path)
                if os.path.isdir(os.path.join(sessions_path, session))]
    return sessions


def scst_get_portal_addr(target):
    portal_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target, "allowed_portal")
    try:
        portal_file = open(portal_path, 'r')
        portal_value = portal_file.read().split("\n")[0]
        portal_file.close()
    except Exception:
        # allowed_portal is not defined
        portal_value = "0.0.0.0"
        pass
    return portal_value


def scst_get_device_params(device):
    result = defaultdict(lambda: "")
    device_path = os.path.join(SYSFS_SCST_DEVICES, device)
    params = [param for param in os.listdir(device_path)
              if not os.path.isdir(os.path.join(device_path, param))]
    for param in params:
        try:
            param_file = open(os.path.join(device_path, param), 'r')
            param_value = param_file.read().replace("\n", "").replace("[key]", "")
            param_file.close()
            result[param] = param_value
        except Exception:
            # Probably we just don't have enough permission to read sysfs file
            pass
    return result


def scst_get_luns():
    result = {}
    targets = scst_get_iscsi_targets()
    for target in targets:
        lun0_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target,
                                 SYSFS_SCST_LUN0_DEV)
        lun0_device = str(Path(lun0_path).resolve())
        try:
            lun0_filename_file = open(os.path.join(lun0_device, "filename"))
            lun0_filename = lun0_filename_file.read().split("\n")[0]
            lun0_filename_file.close()
            rel_id_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target,
                                       "rel_tgt_id")
            rel_id_file = open(rel_id_path, 'r')
            rel_id_value = rel_id_file.read().split("\n")[0]
            rel_id_file.close()
            result[lun0_filename] = rel_id_value
        except FileNotFoundError:
            pass
    return result


def scst_get_luns2():
    luns = [device for device in os.listdir(SYSFS_SCST_LUNS)
            if device != 'mgmt']
    result = {}
    for lun in luns:
        device = os.path.join(SYSFS_SCST_LUNS, lun, "device/filename")
        device_file = open(device, 'r')
        device_name = device_file.read().split('\n')[0]
        result[device_name] = lun
    return result


def scst_get_lun_wwn(lun):
    targets = scst_get_iscsi_targets()
    wwns = {}
    for target in targets:
        rel_id_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target,
                                   "rel_tgt_id")
        rel_id_file = open(rel_id_path, 'r')
        rel_id_value = rel_id_file.read().split("\n")[0]
        rel_id_file.close()
        wwns[rel_id_value] = target
    try:
        return wwns[lun]
    except KeyError:
        return None


def scst_get_lun_wwn2(lun):
    exports_path = os.path.join(SYSFS_SCST_LUNS, lun, "device/exported")
    exports = os.listdir(exports_path)
    for export in exports:
        p = os.path.join(exports_path, export)
        export_path = str(Path(p).resolve())
        if "iscsi" in export_path:
            return get_iscsi_wwn(export_path)


def exec_shell_command(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    stdout, stderr = proc.communicate()
    return stdout.split('\n')


def debug_log(*messages):
    with open("/var/log/ctladm.log", "a") as log_file:
        message = map(lambda x: str(x), list(messages))
        log_file.write('\n'.join(list(message)))
        log_file.write('\n')
        log_file.close()


def get_devlist(xml_output=False):
    devlist = []
    luns = scst_get_luns()

    for dev in scst_get_devices():
        dev_params = scst_get_device_params(dev)
        if dev_params['filename']:
            if dev_params['filename'] in luns.keys():
                wwn = scst_get_lun_wwn(luns[dev_params['filename']])
                devlist.append(list(map(lambda x: str(x), [
                    luns[dev_params['filename']],
                    'block',
                    safe_cast(dev_params['size'], int, 0),
                    safe_cast(dev_params['blocksize'], int, 0),
                    dev_params['usn'],
                    dev,
                    dev_params['filename'],
                    wwn,
                    safe_cast(dev_params['threads_num'], int, 0)
                ])))

    debug_log("Command: devlist", "Args: noargs\n")
    if xml_output:
        xml_root = minidom.Document()

        # Used to strip declaration string later
        declaration = xml_root.toxml()

        xml = xml_root.createElement('ctllunlist')
        xml_root.appendChild(xml)
        for dev in devlist:
            lun = xml_root.createElement('lun')
            lun.setAttribute('id', dev[0])
            elem = xml_root.createElement('backend_type')
            text = xml_root.createTextNode(dev[1])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('lun_type')
            text = xml_root.createTextNode('0')
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('size')
            text = xml_root.createTextNode(dev[2])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('blocksize')
            text = xml_root.createTextNode(dev[3])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('serial_number')
            text = xml_root.createTextNode(dev[4])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('device_id')
            text = xml_root.createTextNode(dev[5])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('num_threads')
            text = xml_root.createTextNode(dev[8])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('file')
            text = xml_root.createTextNode(dev[6])
            elem.appendChild(text)
            lun.appendChild(elem)
            elem = xml_root.createElement('ctld_name')
            text = xml_root.createTextNode(','.join([dev[7], 'lun', '0']))
            elem.appendChild(text)
            lun.appendChild(elem)
            xml.appendChild(lun)
        xml_str = xml_root.toprettyxml(indent="\t")[(len(declaration)+1):]
        return xml_str
    else:
        return [dev[0:6] for dev in devlist]


def get_portlist(xml_output=False):
    portlist = []
    luns = scst_get_luns()
    for dev in scst_get_devices():
        dev_params = scst_get_device_params(dev)
        if dev_params['filename']:
            if dev_params['filename'] in luns.keys():
                wwn = scst_get_lun_wwn(luns[dev_params['filename']])
                portlist.append(list(map(lambda x: str(x), [
                    luns[dev_params['filename']],
                    "YES" if dev_params['active'] == '1' else "NO",
                    "iscsi",
                    "iscsi",
                    "{},t,0x0101".format(wwn),
                    wwn
                ])))
    debug_log("Command: portlist\n")
    if xml_output:
        xml_root = minidom.Document()
        # Used to strip declaration string later
        declaration = xml_root.toxml()

        xml = xml_root.createElement('ctlportlist')
        xml_root.appendChild(xml)
        for port in portlist:
            targ_port = xml_root.createElement('targ_port')
            targ_port.setAttribute('id', port[0])
            elem = xml_root.createElement('lun')
            elem.setAttribute('id', '0')
            text = xml_root.createTextNode(port[0])
            elem.appendChild(text)
            targ_port.appendChild(elem)
            elem = xml_root.createElement('target')
            text = xml_root.createTextNode(port[5])
            elem.appendChild(text)
            targ_port.appendChild(elem)
            elem = xml_root.createElement('initiator')
            initiator = ""
            sessions = scst_get_target_sessions(port[5])
            if sessions:
                initiator = sessions[0]
            text = xml_root.createTextNode(initiator)
            elem.appendChild(text)
            targ_port.appendChild(elem)
            xml.appendChild(targ_port)
        xml_str = xml_root.toprettyxml(indent="\t")[(len(declaration)+1):]
        return xml_str
    else:
        return [port[0:5] for port in portlist]


def get_portlist_qvp(port):
    portlist = {}
    luns = scst_get_luns()
    for k, v in luns.items():
        portlist[v] = {
            'Target': scst_get_lun_wwn(v),
            'LUN 0': v
        }
    '''
    for lun in rtsroot.luns:
        portlist[lun.storage_object.name] = {
            'Target': lun.parent_tpg.parent_target.wwn,
            'LUN 0': lun.storage_object.name
        }
    '''
    try:
        print('Target: {}'.format(portlist[str(port)]['Target']))
        print('LUN 0: {}'.format(portlist[str(port)]['LUN 0']))
    except KeyError:
        # no such port
        pass
    debug_log("portlist qvp")


def get_islist():
    islist = []
    targets = scst_get_iscsi_targets()
    for target in targets:
        sessions = scst_get_target_sessions(target)
        portal = scst_get_portal_addr(target)
        for session in sessions:
            islist.append(list(map(lambda x: str(x), [1, portal,
                          session,
                          target]))
                          )
    return islist


def create_lun(options, deviceid, lun):
    # opt_file = options[0].split('=')[1]
    opt_wwn = options[2].split('=')[1].split(',')[0]
    mgmt_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, opt_wwn,
                             SYSFS_SCST_LUNS_MGMT)
    command = "add {} 0".format(deviceid)

    mgmt_file = open(mgmt_path, "w")
    mgmt_file.write(command)
    mgmt_file.close()


def remove_lun(lun):
    target = scst_get_lun_wwn(lun)
    if target:
        mgmt_path = os.path.join(SYSFS_SCST_ISCSI_TGTS, target,
                                 SYSFS_SCST_LUNS_MGMT)
        command = "del 0"
        mgmt_file = open(mgmt_path, "w")
        mgmt_file.write(command)
        mgmt_file.close()
    debug_log("Command: remove lun LUN: {}".format(lun))


def print_result(result):
    if type(result) is str:
        print(result)
    else:
        for res in result:
            print('\t'.join(res))


def main(args):
    debug_log(args)
    if args.command == 'devlist':
        print_result(get_devlist(args.x))
    if args.command == 'islist':
        print_result(get_islist())
    if args.command == 'portlist' and args.qvp is None:
        print_result(get_portlist(args.x))
    if args.command == 'portlist' and args.qvp is not None:
        get_portlist_qvp(args.qvp)
    if args.command == 'create':
        create_lun(args.o, args.d, args.l)
    if args.command == 'remove':
        remove_lun(args.l)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Linux ctladm for PlayKey"
                                     "zfsapi (SCST)")
    parser.add_argument('command', type=str, action='store',
                        help='ctladm command')
    parser.add_argument('-q', action='store_true', help='Omit header')
    parser.add_argument('-qvp', type=int, action='store', required=False,
                        help='Omit header, verbose, specify port number')
    parser.add_argument('-b', type=str, action='store', help='Device type')
    parser.add_argument('-o', type=str, action='append', help='Create options')
    parser.add_argument('-d', type=str, action='store', help='Device ID')
    parser.add_argument('-l', type=str, action='store', help='LUN')
    parser.add_argument('-x', action='store_true', help='XML Output')

    args = parser.parse_args()
    main(args)
