# Create spool directory
mkdir -p /var/spool/zfsapi
chown zfsreplica:www-data /var/spool/zfsapi

# FreeBSD sudo is in /usr/local/bin and we need to make a link
ln -s /usr/bin/sudo /usr/local/bin/sudo
