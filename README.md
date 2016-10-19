# yumrepos

[![Build Status](https://api.travis-ci.org/arnehilmann/yumrepos.svg?branch=master)](https://travis-ci.org/arnehilmann/yumrepos)
[![Coverage Status](https://coveralls.io/repos/arnehilmann/yumrepos/badge.svg?branch=master&service=github)](https://coveralls.io/github/arnehilmann/yumrepos?branch=master)

Minimal Yum Repo Server, with ReST API and Filesystem Backend

## tl;dr for centos7 end users

follow instructions in our [centos7-specific repository](https://arnehilmann.github.io/yumrepos/index.html)


## tl;dr for developers

```
git clone https://github.com/arnehilmann/yumrepos.git
cd yumrepos
scripts/init-virtualenv
. venv/bin/activate
```

## rest API

### check if yum-repo service is up
```curl $HOST/repos/```

response: 200 OK, exit code of curl != 0



### create repo
```curl -X PUT $HOST/admin/v1/NEW_REPO```

response: 201 CREATED, ?



### check repo
```curl $HOST/$TESTREPO1/```

response: 200 OK, 404 NOT FOUND



### upload rpm
```curl -F rpm=@file_to_be_uploaded.rpm $HOST/admin/v1/TARGET_REPO```

response: 201 CREATED, 404 NOT FOUND



### check metadata of uploaded rpm
```curL $HOST/admin/v1/TARGET_REPO/RPM/info```

response: 200 OK (info in response body as json), 404 NOT FOUND



### move rpm to another repo
```curl -X STAGE $HOST/admin/v1/SOURCE_REPO/RPM/stageto/TARGET_REPO```

response: ?



### delete empty repo
```curl -X DELETE $HOST/admin/v1/OBSOLETE_REPO```

repsonse: 204 NO CONTENT, 409 CONFLICT (if not empty)



### link to another repo
```curl -X PUT $HOST/admin/v1/NEW_REPO?link_to=REPO_ALREADY_PRESENT```

response: 201 CREATED



### check if repo is a link
```curl $HOST/admin/v1/REPO_TO_CHECK/is_link```

repsonse: 200 OK (true or false in response body), 404 NOT FOUND



### delete rpm
```curl -X DELETE $HOST/admin/v1/REPO/RPM_TO_DELETE```

response: 204 NO CONTENT, 404 NOT FOUND



### delete repo recursivly
```curl -X DELETERECURSIVLY $HOST/admin/v1/REPO_TO_BE_DELETED```

response: ?



### shutdown repo server
```curl -X POST $HOST/admin/v1/shutdown```

response: ?

