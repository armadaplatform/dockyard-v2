#!/usr/bin/env bash

export GOPATH=/go
export PATH=$GOPATH/bin:/usr/local/go/bin:$PATH

mkdir -p "$GOPATH/src" "$GOPATH/bin"
chmod -R 777 "$GOPATH"

apt-get update
apt-get install -y librados-dev apache2-utils git

export CHECKOUT_DIR=/go/src/github.com/docker
export DISTRIBUTION_DIR=$CHECKOUT_DIR/distribution
export GOPATH=$DISTRIBUTION_DIR/Godeps/_workspace:$GOPATH
export DOCKER_BUILDTAGS="include_rados include_oss include_gcs"

mkdir -p $CHECKOUT_DIR
cd $CHECKOUT_DIR
git clone -b v2.2.1 --single-branch --depth 1 https://github.com/docker/distribution.git

cd $DISTRIBUTION_DIR

make PREFIX=/go clean binaries

mkdir -p /etc/docker/registry/
cp cmd/registry/config-dev.yml /etc/docker/registry/config.yml

mkdir -p /var/lib/registry
chmod 777 /var/lib/registry
