#!/usr/bin/env bash
# Install PrusaSlicer from Flathub for headless CI slicing (issue #100).
#
# PrusaSlicer 2.9.x ships no AppImage, so the previous AppImage URL in
# Dockerfile.live-test / live-test.yml was dead. Flathub is the supported Linux
# distribution channel.
#
# Pin a build by exporting PRUSASLICER_FLATPAK_COMMIT before calling this script.
# Find the current commit with:
#   flatpak remote-info --system flathub com.prusa3d.PrusaSlicer
set -euo pipefail

APP_ID="com.prusa3d.PrusaSlicer"
PIN="${PRUSASLICER_FLATPAK_COMMIT:-}"

if ! command -v flatpak >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends flatpak xvfb
fi

sudo flatpak remote-add --if-not-exists flathub \
  https://dl.flathub.org/repo/flathub.flatpakrepo

echo "==> Installing ${APP_ID} from Flathub"
sudo flatpak install -y --noninteractive flathub "${APP_ID}"

if [ -n "${PIN}" ]; then
  echo "==> Pinning ${APP_ID} to commit ${PIN}"
  sudo flatpak update -y --noninteractive --commit="${PIN}" "${APP_ID}"
fi

# Record the resolved build so the pin can be captured for issue #99.
echo "==> Installed build:"
flatpak info "${APP_ID}" | sed -n 's/^ *\(Version\|Commit\|Date\):/\1:/p'

# `flatpak run` is sandboxed; --filesystem=host is required so the slicer can
# read the model/config out of the workspace and write the G-code back.
sudo tee /usr/local/bin/prusa-slicer >/dev/null <<'SHIM'
#!/usr/bin/env bash
exec flatpak run --filesystem=host \
  --env=QT_QPA_PLATFORM=offscreen \
  com.prusa3d.PrusaSlicer "$@"
SHIM
sudo chmod +x /usr/local/bin/prusa-slicer

echo "==> prusa-slicer shim installed"
prusa-slicer --help >/dev/null 2>&1 || {
  echo "FAIL: prusa-slicer shim is not runnable" >&2
  exit 1
}