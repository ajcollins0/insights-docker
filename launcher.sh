#!/bin/bash

export PS1="(chroot)$ "
export PYTHONPATH="/mnt/opt/python/site-packages"
cd /mnt/redhat_access_insights
python __init__.py --display-name="DOCKER-`cat /etc/redhat-access-insights/display-name`" 