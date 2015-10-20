#!/bin/bash
set -e -E -u

TESTREPO=repos/testrepo

rm -rf $TESTREPO

set -x

curl http://localhost:8080/repos           -i -s | grep "200 OK"

curl -F rpm=@res/foo-1.0-1.x86_64.rpm \
    http://localhost:8080/admin/$TESTREPO  -i -s | grep "404 NOT FOUND"

curl -X PUT \
    http://localhost:8080/admin/$TESTREPO  -i -s | grep "201 CREATED"

curl http://localhost:8080/$TESTREPO       -i -s | grep "200 OK"

curl -F rpm=@res/foo-1.0-1.x86_64.rpm \
    http://localhost:8080/admin/$TESTREPO  -i -s | grep "201 CREATED"

curl http://localhost:8080/$TESTREPO       -i -s | grep "200 OK"

[[ -e $TESTREPO/foo-1.0-1.x86_64.rpm ]]
[[ -d $TESTREPO/repodata ]]

curl -X DELETE \
    http://localhost:8080/admin/$TESTREPO  -i -s | grep "409 CONFLICT"

curl -X DELETE \
    http://localhost:8080/admin/$TESTREPO/foo-1.0-1.x86_64.rpm -i -s | grep "204 NO CONTENT"

curl -X DELETE \
    http://localhost:8080/admin/$TESTREPO/foo-1.0-1.x86_64.rpm  -i -s | grep "404 NOT FOUND"

curl -X DELETE \
    http://localhost:8080/admin/$TESTREPO  -i -s | grep "204 NO CONTENT"

[[ ! -d $TESTREPO ]]

set +x
echo "SUCCESS"
