
#### Enter root shell

    sudo su

#### Clone this repo
    cd ~
    git clone https://github.com/Tualua/pk-api-linux.git

#### Ubuntu 
##### Install OpenZFS 2.0.1

    apt -y  install build-essential autoconf automake libtool gawk alien fakeroot dkms libblkid-dev uuid-dev libudev-dev libssl-dev zlib1g-dev libaio-dev libattr1-dev libelf-dev linux-headers-$(uname -r) python3 python3-dev python3-setuptools python3-cffi libffi-dev
    cd ~
    wget https://github.com/openzfs/zfs/releases/download/zfs-2.0.1/zfs-2.0.1.tar.gz
    tar xf zfs-2.0.1.tar.gz
    cd zfs-2.0.1
    sh autogen.sh
    ./configure
    make -s -j$(nproc) deb-dkms deb
    dpkg -i zfs-dkms_2.0.1-1_amd64.deb zfs_2.0.1-1_amd64.deb libzfs4_2.0.1-1_amd64.deb libnvpair3_2.0.1-1_amd64.deb libuutil3_2.0.1-1_amd64.deb
    systemctl enable zfs-import-cache
    systemctl enable zfs-import.target
    modprobe zfs
    zpool import data
    zpool set cachefile=/etc/zfs/zpool.cache data

##### Install additional software

    apt -y install expat
    apt -y install libxml-parser-perl libdevel-stacktrace-perl libdata-uuid-perl
    apt -y install nginx
    apt -y install uwsgi uwsgi-plugin-psgi
    apt -y install targetcli-fb
    apt -y install mbuffer

##### Create user to run API

    useradd zfsreplica
    usermod zfsreplica -aG www-data 
    usermod zfsreplica -aG sudo

##### Create log directory

    mkdir -p /var/log/zfsreplica
    chown zfsreplica:www-data /var/log/zfsreplica

##### Create spool directory

    mkdir -p /var/spool/zfsapi
    chown zfsreplica:www-data /var/spool/zfsapi

##### FreeBSD sudo and perl is in /usr/local/bin and we need to make a link

    ln -s /usr/bin/sudo /usr/local/bin/sudo
    ln -s /usr/bin/perl /usr/local/bin/perl
    
##### visudo

Change `%sudo   ALL=(ALL:ALL) ALL` to `%sudo   ALL=(ALL:ALL) NOPASSWD:ALL`

##### ctladm

    cp ~/pk-api-linux/ctladm /usr/bin/
    chmod +x /usr/bin/ctladm
    mkdir /etc/ctladm
    cp ~/pk-api-linux/ctladm.ini /etc/ctladm
    
##### NGINX

    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    cp ~/pk-api-linux/nginx/nginx.conf /etc/nginx/
    cp ~/pk-api-linux/nginx/api.conf /etc/nginx/conf.d/
    mkdir -p /var/tmp/nginx/cache/default
    mkdir /var/www/api
    rm /etc/nginx/sites-enabled/default

##### Copy API to /var/www/api
    
###### Check nginx config syntax    
    
    nginx -t
    systemctl reload nginx
        
##### uWSGI
    mkdir /usr/local/etc/uwsgi
    cp ~/pk-api-linux/uwsgi/*.ini /usr/local/etc/uwsgi/
    cp ~/pk-api-linux/uwsgi/uwsgi-app\@.service /etc/systemd/system/
    systemctl enable uwsgi-app@uwsgi_replicate.service --now
    systemctl enable uwsgi-app@uwsgi_api.service --now

###### Check uWSGI logs

    # tail -n50 /var/log/uwsgi/uwsgi_api.log

    initialized Perl 5.30.0 main interpreter at 0x55f1262f9820
    your server socket listen backlog is limited to 32 connections
    your mercy for graceful operations on workers is 60 seconds
    mapped 291680 bytes (284 KB) for 3 cores
    *** Operational MODE: preforking ***
    Plack::Util is not installed, using "do" instead of "load_psgi"
    PSGI app 0 (/var/www/api/api.psgi) loaded in 0 seconds at 0x55f12653f978 (interpreter 0x55f1262f9820)
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI master process (pid: 5999)
    spawned uWSGI worker 1 (pid: 6016, cores: 1)
    spawned uWSGI worker 2 (pid: 6017, cores: 1)
    spawned uWSGI worker 3 (pid: 6018, cores: 1)
    *** Stats server enabled on 127.0.0.1:1717 fd: 14 ***

##### Check API

    curl -sS "http://localhost/api/?action=status"

#### Create LUNs and initiators

You should limit LUNs visibility to hosts by using initiator names in acl. Also do not forget to edit `/etc/ctladm.ini` and add vm and initiator names

Create backstore for system disk

    targetcli backstores/block create name=1001 dev=/dev/zvol/data/kvm/desktop/desktop-vm1
    
Create initiator

    targetcli iscsi/ create wwn=iqn.2016-04.net.playkey.iscsi:desktop-vm1
    
Delete default portal

    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:desktop-vm1/tpg1/portals/ delete ip_address=0.0.0.0 ip_port=3260
    
Add portal

    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:desktop-vm1/tpg1/portals/ create ip_address=192.168.255.1
    
Disable authentication

    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:desktop-vm1/tpg1/ set attribute authentication=0
    
Limit LUN access only to initiator with WWN iqn.2020-09.net.playkey.iscsi:hv:pk-host1 (for example)

    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:desktop-vm1/tpg1/acls create wwn=iqn.2020-09.net.playkey.iscsi:hv:pk-host1

Add LUN to initiator

    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:desktop-vm1/tpg1/luns create lun=0 storage_object=/backstores/block/1001

All the same for games disk

    targetcli backstores/block create name=2001 dev=/dev/zvol/data/kvm/desktop/games-vm1
    targetcli iscsi/ create wwn=iqn.2016-04.net.playkey.iscsi:games-vm1
    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:games-vm1/tpg1/portals/ delete ip_address=0.0.0.0 ip_port=3260
    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:games-vm1/tpg1/portals/ create ip_address=192.168.255.1
    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:games-vm1/tpg1/ set attribute authentication=0
    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:games-vm1/tpg1/acls create wwn=iqn.2020-09.net.playkey.iscsi:hv:pk-host1
    targetcli /iscsi/iqn.2016-04.net.playkey.iscsi:games-vm1/tpg1/luns create lun=0 storage_object=/backstores/block/2001
    
Save targetcli config

    targetcli saveconfig
