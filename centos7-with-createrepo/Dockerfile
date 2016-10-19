FROM centos:7
MAINTAINER "Arne Hilmann" <arne.hilmann@gmail.com>

RUN yum install -y createrepo_c && yum clean all
CMD ["createrepo_c", "/repo"]
