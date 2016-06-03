#!/bin/bash
set -u -e -E

. ./yumtests.settings

rm -rf $REPO && mkdir -p $REPO
rm -rf $EMPTY_DIR && mkdir -p $EMPTY_DIR

cat > $TMP/yumtop.conf << TOPCONF
[toprepo]
name=toprepo
baseurl=file://$REPO
gpgcheck=0
enabled=1
TOPCONF

cat > $TMP/yum1.conf << 1CONF
[repo1]
name=repo1
baseurl=file://$REPO/repo1
gpgcheck=0
enabled=1
1CONF

mkdir -p $REPO $REPO/repo1

yumtop repolist all || :

createrepo_c $REPO
createrepo_c $REPO/repo1

yumtop repolist all

create_rpm foo 1.0 repo1

yumtop search foo | grep "No matches found"

createrepo_c $REPO

yumtop search foo | grep -C 100 --color=always "foo.x86"

yumtop list foo | grep "1.0-1"

create_rpm foo 1.1 repo1

yumtop list foo | grep "1.0-1" | grep toprepo

createrepo_c $REPO/repo1

yumtop list foo | grep "1.0-1" | grep toprepo
yum1 list foo | grep "1.1-1" | grep repo1

create_rpm foo 1.2

createrepo_c $REPO

yumtop list foo | grep "1.2-1" | grep toprepo
yum1 list foo | grep "1.1-1" | grep repo1
exit


echo "---------------------"

mkdir -p $REPO/repo2
create_rpm foo 2.0 repo2
createrepo_c $REPO/repo2

yum list foo | grep "1.2-1" | grep toprepo

ln -sf $REPO/repo2/*.rpm* $REPO/repo1
createrepo_c $REPO/repo1

yum list foo
yum list foo | grep "2.0-1" | grep repo1
