---
title: The YumRepos Repository :o)
header-includes:
    <meta charset="utf-8">
    <meta name="description" content="Repository for the YumRepos Packages">
    <meta name="author" content="Arne Hilmann <arne.hilmann@gmail.com>">

    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link href="https://fonts.googleapis.com/css?family=Raleway:400,300,600" rel="stylesheet" type="text/css">

    <link rel="stylesheet" href="css/normalize.css">
    <link rel="stylesheet" href="css/skeleton.css">

    <link rel="icon" type="image/png" href="images/favicon.png">
---

<div class="container">
<div class="row">
<div class="column" style="margin-top: 10%; margin-bottom: 20%;">


## YumRepos Repo

This is a yum repository for the yumrepos rpms and its centos7 configuration!


#### Prerequisites

* centos7 machine, including root access and internet access


#### Installation

1. enable epel repos and yum utilities(as root user):<br/>
    ```yum install epel-release yum-utils```
2. enable this repo:<br/>
    ```yum-config-manager --add-repo https://arnehilmann.github.io/yumrepos/yumrepos.repo```
3. install yumrepos configuration for centos7:<br/>
    ```yum install yumrepos-behind-nginx-on-centos7```


#### Next Steps

Follow the instructions on your new shiny yumrepos server:<br/>
```https://[YUMREPOS_SERVER]/```


#### Further Questions/Comments?

Have a look at the <a href="https://github.com/arnehilmann/yumrepos#rest-api">API</a>.<br/>
And see the <a href="https://github.com/arnehilmann/yumrepos">admin part</a>
or the <a href="https://github.com/arnehilmann/yumrepos-behind-nginx-on-centos7">centos7-specific configuration</a>
of this installation.
