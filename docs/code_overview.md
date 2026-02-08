# Code Overview


## [p2ppparams.py](https://github.com/vhspace/p2pp/blob/master/p2pp/p2ppparams.py)


Here will all the P2PP parameters be checked and mapped to their corresponding variables. These variables can be used throughout the project.


## [psconfig.py](https://github.com/vhspace/p2pp/blob/master/p2pp/psconfig.py)


All the settings and parameters from PrusaSlicer are being stripped from the generated gcode.


## [gcode.py](https://github.com/vhspace/p2pp/blob/master/p2pp/gcode.py)


All gcode commands are getting stripped from the gcode file and categorised by type. The gcode also gets manipulated using the functions provided in the file.


## [mcf.py](https://github.com/vhspace/p2pp/blob/master/p2pp/mcf.py)


Contains the main logic for processing the gcode. (It links all the features here)


## [omega.py](https://github.com/vhspace/p2pp/blob/master/p2pp/omega.py)


Generate the Omega; Header that drives the Palette to p2pp_process_file filament.  
All the splice lengths and splice algorithms are inserted into this file.


## [pings.py](https://github.com/vhspace/p2pp/blob/master/p2pp/pings.py)


Contains the logic for inserting pings.


## [p3_upload.py](https://github.com/vhspace/p2pp/blob/master/p2pp/p3_upload.py)


Code for uploading to the P3 (Pro).


## [side_wipe.py](https://github.com/vhspace/p2pp/blob/master/p2pp/sidewipe.py)


Contains side wipe logic.


## [purgetower.py](https://github.com/vhspace/p2pp/blob/master/p2pp/purgetower.py)


Contains purge tower logic.


## [manualswap.py](https://github.com/vhspace/p2pp/blob/master/p2pp/manualswap.py)


Contains manual swap logic.


## [checkversion.py](https://github.com/vhspace/p2pp/blob/master/p2pp/checkversion.py)


Contains check version logic.


## [variables.py](https://github.com/vhspace/p2pp/blob/master/p2pp/variables.py)


Contains all the variables with their default values.


## [gui.py](https://github.com/vhspace/p2pp/blob/master/p2pp/gui.py)

Contains gui logic.

## [formatnumbers.py](https://github.com/vhspace/p2pp/blob/master/p2pp/formatnumbers.py)


Helper for formatting numbers.


## [colornames.py](https://github.com/vhspace/p2pp/blob/master/p2pp/colornames.py)


Helper for determining the name of colors.


## [P2PP.py](https://github.com/vhspace/p2pp/blob/master/P2PP.py)


Main application code. (This does not contain any post processor logic)


## [setup.py](https://github.com/vhspace/p2pp/blob/master/setup.py)


Used to build the application.


## [genpreview.py](https://github.com/vhspace/p2pp/blob/master/p2pp/genpreview.py)


Developer tool to visualize the preview. (Not yet tested)


## [bedprojection.py](https://github.com/vhspace/p2pp/blob/master/p2pp/bedprojection.py)


Developer tool to visualize the printbed area. (Not yet tested)


## [tower.py](https://github.com/vhspace/p2pp/blob/master/tower/tower.py)


Developer tool to test purge tower generation algorithms. (Not yet tested)