#!/bin/bash

TMP=$PWD/tmp
REPO=$TMP/repo

EMPTY_DIR=$TMP/empty

create_rpm() {
    NAME=$1
    VERSION=$2
    TARGET_DIR=$REPO/${3:-}
    mkdir -p $TARGET_DIR
    (
        cd $TARGET_DIR
        fpm -s dir -t rpm -v $VERSION -n $NAME --force $EMPTY_DIR
    )
}

yum() {
    echo
    echo "yum $*"
    /usr/bin/yum -c $TMP/yum.conf clean all
    /usr/bin/yum -c $TMP/yum.conf $*
}
