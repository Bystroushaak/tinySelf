#!/bin/bash
# Inspired by the https://xan-manning.co.uk/making-deb-packages-using-docker/

# Clear out the /build and /release directory
rm -rf /build/*
rm -rf /release/*

cd /pypy
hg update 97567

cd /src
# Re-pull the repository
git fetch
git pull

# BUILD_VERSION=$(git describe --tags $(git rev-list --tags --max-count=1)) && \
# git checkout ${BUILD_VERSION}
BUILD_VERSION=`date "+%Y%m%d%H%M"`

# Compile tinySelf
export RPYTHON_PATH="/pypy/rpython/bin"
export PYTHON_PATH="src/:/pypy:$PYTHONPATH"

./compile.py -q $EXTRA_ARGS

# copy output binary file
mkdir -p /build/usr/bin
cp tSelf /build/usr/bin
cp tSelf /release

# copy stdlib
mkdir -p /build/var/lib/tinySelf/
cp objects/stdlib.tself /build/var/lib/tinySelf/stdlib.tself

# Get the Install Size
INSTALL_SIZE=$(du -s /build | awk '{ print $1 }')

# Make DEBIAN directory in /build
mkdir -p /build/DEBIAN

# Copy the control file from resources
cat > /build/DEBIAN/control <<EOF
Package: tinySelf
Version: __VERSION__
Architecture: amd64
Installed-Size: __FILESIZE__
Priority: extra
Homepage: https://github.com/Bystroushaak/tinySelf
Maintainer: Bystroushaak <bystrousak@kitakitsune.org>
Description: Programming language inspired by Self.
 Self-like language implemented in the RPython language toolkit.
 .

EOF

# Fill in the information in the control file
sed -i "s/__VERSION__/${BUILD_VERSION}/g" /build/DEBIAN/control
sed -i "s/__FILESIZE__/${INSTALL_SIZE}/g" /build/DEBIAN/control

# Build our Debian package
fakeroot dpkg-deb -b "/build"

# Move it to release
mv /build.deb /release/tSelf-${BUILD_VERSION}-amd64.deb
