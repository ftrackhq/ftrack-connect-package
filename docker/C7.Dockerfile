#########################################################################
# :copyright: Copyright (c) 2020 ftrack
#

FROM inveniosoftware/centos7-python:3.6
LABEL ftrack AB

RUN yum -y update
RUN yum -y groupinstall "Development Tools"

RUN yum install -y *libxcb* libXi libSM fontconfig libXrender libxkbcommon-x11 qt5*

RUN python -m pip install --upgrade pip

RUN mkdir -p /usr/src/app

# install connect
WORKDIR /usr/src/app
RUN git clone -b backlog/connect-2/story https://bitbucket.org/ftrack/ftrack-connect.git
WORKDIR /usr/src/app/ftrack-connect
RUN python -m pip install -r requirements.txt
RUN python setup.py install

WORKDIR /usr/src/app
RUN git clone -b backlog/connect-2/story https://bitbucket.org/ftrack/ftrack-connect-package.git
WORKDIR /usr/src/app/ftrack-connect-package
RUN python -m pip install -r requirements.txt
RUN python setup.py build

WORKDIR /usr/src/app/ftrack-connect-package/build
RUN tar -czvf ftrack-connect-2-C7.tar.gz exe.linux-x86_64-3.6
