..
    :copyright: Copyright (c) 2018 ftrack

#################
Build and Release
#################

ftack Connect can be packaged and released as binary though different systems.
In this section we'll have a closer look on how to.


1) **Building from sources in vitual environments**
2) **Building using docker**


Building from sources in vitual environments
============================================

Building from sources requires a slightly more complex setup, but ensure full control over the release process.

requirements
------------

1) python3 interpreter installed and avialable on $PATH
2) an activated virtual environment created with python3 
3) source code of ftrack-connect
4) source code of ftrack-connect-package

instal ftrack-connect
---------------------

.. note::

    This process will provide you with ftrack-connect executable installed in the virtual environment.

1) cd into ftrack-connect folder
2) install dependencies with : python -m pip install -r requirements.txt --force

package ftrack-connect
---------------------

1) cd into ftrack-connect-package folder
2) install dependencies with : python -m pip install -r requirements.txt --force
3_ 


Building using dockers
======================

.. note:: 
    
    Docker builds are currently available only for Linux (Centos 7 and 8) and Windows. 

.. note::

   If you are building on desktop and not on CI it is suggested to add the flag --no-cache to ensure no previous cache is used.



Windows
-------

.. warning::

    In order to run windows containers, is required windows **10 professional** or above.


.. code-block::

   docker build --rm -t ftrack/connect-package:win10 -f Win10.Dockerfile .


Linux C7
--------

.. code-block::

    docker build --rm -t ftrack/connect-package:c7 -f C7.Dockerfile .


Linux C8
--------

.. code-block::

    docker build --rm -t ftrack/connect-package:c8 -f C8.Dockerfile .





Run 
---

.. note::

    The image has to **run** a first time before extracting the built result.


.. code-block::

    docker run ftrack/connect-package:<TAG>


Extract builds
--------------

To get the latest **CONTAINER ID** number.

.. code-block::

    docker ps -l



Windows
.......

.. code-block::

    docker cp CONTAINER ID:"/usr/src/app/ftrack-connect-package/dist/ftrack Connect-2.0-win64.msi" .


Linux C7
........

.. code-block::

    docker cp CONTAINER ID:"/usr/src/app/ftrack-connect-package/build/ftrack Connect-2.0-C7.tar.gz" .


Linux C8
........

.. code-block::

    docker cp CONTAINER ID:"/usr/src/app/ftrack-connect-package/build/ftrack Connect-2.0-C8.tar.gz" .


Debug
-----


To inspect the docker run :

.. code-block::

    docker run -ti <docker image id> bash


