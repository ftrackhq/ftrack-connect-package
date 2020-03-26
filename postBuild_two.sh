#! /usr/bin/env bash
# :copyright: Copyright (c) 2014 ftrack

#set -x #echo on
#chmod u+x postBuild_two.sh to run the script

if [ -z ${CONNECT_PACKAGE_VERSION+x} ]; then
  echo "CONNECT_PACKAGE_VERSION is unset";
  echo "Please: $ export CONNECT_PACKAGE_VERSION='<your_connect_package_version_here>'";
  exit 1
fi

root_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
macOs_folder=$root_folder'/build/ftrack-connect.app/Contents/MacOS/'
app_file=$root_folder'/build/ftrack-connect.app'
dmg_file=$root_folder'/build/ftrack-connect-package-'$CONNECT_PACKAGE_VERSION'.dmg'

xcrun stapler staple $app_file
xcrun stapler staple $dmg_file

echo "check the code is signed using the following commands: "
echo "codesign -vvv --deep --strict build/ftrack-connect.app"
echo "spctl -a -v build/ftrack-connect.app"