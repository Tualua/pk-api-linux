#### Enter root shell

    sudo su

##### visudo

    Uncomment line near the end of the file `%wheel  ALL=(ALL)       NOPASSWD: ALL`

#### Install git

    dnf -y install git

#### Clone this repo
    cd ~
    git clone https://github.com/Tualua/pk-api-linux.git

#### Oracle Linux 8
##### Install OpenZFS 2.1.0

    dnf -y install oracle-epel-release-el8 -y
    dnf -y install gcc make autoconf automake libtool rpm-build dkms libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-uek-devel-$(uname -r) python3 python3-devel python3-setuptools python3-cffi libffi-devel
    exit
    cd ~
    wget https://github.com/openzfs/zfs/releases/download/zfs-2.1.0/zfs-2.1.0.tar.gz
    tar xf zfs-2.0.4.tar.gz
    cd zfs-2.0.4
    ./configure
    make -j1 rpm-utils rpm-dkms
    sudo yum localinstall *.$(uname -p).rpm *.noarch.rpm    
    sudo su
    modprobe zfs
    zpool import data

#### NGINX

    dnf -y module disable nginx:1.14
    dnf -y module enable nginx:1.18
    dnf -y install nginx
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    cp ~/pk-api-linux/ol8/nginx/nginx.conf /etc/nginx/
    cp ~/pk-api-linux/ol8/nginx/api.conf /etc/nginx/conf.d/
    mkdir -p /var/cache/httpd/default
    mkdir -p /var/cache/httpd/mobile
    mkdir -p /var/cache/httpd/temp
    mkdir -p /var/www/api
    semodule -i ~/pk-api-linux/ol8/selinux/nginx_custom.pp

###### Check nginx config syntax

    nginx -t

###### Enable and start nginx

    systemctl enable nginx --now

##### Create user to run API

    useradd zfsreplica
    usermod zfsreplica -aG nginx
    usermod zfsreplica -aG wheel

##### Create log directory

    mkdir -p /var/log/zfsreplica
    chown zfsreplica:nginx /var/log/zfsreplica

##### Create spool directory

    mkdir -p /var/spool/zfsapi
    chown zfsreplica:nginx /var/spool/zfsapi

##### FreeBSD sudo and perl is in /usr/local/bin and we need to make a link

    ln -s /usr/bin/sudo /usr/local/bin/sudo
    ln -s /usr/bin/perl /usr/local/bin/perl

##### Copy API to /var/www/api

#### uWSGI

    dnf -y install expat-devel
    cd ~
    wget https://projects.unbit.it/downloads/uwsgi-2.0.19.1.tar.gz
    tar xf uwsgi-2.0.19.1.tar.gz
    cd uwsgi-2.0.19.1/
    CFLAGS="-fno-PIE -fPIC -no-pie --static" LDFLAGS="-fno-PIE -fPIC -no-pie" python3 uwsgiconfig.py --build psgi
    cp uwsgi /usr/bin/
    cpan install Data::UUID
    cpan install Devel::StackTrace
    cpan install XML::Parser
    mkdir /usr/local/etc/uwsgi
    cp ~/pk-api-linux/ol8/uwsgi/*.ini /usr/local/etc/uwsgi/
    cp ~/pk-api-linux/ol8/uwsgi/uwsgi-app\@.service /etc/systemd/system/
    systemctl enable uwsgi-app@uwsgi_replicate.service --now
    systemctl enable uwsgi-app@uwsgi_api.service --now

###### Check uWSGI logs

    # tail -n50 /var/log/uwsgi/uwsgi_api.log

    initialized Perl 5.26.3 main interpreter at 0x562882521e60
    your server socket listen backlog is limited to 32 connections
    your mercy for graceful operations on workers is 60 seconds
    mapped 291680 bytes (284 KB) for 3 cores
    *** Operational MODE: preforking ***
    Plack::Util is not installed, using "do" instead of "load_psgi"
    PSGI app 0 (/var/www/api/api.psgi) loaded in 0 seconds at 0x5628827c0a50 (interpreter 0x562882521e60)
    *** uWSGI is running in multiple interpreter mode ***
    spawned uWSGI master process (pid: 277660)
    spawned uWSGI worker 1 (pid: 277662, cores: 1)
    spawned uWSGI worker 2 (pid: 277663, cores: 1)
    spawned uWSGI worker 3 (pid: 277664, cores: 1)
    *** Stats server enabled on 127.0.0.1:1717 fd: 16 ***

#### mbuffer for replication

    dnf -y install mbuffer
    ln -s /bin/mbuffer /usr/local/bin/mbuffer

##### iSCSI

    wget https://sourceforge.net/code-snapshots/svn/s/sc/scst/svn/scst-svn-r9506-branches-3.5.x.zip
    unzip scst-svn-r9506-branches-3.5.x.zip
    cd scst-svn-r9506-branches-3.5.x/
    make 2release
    make scst-dkms-rpm
    make rpm
    cd /usr/src/packages/RPMS/x86_64/
    yum -y localinstall scst-dkms-3.5.0-1.el8.x86_64.rpm scst-dkms-userspace-3.5.0-1.el8.x86_64.rpm
    rpm -ivh scstadmin-1.0.0-1.x86_64.rpm
    cp ~/pk-api-linux/etc/scst.conf /etc/scst.conf

##### ctladm

<<<<<<< HEAD:INSTALL-OL8.md
    cp ~/pk-api-linux/ctladm /usr/bin/ctladm
=======
    cp ~/pk-api-linux/ctladm-scst /usr/bin/
>>>>>>> ab331337c4bcec4c006d1c744c2bc1bf4a8aafea:INSTALL-OL8.3.md
    chmod +x /usr/bin/ctladm
    mkdir /etc/ctladm
        
##### Check API

    curl -sS "http://localhost/api/?action=status"

#### Create LUNs and initiators

