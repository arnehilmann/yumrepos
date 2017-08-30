# yumrepos

[![Build Status](https://api.travis-ci.org/arnehilmann/yumrepos.svg?branch=master)](https://travis-ci.org/arnehilmann/yumrepos)
[![Coverage Status](https://coveralls.io/repos/arnehilmann/yumrepos/badge.svg?branch=master&service=github)](https://coveralls.io/github/arnehilmann/yumrepos?branch=master)
[![PyPI](https://img.shields.io/pypi/v/yumrepos.svg)](https://pypi.python.org/pypi/yumrepos)

Minimal Yum Repo Server, with ReST API and deduplicating Filesystem Backend


## features

* simple ReST API: create/remove repos, upload/move/remove rpms
* fast read access: uses nginx as frontend
* dedicated update command: you decide when to recalculate repo metadata
* fast metadata calculation: uses C implementation, merges pre-calculated metadata
* deduplicated RPMs: hardlinked copies only
* supports symbolic repo links
* there is a [dedicated HiRes Promo Website](https://arnehilmann.github.io/yumrepos/index.html)


## tl;dr for centos7 end users

follow instructions in the [centos7-specific repository](https://arnehilmann.github.io/yumrepos/index.html)


## tl;dr for developers

```
git clone https://github.com/arnehilmann/yumrepos.git
cd yumrepos
scripts/init-virtualenv
. venv/bin/activate
# start a basic development server
./src/main/scripts/yumrepos
# now use the API with $HOST=http://127.0.0.1:8080/
```

then see the [full lifecycle test](src/unittest/resources/full-lifecycle-tests)


## rest API

### check if yum-repo service is up
```curl $HOST/repos/```

response: 200 OK, exit code of curl != 0



### create repo
```curl -X PUT $HOST/admin/v1/repos/NEW_REPO```

response: 201 CREATED, 403 FORBIDDEN (wrong reponame, non-existing path)



### create multiple repos
```curl -F pathspec="PATHSPEC" $HOST/admin/v1/repos```

PATHSPEC: define pathes via
[brace expansion](https://www.gnu.org/software/bash/manual/html_node/Brace-Expansion.html)

pathspec example:
```curl -F pathspec="base/{6,7}/{x86_64,noarch}" $HOST/admin/v1/repos```
results in the following repo hierarchy:
```
base/
+-- 6/
|   +-- x86_64/
|   +-- noarch/
|
+-- 7/
    +-- x86_64/
    +-- noarch/
```

response: 201 CREATED, 403 FORBIDDEN (wrong reponame, non-existing path), 400 BAD REQUEST (missing/malformed pathspec)



### check repo
```curl $HOST/$TESTREPO1/```

response: 200 OK, 404 NOT FOUND



### upload rpm
```curl -F rpm=@file_to_be_uploaded.rpm $HOST/admin/v1/repos/TARGET_REPO```

response: 201 CREATED, 404 NOT FOUND



### check metadata of uploaded rpm
```curL $HOST/admin/v1/repos/TARGET_REPO/RPM?info```

response: 200 OK (info in response body as json), 404 NOT FOUND



### move rpm to another repo
```curl -X STAGE $HOST/admin/v1/repos/SOURCE_REPO/RPM?stageto=TARGET_REPO```

response: 201 CREATED, 404 NOT FOUND (source rpm not found), 409 CONFLICT (rpm already present in target repo)



### copy rpm to another repo
```curl -X COPY $HOST/admin/v1/repos/SOURCE_REPO/RPM?stageto=TARGET_REPO```

response: 201 CREATED, 404 NOT FOUND (source rpm not found), 409 CONFLICT (rpm already present in target repo)



### delete empty repo
```curl -X DELETE $HOST/admin/v1/repos/OBSOLETE_REPO```

repsonse: 204 NO CONTENT, 409 CONFLICT (if not empty)



### link to another repo
```curl -X PUT $HOST/admin/v1/repos/NEW_REPO?link_to=REPO_ALREADY_PRESENT```

response: 201 CREATED, 404 NOT FOUND (repo not already present)



### check if repo is a link
```curl $HOST/admin/v1/repos/REPO_TO_CHECK?is_link```

repsonse: 200 OK (true or false in response body), 404 NOT FOUND



### delete rpm
```curl -X DELETE $HOST/admin/v1/repos/REPO/RPM_TO_DELETE```

response: 204 NO CONTENT, 404 NOT FOUND



### delete repo recursivly
```curl -X DELETERECURSIVLY $HOST/admin/v1/repos/REPO_TO_BE_DELETED```

response: 204 NO CONTENT, 404 NOT FOUND



### shutdown repo server
```curl -X POST $HOST/admin/v1/shutdown```

response: 200 OK, 403 FORBIDDEN (when not in standalone mode)



## development cheat sheet

### build in docker container

```
docker run -it -v $PWD:/local -w /local centos:7 bash
yum install -y createrepo_c
scripts/init-virtualenv
. ve/bin/activate

# do stuff
pyb
```

### create dummy rpm, when fpm tool not available

```
docker run -it -v $PWD:/local -w /local alanfranz/fwd-centos-7 fpm -s empty -t rpm -n foo -v 1.42
```

### build debian package of createrepo_c, for build on travis-ci

```
git clone https://github.com/rpm-software-management/createrepo_c.git
cd createrepo_c
```

```
docker run -v $PWD:/local -it ubuntu:trusty bash
mkdir build
cd build
apt-get update
apt-get install -y libbz2-dev cmake libexpat1-dev libmagic-dev libglib2.0-dev libcurl4-openssl-dev \
    libxml2-dev libpython2.7-dev librpm-dev libssl-dev libsqlite3-dev liblzma-dev zlib1g-dev doxygen \
    check python-nose
cmake ..
make
mkdir -p docroot/usr/{bin,lib}
mv src/lib* docroot/usr/lib
mv src/*_c docroot/usr/bin
exit
```

```
fpm -t deb -n createrepo_c -s dir -C docroot/ --verbose .
```
