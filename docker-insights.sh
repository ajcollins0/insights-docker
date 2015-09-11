#!/bash/bin

IMAGE="./image"

function cleanup () {
    # try clean up
    for var in sys proc dev tmp var/tmp var/log mnt/opt/python mnt etc/pki/consumer etc root
    do
        umount ${IMAGE}/${var}
    done

    # wipe out old stuff
    rm -rf etc 

    atomic unmount $IMAGE
}

# wipe out old data
# rm -rf log vartmp 

mkdir $IMAGE log vartmp
mkdir insights-client/opt
mkdir insights-client/opt/python

cleanup

# mount the image
atomic mount rhel $IMAGE

# copy the images etc shit
rsync -aqPS ${IMAGE}/etc .

# bind mount all the stuff needed to run
for var in /sys /proc /dev /tmp  etc
do
    mount -o bind ${var} ${IMAGE}/${var}
done
mount -o bind vartmp ${IMAGE}/var/tmp
mount -o bind log ${IMAGE}/var/log
mount -o bind insights-client ${IMAGE}/mnt
mount -o bind /usr/lib/python2.7 ${IMAGE}/mnt/opt/python
mount -o bind /etc/pki/consumer ${IMAGE}/etc/pki/consumer
mount -o bind /root/ ${IMAGE}/root/

# copy over the resolve.conf so we can resolve shit... duh
cp /etc/resolv.conf ${IMAGE}/etc/

# setup /etc/redhat-access-insights
rm -rf ${IMAGE}/etc/redhat-access-insights
cp -r insights-client/etc ${IMAGE}/etc/redhat-access-insights

# setup machine-id FIXME these need to be dynamically gathered
echo 275be1d3d070 > ${IMAGE}/etc/redhat-access-insights/machine-id
echo "rhel"       > ${IMAGE}/etc/redhat-access-insights/display-name

chroot $IMAGE /mnt/launcher.sh
cleanup