FROM apache/superset:2.0.0
#FROM 1XXXXXXXXXXX.dkr.ecr.us-east-2.amazonaws.com/harbor-foo-bar:apache-superset-2-0-0

#COPY ca-bundle.crt /etc/pki/ca-trust/source/anchors/

# Switch to root to install the required packages
USER root

RUN mkdir /app/scripts
COPY /scripts/docker-init.sh /app/scripts/
COPY /scripts/superset-entrypoint.sh /app/scripts/
COPY /scripts/docker-bootstrap.sh /app/scripts/
COPY /scripts/docker-entrypoint.sh /app/scripts/
COPY local_requirements.txt /scripts/requirements-local.txt

# Provide permissions to files
RUN ["chmod", "+x", "/app/scripts/docker-init.sh"]
RUN ["chmod", "+x", "/app/scripts/superset-entrypoint.sh"]
RUN ["chmod", "+x", "/app/scripts/docker-bootstrap.sh"]
RUN ["chmod", "+x", "/app/scripts/docker-entrypoint.sh"]

#RUN update-ca-trust enable
#RUN update-ca-trust extract

# Copy pip config file to enable pip install inside namespace when running on AWS WorkSpaces
#COPY pip.conf pip.conf
#ENV PIP_CONFIG_FILE pip.conf


# install compilers for enabling pip install of special modules
#RUN yum -y install gcc gcc-c++ unixODBC-devel libffi-devel platform-python-devel.x86_64 openssl-devel cyrus-sasl-devel openldap-devel
#RUN dnf -y update
#RUN yum -y update
#RUN yum -y update expat
RUN dnf -y upgrade
RUN yum -y upgrade

#RUN yum -y install wget
##RUN wget https://centos.pkgs.org/8/centos-baseos-x86_64/numactl-libs-2.0.12-13.el8.x86_64.rpm.html
## Install numactl dependency of mysql community release
#RUN wget https://vault.centos.org/centos/8/BaseOS/x86_64/os/Packages/numactl-libs-2.0.12-13.el8.x86_64.rpm
#RUN yum -y localinstall numactl-libs-2.0.12-13.el8.x86_64.rpm --nogpgcheck

## Install MySQL using the MySQL Yum Repository
## https://www.tecmint.com/install-latest-mysql-on-rhel-centos-and-fedora/
## Add the MySQL Yum Repository
#RUN wget https://repo.mysql.com/mysql80-community-release-el8-1.noarch.rpm
#RUN yum -y localinstall mysql80-community-release-el8-1.noarch.rpm --nogpgcheck
#RUN yum repolist enabled | grep "mysql.*-community.*"
## Install MySQL
#RUN yum -y install mysql-community-server --nogpgcheck
#RUN yum -y update --nogpgcheck
#RUN yum -y update

COPY local_requirements.txt .

RUN pip install -r local_requirements.txt
## Del pip.conf when running on AWS WorkSpaces
#RUN rm pip.conf

## Add the superset_config.py file to the container
COPY superset_config.py /app/

## We tell Superset where to find it
ENV SUPERSET_CONFIG_PATH /app/superset_config.py

# Switching back to using the `superset` user
USER superset
