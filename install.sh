# Ubuntu 
# Install OpenZFS 2.0.1
sudo su
apt -y install build-essential autoconf automake libtool gawk alien fakeroot dkms libblkid-dev uuid-dev libudev-dev libssl-dev zlib1g-dev libaio-dev libattr1-dev libelf-dev linux-headers-$(uname -r) python3 python3-dev python3-setuptools python3-cffi libffi-dev
cd ~
wget https://github.com/openzfs/zfs/releases/download/zfs-2.0.1/zfs-2.0.1.tar.gz
tar xf zfs-2.0.1.tar.gz
cd zfs-2.0.1
sh autogen.sh
./configure
make -s -j$(nproc) deb-dkms deb
dpkg -i zfs-dkms_2.0.1-1_amd64.deb zfs_2.0.1-1_amd64.deb libzfs4_2.0.1-1_amd64.deb libnvpair3_2.0.1-1_amd64.deb libuutil3_2.0.1-1_amd64.deb

apt -y install expat
apt -y install libxml-parser-perl libdevel-stacktrace-perl
apt -y install nginx
apt -y install uwsgi uwsgi-plugin-psgi
apt -y install targetcli-fb

useradd zfsreplica
usermod zfsreplica -aG www-data 
usermod zfsreplica -aG sudo

# Create log directory
mkdir -p /var/log/zfsreplica
chown zfsreplica:www-data /var/log/zfsreplica

# Create spool directory
mkdir -p /var/spool/zfsapi
chown zfsreplica:www-data /var/spool/zfsapi

# FreeBSD sudo is in /usr/local/bin and we need to make a link
ln -s /usr/bin/sudo /usr/local/bin/sudo
