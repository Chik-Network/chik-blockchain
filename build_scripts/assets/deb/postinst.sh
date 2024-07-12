#!/usr/bin/env bash
# Post install script for the UI .deb to place symlinks in places to allow the CLI to work similarly in both versions

set -e

chown -f root:root /opt/chik/chrome-sandbox || true
chmod -f 4755 /opt/chik/chrome-sandbox || true
ln -s /opt/chik/resources/app.asar.unpacked/daemon/chik /usr/bin/chik || true
ln -s /opt/chik/chik-blockchain /usr/bin/chik-blockchain || true
