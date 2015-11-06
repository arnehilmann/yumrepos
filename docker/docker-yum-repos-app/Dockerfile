FROM centos

ADD yum-repos-*.noarch.rpm /tmp/
RUN yum install -y /tmp/yum-repos-*.rpm

EXPOSE 8080

CMD ["yum-repos"]
