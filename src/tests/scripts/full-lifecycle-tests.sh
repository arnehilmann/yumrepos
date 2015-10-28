#!/bin/bash
set -e -E -u -o pipefail -C

TESTREPO1=repos/testrepo1
TESTREPO2=repos/testrepo2
TESTREPO3=repos/testrepo3
HOST=http://localhost:8080
TESTRPM=foo-1.0-1.x86_64.rpm

TEST_YUM=false
if yum --version &> /dev/null; then
    TEST_YUM=true
    YUM="yum -c res/yum.conf"
    echo "'yum' command found"
fi

echo "preparing test repos"
rm -rf $TESTREPO1 $TESTREPO2 $TESTREPO3


# set -x

echo "check if yum-repo service is up"
curl $HOST/repos           -i -s | grep "200 OK"

echo "try to upload rpm to non-existant repo"
curl -F rpm=@res/$TESTRPM $HOST/admin/$TESTREPO1  -i -s | grep "404 NOT FOUND"

echo "create $TESTREPO1"
curl -X PUT $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

echo "check created repo"
curl $HOST/$TESTREPO1       -i -s | grep "200 OK"

echo "upload rpm to $TESTREPO1"
curl -F rpm=@res/$TESTRPM $HOST/admin/$TESTREPO1  -i -s | grep "201 CREATED"

echo "check rpm and metadata"
[[ -e $TESTREPO1/$TESTRPM ]]
[[ -d $TESTREPO1/repodata ]]

echo "create $TESTREPO2"
curl -X PUT $HOST/admin/$TESTREPO2 -i -s | grep "201 CREATED"

echo "check metadata"
[[ -d $TESTREPO2/repodata ]]

echo "create empty repo3"
curl -X PUT $HOST/admin/$TESTREPO3 -i -s | grep "201 CREATED"

if $TEST_YUM; then
    echo "search for rpm via yum"
    $YUM clean all
    $YUM repolist
    $YUM search foo 2> /dev/null | grep "foo.x86_64"
    echo "rpm found in repo: " $($YUM info foo | grep "testrepo1")
fi

curl -X STAGE $HOST/admin/$TESTREPO1/$TESTRPM/stageto/testrepo2

if $TEST_YUM; then
    echo "search for rpm via yum"
    $YUM clean all
    $YUM repolist
    $YUM search foo 2> /dev/null | grep "foo.x86_64"
    echo "rpm found in repo: " $($YUM info foo | grep "testrepo2")
fi

echo "replace repo3 with a link to repo2"
curl -X DELETE $HOST/admin/$TESTREPO3 -i -s | grep "204 NO CONTENT"
curl -X PUT $HOST/admin/$TESTREPO3?link_to=testrepo2 -i -s | grep "201 CREATED"

echo "check for repo links"
curl $HOST/admin/$TESTREPO1/is_link -i -s | grep "false"
curl $HOST/admin/$TESTREPO3/is_link -i -s | grep "true"

if $TEST_YUM; then
    echo "search for rpm via yum"
    $YUM clean all
    $YUM repolist
    $YUM search foo | grep "foo.x86_64"
    echo "rpm found in repo: " $($YUM info foo --showduplicates | grep "repo3")
fi

echo "tear down test repos"

echo "try to remove non-empty $TESTREPO2"
curl -X DELETE $HOST/admin/$TESTREPO2  -i -s | grep "409 CONFLICT"

echo "remove rpm"
curl -X DELETE $HOST/admin/$TESTREPO2/$TESTRPM -i -s | grep "204 NO CONTENT"

echo "try to remove rpm that was removed already"
curl -X DELETE $HOST/admin/$TESTREPO2/$TESTRPM  -i -s | grep "404 NOT FOUND"

echo "remove empty repo $TESTREPO1"
curl -X DELETE $HOST/admin/$TESTREPO1  -i -s | grep "204 NO CONTENT"

echo "remove empty repo $TESTREPO2"
curl -X DELETE $HOST/admin/$TESTREPO2  -i -s | grep "204 NO CONTENT"

echo "check if repos are removed"
[[ ! -d $TESTREPO1 ]]
[[ ! -d $TESTREPO2 ]]
[[ ! -d $TESTREPO3 ]]

echo "SUCCESS"
