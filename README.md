# yum-repos

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
yum-repos
full-lifecycle-test.sh

```

## generate some dummy rpms

```
fpm -s dir -C empty -t rpm -n foo
```
