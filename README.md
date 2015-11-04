# yum-repos

[![Build Status](https://api.travis-ci.org/arnehilmann/yum-repos.svg?branch=master)](https://travis-ci.org/arnehilmann/yum-repos)
[![Coverage Status](https://coveralls.io/repos/arnehilmann/yum-repos/badge.svg)](https://coveralls.io/r/arnehilmann/yum-repos)

minimal yum repo server, with rest API and filesystem backend

## tl;dr

```
git clone https://github.com/arnehilmann/yum-repos.git
cd yum-repos
virtualenv ve
. ve/bin/activate
. ./initenv
pip install pybuilder
pyb install_dependencies

pyb -X
```

## rest API

### list all repos

```curl http://<yourhost>/repos```

### add repo 'new-repo'
```curl -X PUT http://<yourhost>/admin/repos/new-repo```

### ...

## generate some dummy rpms

```
fpm -s dir -C empty -t rpm -n foo
```
