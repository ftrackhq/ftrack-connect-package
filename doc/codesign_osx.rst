..
    :copyright: Copyright (c) 2014 ftrack

########
CodeSign
########

Sign the application (Manually)
--------

Set Environment variables

.. code-block:: bash

        #Set your certificate id to CODESIGN_IDENTITY
        $ export CODESIGN_IDENTITY="<your_certificate_id_here>"

        #Set your Apple user name to APPLE_USER_NAME
        $ export APPLE_USER_NAME="<your_apple_user>"

        #Set the the connect package version
        $ export CONNECT_PACKAGE_VERSION='<your_connect_package_version_here>'

        #Set your apple password to the keychain with the name AppleDevPass.
        #(Just create the item named AppleDevPass with your apple developer password in your keychain)

1. Move resource folder, common.zip, logo.icns and distutils to
Resources folder

.. code-block:: bash

    $ mv ./build/ftrack-connect.app/Contents/MacOS/resource/ ./build/ftrack-connect.app/Contents/Resources/
    $ mv ./build/ftrack-connect.app/Contents/MacOS/common.zip ./build/ftrack-connect.app/Contents/Resources/
    $ mv ./build/ftrack-connect.app/Contents/MacOS/distutils ./build/ftrack-connect.app/Contents/Resources/
    $ mv ./build/ftrack-connect.app/Contents/MacOS/logo.icns ./build/ftrack-connect.app/Contents/Resources/

2. Move the rest of files to Frameworks except the executable
ftrack_connect_package to the Frameworks folder

.. code-block:: bash

    $ macOs_folder='./build/ftrack-connect.app/Contents/MacOS/'
    $ frameworks_folder='./build/ftrack-connect.app/Contents/Frameworks/'
    $ executable_file=$macOs_folder/'ftrack_connect_package'
    $ for lib in $macOs_folder/*; do if [ ${lib} != ${executable_file} ] ; then mv $lib $frameworks_folder; fi;done

3. symlink the moved files from Resources folder back to MacOS folder
(IMPORTANT, has to be a relative symlink from MacOS)

.. code-block:: bash

    $ cd /path/to/build/ftrack-connect.app/Contents/MacOS/
    $ ln -s ../Resources/distutils ./
    $ ln -s ../Resources/common.zip ./
    $ ln -s ../Resources/icon.icns ./
    $ ln -s ../Resources/resource ./

4. symlink the moved files from Framework folder back to MacOs folder
(IMPORTANT, has to be a relative symlink from MacOS)

.. code-block:: bash

    $ cd /path/to/MacOS/folder
    $ for lib in ../Frameworks/*; do ln -s ../Frameworks/${lib} ./; done

5. Sign the app with deep and the entitlements file (we should add the
entitlements automatically to the build folder)

.. code-block:: bash

    #move back to your root folder
    $ cd /path/to/ftrack-connect-package/
    $ codesign --verbose --force --options runtime --timestamp --deep --strict --entitlements "resuource/entitlements.plist" --sign $CODESIGN_IDENTITY ./build/ftrack-connect.app

6. Create the dmg

.. code-block:: bash
    $ appdmg resource/appdmg.json build/ftrack-connect-package-1.1.2.dmg

7. Notarize the app (you have to be in a OSX system > macOS 10.14.5 and
xcode installed > Xcode 10 with your developer credentials logged)

.. code-block:: bash

    $ xcrun altool --notarize-app --primary-bundle-id "ftrack.connect.package.dmg" --username $APPLE_USER_NAME --password "@keychain:AppleDevPass" --file ./build/ftrack-connect-package-$CONNECT_PACKAGE_VERSION.dmg
    $ sudo xcode-select -s /Applications/Xcode.app
    #Save the returned UUID
    #Example: RequestUUID = dd57d23b-d825-4a1e-8444-1c7bccaec5c7
    # Check status of your request
    $ xcrun altool --notarization-history 0 -u $APPLE_USER_NAME -p "@keychain:AppleDevPass"
    # When the request finishes, you can see the url of the log with the
    following command (copy the logfileurl)
    $ xcrun altool --notarization-info <RequestUUID_code_here> -u $APPLE_USER_NAME -p "@keychain:AppleDevPass"
    # In case of a success notarization, staple the ticket to the
    distribution package (just in the app is needed, can be also done to
    the dmg but not in a zip)
    $ xcrun stapler staple "build/ftrack-connect.app"
    $ xcrun stapler staple "build/ftrack-connect-package-1.1.2.dmg"

8. Verify your app is well signed:

.. code-block:: bash

    $ codesign -vvv --deep --strict build/ftrack-connect.app
    $ spctl -a -v build/ftrack-connect.app

Sign the application (Automatically)
--------

1. Cd to the root folder of the repo

.. code-block:: bash

    $ cd /path/to/ftrack-connect-package

2. Give permissions to postBuild_one.sh and postbuild_two.sh scripts

.. code-block:: bash

    $ chmod u+x postBuild_one.sh
    $ chmod u+x postBuild_two.sh

3. Execute postBuild.sh

.. code-block:: bash

    $ ./postBuild.sh

4. When finish, follow the instructions and if notarize process succeed
execute postBuild_two.sh

.. code-block:: bash

    $ postBuild_two.sh

