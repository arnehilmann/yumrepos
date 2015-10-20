#!/bin/bash
set -e -E -u -o pipefail -C

TESTREPO1=repos/repo1
TESTREPO2=repos/repo2
HOST=http://localhost:8080
TESTRPM=foo-1.0-1.x86_64.rpm

TEST_YUM=false
if yum --version &> /dev/null; then
    TEST_YUM=true
    YUM="yum -c res/yum.conf"
    echo "'yum' command found, testing testrepo now"
fi

rm -rf $TESTREPO1 $TESTREPO2

# set -x

curl $HOST/repos           -i -s | grep "200 OK"

curl -F rpm=@res/$TESTRPM \
    $HOST/admin/$TESTREPO1  -i -s | grep "404 NOT FOUND"

curl -X PUT \
    $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

curl -X PUT \
    $HOST/admin/$TESTREPO2 -i -s | grep "201 CREATED"

curl $HOST/$TESTREPO1       -i -s | grep "200 OK"

curl -F rpm=@res/$TESTRPM \
    $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

curl $HOST/$TESTREPO1       -i -s | grep "200 OK"

[[ -e $TESTREPO1/$TESTRPM ]]
[[ -d $TESTREPO1/repodata ]]

if $TEST_YUM; then
    $YUM clean all
    $YUM repolist
    $YUM search foo | grep "foo.x86_64"
    $YUM info foo | grep "Repo"
fi

curl -X STAGE -d target-repo=repo2 $HOST/admin/$TESTREPO1/$TESTRPM

if $TEST_YUM; then
    $YUM clean all
    $YUM repolist
    $YUM search foo | grep "foo.x86_64"
    $YUM info foo | grep "Repo"
fi

curl -X DELETE \
    $HOST/admin/$TESTREPO2  -i -s | grep "409 CONFLICT"

curl -X DELETE \
    $HOST/admin/$TESTREPO2/$TESTRPM -i -s | grep "204 NO CONTENT"

curl -X DELETE \
    $HOST/admin/$TESTREPO2/$TESTRPM  -i -s | grep "404 NOT FOUND"

curl -X DELETE \
    $HOST/admin/$TESTREPO2  -i -s | grep "204 NO CONTENT"

[[ ! -d $TESTREPO2 ]]

echo "SUCCESS"
