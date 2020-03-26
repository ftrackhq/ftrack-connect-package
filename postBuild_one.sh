#! /usr/bin/env bash
# :copyright: Copyright (c) 2014 ftrack

#set -x #echo on
#chmod u+x postBuild_one.sh to run the script

if [ -z ${CONNECT_PACKAGE_VERSION+x} ]; then
  echo "CONNECT_PACKAGE_VERSION is unset";
  echo "Please: $ export CONNECT_PACKAGE_VERSION='<your_connect_package_version_here>'";
  exit 1
fi

if [ -z ${CODESIGN_IDENTITY+x} ]; then
  echo "CODESIGN_IDENTITY is unset";
  echo "Please: $ export CODESIGN_IDENTITY='<your_certificate_id_here>'";
  exit 1
fi

if [ -z ${APPLE_USER_NAME+x} ]; then
  echo "APPLE_USER_NAME is unset";
  echo "Please: $ export APPLE_USER_NAME='<your_apple_user>'";
  exit 1
else
  applePass=`security find-generic-password -s AppleDevPass`
  if [ -z ${applePass+x} ]; then
    echo "AppleDevPass is unset in the keychain";
    echo "Please: create the item named AppleDevPass with your apple developer
    password in your keychain";
    exit 1
  fi
fi

root_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
macOs_folder=$root_folder'/build/ftrack-connect.app/Contents/MacOS/'
resources_folder=$root_folder'/build/ftrack-connect.app/Contents/Resources/'
frameworks_folder=$root_folder'/build/ftrack-connect.app/Contents/Frameworks/'
executable_file=$macOs_folder'/ftrack_connect_package'
app_file=$root_folder'/build/ftrack-connect.app'
dmg_file=$root_folder'/build/ftrack-connect-package-'$CONNECT_PACKAGE_VERSION'.dmg'

mv $macOs_folder/resource $resources_folder
mv $macOs_folder/distutils $resources_folder
mv $macOs_folder/common.zip $resources_folder
mv $macOs_folder/logo.icns $resources_folder

echo $executable_file
for lib in $macOs_folder/*;
do if [ $lib != $executable_file ] ;
then mv $lib $frameworks_folder;
fi;
done;

cd $macOs_folder

ln -s ../Resources/distutils ./
ln -s ../Resources/common.zip ./
ln -s ../Resources/icon.icns ./
ln -s ../Resources/resource ./

for lib in ../Frameworks/*;
do ln -s ../Frameworks/${lib} ./;
done;


cd $root_folder

codesign --verbose --force --options runtime --timestamp --deep --strict --entitlements "./build/entitlements.plist" --sign $CODESIGN_IDENTITY $app_file

appdmg resource/appdmg.json $dmg_file

sudo xcode-select -s /Applications/Xcode.app

notarize_response=$(xcrun altool --notarize-app --primary-bundle-id "ftrack.connect.package.dmg" --username $APPLE_USER_NAME --password "@keychain:AppleDevPass" --file $dmg_file)
echo "Please save the following RequestUUID: $notarize_response"
echo "Check the current status using the following command:
xcrun altool --notarization-history 0 -u APPLE_USER_NAME -p '@keychain:AppleDevPass'"
echo "When finish check the log of you app using the following command
(put your RequestUUID number):
xcrun altool --notarization-info <RequestUUID_code_here>
-u APPLE_USER_NAME -p '@keychain:AppleDevPass'"
echo "if succed run the postBuild_two.sh"