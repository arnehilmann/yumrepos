FROM centos

RUN yum install -y rpm-build python-setuptools
ADD build-yum-repos-rpm /usr/bin/

CMD ["build-yum-repos-rpm"]

#RUN rpmbuild --rebuild yum-repos-*.src.rpm
#RUN rm -f yum-repos-*
#RUN cp $HOME/rpmbuild/RPMS/noarch/yum-repos-*.noarch.rpm .
# RUN yum install -y $HOME/rpmbuild/RPMS/noarch/yum-repos-*.noarch.rpm

# docker run -it vi $PWD:/project -w /project mycentos bash
# docker run -it -p 8080:8080 yum-repos yum-repos
