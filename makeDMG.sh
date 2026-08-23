
#!/bin/zsh

version=$(python3 version.py)
outputfile="/Users/vhspace/Dropbox/Public/p2pp/Development/MacOS/p2pp_${version}.dmg"
#outputfile="/Users/vhspace/Desktop//p2pp_${version}.dmg"
rm dist/p2pp.dmg
rm -rf build dist
python3 setup.py py2app
rm -rf dist/p2pp.app/Contents/plugins
cp -r dist/* /Applications/
hdiutil create dist/p2pp.dmg -ov -volname "p2ppInstaller" -fs HFS+ -srcfolder "dist"
rm /Users/vhspace/Dropbox/Public/p2pp.dmg
rm ${outputfile}
hdiutil convert dist/p2pp.dmg -format UDZO -o ${outputfile}

