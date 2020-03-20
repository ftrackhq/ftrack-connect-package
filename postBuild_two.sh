#set -x #echo on
#chmod u+x postBuild_two.sh to run the script
# Activate this if we like to validate that an argument for the code is passed
#if [ -z "$1" ] ;
#  then
#    echo "please provide the notarizer code"
#    exit 1
#fi;

root_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
macOs_folder=$root_folder'/build/ftrack-connect.app/Contents/MacOS/'
app_file=$root_folder'/build/ftrack-connect.app'
dmg_file=$root_folder'/build/ftrack-connect-package-1.1.2.dmg'

xcrun stapler staple $app_file
xcrun stapler staple $dmg_file

echo "check the code is signed using the following commands: "
echo "codesign -vvv --deep --strict /Users/lluisftrack/work/brokenC/ftrack/repos/ftrack-connect-package/build/ftrack-connect.app"
echo "spctl -a -v /Users/lluisftrack/work/brokenC/ftrack/repos/ftrack-connect-package/build/ftrack-connect.app"