#!/bin/bash

# Set color ENV vars
RED='\033[0;31m'
GREEN='\033[0;32m'
LIGHT_BLUE='\033[1;34m'
NC='\033[0m' # No Color

# Wipe any existing partitions
# Create a new gpt
# Create a new partition
# Format partition to exFat labeled PLOTS so it can be found by fstab
# Mount
# Return Exit Code
echo -e "${LIGHT_BLUE}|Preparing Disk|${NC}"
umount /chia/dst || /bin/true && \
    sudo mdadm --stop --scan && \
    wipefs -a /dev/chiadst && \
    parted -s /dev/chiadst mklabel gpt && \
    parted -s /dev/chiadst mkpart CHIA 0% 100% && \
    sleep 1 && \
    mkfs.exfat -n "PLOTS" /dev/chiadst1 && \
    mount /chia/dst && \
    (echo -e "${GREEN}|Disk Preparred|${NC}"; exit 0) \
    || (c=$?; echo -e "${RED}|Failed Preparing Disk|${NC}"; (exit $c))