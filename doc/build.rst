..
    :copyright: Copyright (c) 2018 ftrack

#################
Build and Release
#################

**ftrack Connect** can be packaged and released as binary through different systems.
In this section we'll have a closer look on how to.


1) **Building from sources in vitual environments**
2) **Building using docker**



Building from sources in vitual environments
============================================

Building from sources requires a slightly more complex setup, but ensure full control over the release process.

requirements
------------

1) `python3 <https://www.python.org/downloads/>`_ interpreter installed and avialable on $PATH 
2) an activated virtual environment created with python3 
3) source code of `ftrack-connect <git@bitbucket.org:ftrack/ftrack-connect.git>`_ checked out to the correct branch (backlog/connect-2/story)
4) source code of `ftrack-connect-package <git@bitbucket.org:ftrack/ftrack-connect-package.git>`_ checked out to the correct branch (backlog/connect-2/story)

instal ftrack-connect
---------------------

.. note::

    This process will provide you with ftrack-connect executable installed in the virtual environment.
 
1) cd into ftrack-connect folder - :ref:`ftrack-connect:installing`
2) install dependencies with :: 
    
    $ python -m pip install -r requirements.txt --force

package ftrack-connect
----------------------

.. warning::

    ( Windows only )

    Visual studio and `c++ build tools <https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019>`_ should be installed before install the requirements.
    Reference: (`link <https://stackoverflow.com/questions/40018405/cannot-open-include-file-io-h-no-such-file-or-directory>`_)

1) cd into ftrack-connect-package folder
2) install dependencies with ::
    
    $ python -m pip install -r requirements.txt --force
    
3) run the packaging (see below for details for each platform)


Linux
.....

Build tar.gz release with::

    $ python setup.py build_exe



Once build the result will be available in build/exe.linux-x86_64-**<PYTHON VERSION>**

To generate the tar.gz run from the build folder::

    $ tar -zcvf ftrack-connect-package-<PACKAGE VERSION>-<PLATFORM>.tar.gz exe.linux-x86_64-3.7 --transform 's/exe.linux-x86_64-3.7/ftrack-connect-package/'


Generate the md5 with::

    $ md5sum ftrack-connect-package-<PACKAGE VERSION>-<PLATFORM>.tar.gz > ftrack-connect-package-<PACKAGE VERSION>-<PLATFORM>.tar.gz.md5


.. note::

    Please remember to set **<PLATFORM>** to either:

    * C7 for Centos 7 compatible releases.
    * C8 for centos 8 compatible releases.




Windows
.......

Build msi release with::

    $ python setup.py bdist_msi


.. note::

    Codesign process works only on machine where the key certificate is loaded and available.
    Codesign also require to have the signtool.exe installed and available.


.. note::

    In case you are after a redistributeable exec file, you can run **bdist_msi** and find the 
    files in the **build/exe.win-amd64-3.7** folder rather than **dist** one.


To codesign
^^^^^^^^^^^


Once the msi is built, run the following commands to codesign it::

    $ signtool sign /tr http://timestamp.sectigo.com /td sha256 /fd sha256 /a <path to msi file>

At the end of the process you'll then asked to provide your token password, once done, the package should get codesigned.


MacOs
.....

Install appdmg to be able to create the dmg::

    $ npm install -g appdmg


To build without codesign
^^^^^^^^^^^^^^^^^^^^^^^^^

Build with::

    $ python setup.py bdist_mac


To build and codesign
^^^^^^^^^^^^^^^^^^^^^

Set your certificate id to **CODESIGN_IDENTITY**::

    $ export CODESIGN_IDENTITY="<your_certificate_id_here>"

Set your Apple user name to **APPLE_USER_NAME**::

    $ export APPLE_USER_NAME="<your_apple_user>"

Set your APP-specific password generated on https://appleid.apple.com/account/manage to the keychain under the name ftrack_connect_sign_pass.

Execute the following build command and follow the instructions::

    $ python setup.py bdist_mac --codesign_frameworks --codesign --create_dmg --notarize


Building using dockers
======================

As part of this repository, 3 Dockerfile are available to sendbox the build of ftrack-connect-package.

* C7.Dockerfile    [centos 7]
* C8.Dockerfile    [centos 8]
* Win10.Dockerfile [windows 10]

For further informations, please use the README file contained in the **docker** folder.

.. note::

    In order to build in docker windows, you need to have a windows 10 Pro activated and configured.

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


