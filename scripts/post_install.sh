#!/bin/bash
# Update desktop database and icon cache
update-desktop-database -q
gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor