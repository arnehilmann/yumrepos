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
    <link rel="stylesheet" href="css/custom.css">

    <link rel="icon" type="image/png" href="images/favicon.png">

    <style>
        .header{background-image:url("images/header3.jpeg");}
        .header, .footer {background-size:cover; color:#ccc; }
        .oncoloredbg, .oncoloredbg * {font-weight:400;text-shadow:0 0 2px black;}
    </style>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
    <script src="js/site.js"></script>
---
<div class="section header">
<div class="container oncoloredbg" style="padding-top: 15%; padding-bottom: 5%;">

## YumRepos Repo

This is the yum repository for the yumrepos rpms and its centos7 configuration!

</div>
</div>

<div class="navbar-spacer"></div>
<nav class="navbar">
<div class="container">
<ul class="navbar-list">
<li class="navbar-item"><a class="navbar-link" href="#intro">Intro</a></li>
<li class="navbar-item"><a class="navbar-link" href="#installation">Installation</a></li>
<li class="navbar-item"><a class="navbar-link" href="#examples">On Github</a></li>
</ul>
</div>
</nav>

<div class="container">
<div class="row">
<div class="column" style="margin-top: 5%; margin-bottom: 20%;">

#### Prerequisites

* centos7 machine, including root access and internet access


#### Installation

1. enable epel repos and yum utilities (as root user):<br/>
    ```sudo yum install epel-release yum-utils```
2. enable this repo:<br/>
    ```sudo yum-config-manager --add-repo https://arnehilmann.github.io/yumrepos/yumrepos.repo```
3. install yumrepos configuration for centos7:<br/>
    ```sudo yum install yumrepos-behind-nginx-on-centos7```


#### Next Steps

Follow the instructions on your new shiny yumrepos server:<br/>
```https://[YUMREPOS_SERVER]/```


#### Further Questions/Comments?

Have a look at the <a href="https://github.com/arnehilmann/yumrepos#rest-api">API</a>.<br/>
And see the <a href="https://github.com/arnehilmann/yumrepos">admin part</a>
or the <a href="https://github.com/arnehilmann/yumrepos-behind-nginx-on-centos7">centos7-specific configuration</a>
of this installation.
