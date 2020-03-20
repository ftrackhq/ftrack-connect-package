#set -x #echo on
#chmod u+x postBuild.sh to run the script
root_folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
macOs_folder=$root_folder'/build/ftrack-connect.app/Contents/MacOS/'
resources_folder=$root_folder'/build/ftrack-connect.app/Contents/Resources/'
frameworks_folder=$root_folder'/build/ftrack-connect.app/Contents/Frameworks/'
executable_file=$macOs_folder'/ftrack_connect_package'
app_file=$root_folder'/build/ftrack-connect.app'
dmg_file=$root_folder'/build/ftrack-connect-package-1.1.2.dmg'

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

codesign --verbose --force --options runtime --timestamp --deep --strict --entitlements "./build/entitlements.plist" --sign 73BC962FF68FBAB4E57E078D9EE80337E4E3D2CD $app_file

appdmg resource/appdmg.json $dmg_file

sudo xcode-select -s /Applications/Xcode.app

notarize_response=$(xcrun altool --notarize-app --primary-bundle-id "ftrack.connect.package.dmg" --username "lluis.casals@ftrack.com" --password "@keychain:AppleDevPass_LluisFtrack" --file $dmg_file)
echo "Please save the following RequestUUID: $notarize_response"
echo "Check the current status using the following command: xcrun altool --notarization-history 0 -u 'lluis.casals@ftrack.com' -p '@keychain:AppleDevPass_LluisFtrack'"
echo "When finish check the log of you app using the following command (put your RequestUUID number): xcrun altool --notarization-info dd57d23b-d825-4a1e-8444-1c7bccaec5c7 -u 'lluis.casals@ftrack.com' -p '@keychain:AppleDevPass_LluisFtrack'"
echo "if succed run the postBuild_two.sh"