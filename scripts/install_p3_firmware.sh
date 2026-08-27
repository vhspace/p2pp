#!/bin/bash
set -euo pipefail

# Download and load the Palette 3 firmware Docker stack.
# The firmware is publicly available from Mosaic's S3 bucket.
# Since the P3 runs on ARM, Docker images need QEMU binfmt emulation on x86.
#
# Usage: bash scripts/install_p3_firmware.sh
# Env:   P3_FIRMWARE_URL (from .slicer-versions.env)

FIRMWARE_URL="${P3_FIRMWARE_URL:-https://p3-stable.s3.amazonaws.com/versions/p3_22.08.11.0.zip}"
FIRMWARE_DIR="${P3_FIRMWARE_DIR:-/tmp/p3-firmware}"

echo "=== Enabling QEMU binfmt for ARM emulation ==="
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

echo "=== Downloading P3 firmware from ${FIRMWARE_URL} ==="
if [ -d "${FIRMWARE_DIR}" ] && [ -f "${FIRMWARE_DIR}/.loaded" ]; then
    echo "Firmware already downloaded and loaded — skipping"
    exit 0
fi

wget -q "${FIRMWARE_URL}" -O /tmp/p3_firmware.zip
mkdir -p "${FIRMWARE_DIR}"

echo "=== Extracting firmware ==="
# 7z handles the large zip better than unzip
7z x -o"${FIRMWARE_DIR}" /tmp/p3_firmware.zip -y
rm -f /tmp/p3_firmware.zip

echo "=== Loading Docker images ==="
for img in "${FIRMWARE_DIR}"/images/*.tar.gz; do
    echo "Loading $(basename "$img")..."
    docker load -i "$img"
done

echo "=== P3 firmware loaded ==="
touch "${FIRMWARE_DIR}/.loaded"
echo "Firmware extracted to ${FIRMWARE_DIR}"
echo "Start the stack with: cd ${FIRMWARE_DIR} && docker compose up -d"