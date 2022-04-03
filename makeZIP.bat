@echo off
rem #############################################
rem # (c) Copyright 2020 - Tom Van den Eede
rem # required python/pyQt5/cx_freeze to be setup
rem # p2pp must be working prior to running
rem #############################################


rem  Remove ealier builds and create a new one
rem  #########################################

Rmdir /S /Q _build_update_
Mkdir _build_update_
Cd _build_update_

git clone --branch master https://github.com/tomvandeneede/p2pp.git

rem Create the new BUILD
rem ####################
cd p2pp
python setup.py build

rem Determine the version
rem ####################
python version.py >out.txt
set /p version=<out.txt
del out.txt

set name=p2pp_%version%

cd build
Rmdir /S /Q p2pp

rem create a ZIP file
rem #################
move exe.win-amd64-3.9 p2pp
del %name%.zip
"c:\Program Files\WinRAR\WinRar.exe" a -m5 -afzip -y %name%.zip p2pp

rem copy the file to dropbox
rem ########################
copy %name%.zip "c:\users\tomvandeneede\dropbox\public\p2pp\Development\Windows\"

rem # go up to the top level #
cd ..
cd ..
cd ..
Rmdir /S /Q _build_update_


