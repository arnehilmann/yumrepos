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

echo "preparing test repos $TESTREPO1 and $TESTREPO2"
rm -rf $TESTREPO1 $TESTREPO2

# set -x

echo "check repos overview"
curl $HOST/repos           -i -s | grep "200 OK"

echo "try to upload rpm to non-existant repo"
curl -F rpm=@res/$TESTRPM \
    $HOST/admin/$TESTREPO1  -i -s | grep "404 NOT FOUND"

echo "create $TESTREPO1"
curl -X PUT \
    $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

echo "check created repo"
curl $HOST/$TESTREPO1       -i -s | grep "200 OK"

echo "upload rpm to $TESTREPO1"
curl -F rpm=@res/$TESTRPM \
    $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

echo "check rpm and metadata"
[[ -e $TESTREPO1/$TESTRPM ]]
[[ -d $TESTREPO1/repodata ]]

echo "create $TESTREPO2"
curl -X PUT \
    $HOST/admin/$TESTREPO2 -i -s | grep "201 CREATED"

echo "check metadata"
[[ -d $TESTREPO2/repodata ]]

if $TEST_YUM; then
    echo "search for rpm via yum"
    $YUM clean all
    $YUM repolist
    $YUM search foo | grep "foo.x86_64"
    echo "rpm found in repo: " $($YUM info foo | grep "Repo")
fi

curl -X STAGE -d target-repo=repo2 $HOST/admin/$TESTREPO1/$TESTRPM

if $TEST_YUM; then
    echo "search for rpm via yum"
    $YUM clean all
    $YUM repolist
    $YUM search foo | grep "foo.x86_64"
    echo "rpm found in repo: " $($YUM info foo | grep "Repo")
fi

echo "try to remove non-empty $TESTREPO2"
curl -X DELETE \
    $HOST/admin/$TESTREPO2  -i -s | grep "409 CONFLICT"

echo "remove rpm"
curl -X DELETE \
    $HOST/admin/$TESTREPO2/$TESTRPM -i -s | grep "204 NO CONTENT"

echo "try to remove rpm that was removed already"
curl -X DELETE \
    $HOST/admin/$TESTREPO2/$TESTRPM  -i -s | grep "404 NOT FOUND"

echo "remove empty repo $TESTREPO1"
curl -X DELETE \
    $HOST/admin/$TESTREPO1  -i -s | grep "204 NO CONTENT"

echo "remove empty repo $TESTREPO2"
curl -X DELETE \
    $HOST/admin/$TESTREPO2  -i -s | grep "204 NO CONTENT"

echo "check if repos are removed"
[[ ! -d $TESTREPO2 ]]

echo "SUCCESS"
