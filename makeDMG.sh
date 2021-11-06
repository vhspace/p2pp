
#!/bin/zsh

version=$(python3 version.py)
outputfile="/Users/tomvandeneede/Dropbox/Public/p2pp/Development/MacOS/p2pp_${version}.dmg"
python3 setup.py py2app --packages=PIL
cp -r dist/* /Applications/
hdiutil create dist/p2pp.dmg -ov -volname "p2ppInstaller" -fs HFS+ -srcfolder "dist"
rm /Users/tomvandeneede/Dropbox/Public/p2pp.dmg
rm ${outputfile}
hdiutil convert dist/p2pp.dmg -format UDZO -o ${outputfile}
rm dist/p2pp.dmg
rm -rf build dist

