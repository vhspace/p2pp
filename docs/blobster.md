# Blobster Setup


## Purpose


BLOBSTER is a (currently only) Prusa MK3S printer extension that allows for eficient extruder purging through a side-purge mechanism attached to the right X-rod holder of the printer. BLOBSTER is being developped by Evzen Mayer as an open source project. More information on this device and how to make one can be found [here](https://github.com/blobster-io/blobster).


## What setup is required


BLOBSTER has 2 modes that can be used under P2PP - Standard mode and Advanved mode. Both will be explained in the next sections.


### Standard Mode


In standard mode BLOBSTER will take the following configuration parameters (values indicated are the default values pre-programmed in P2PP):  

    ;P2PP BLOBSTER_ENABLE
    ;P2PP BLOBSTER_PURGEPOSITION=254
    ;P2PP BLOBSTER_BLOBSIZE=180
    ;P2PP BLOBSTER_ENGAGETIME=1000
    ;P2PP BLOBSTER_BLOBSPEED=200
    ;P2PP BLOBSTER_COOLINGTIME=60
    ;P2PP BLOBSTER_PRIME_BLOBS=0
    ;P2PP BLOBSTER_CLEARANCE_MM=30
    ;P2PP BLOBSTER_RETRACT=3


### Advanced Mode


In advanced mode BLOBSTER will take the following configuration parameters (values indicated are the default values pre-programmed in P2PP). There are NO default values for the ADVANCED_LENGTH, ADVANCED_FAN and ADVANCED_SPEED parameters.  


    ;P2PP BLOBSTER_ENABLE
    ;P2PP BLOBSTER_ADVANCED
    ;P2PP BLOBSTER_PURGEPOSITION=254
    ;P2PP BLOBSTER_COOLINGTIME=60
    ;P2PP BLOBSTER_PRIME_BLOBS=0
    ;P2PP BLOBSTER_CLEARANCE_MM=30
    ;P2PP BLOBSTER_ENGAGETIME=1000
    ;P2PP BLOBSTER_RETRACT=3
    ;P2PP BLOBSTER_ADVANCED_LENGTH=100,100,8
    ;P2PP BLOBSTER_ADVANCED_SPEED=300,200,100
    ;P2PP BLOBSTER_ADVANCED_FAN=0,20,80


## Command explaination


- `BLOBSTER_ENABLE`  
This ocmmand instructs P2PP to generate code for usage with the BLOBSTER hardware. Please note that for P2PP BLOBSTER is considered a side-purge mechanism so you will have to move the tower off the bed as a secondary trigger to use BLOBSTER.

- `BLOBSTER_ADVANCED` (Advanced mode only)  
Triggers the use of the ADVANCED features of BLOBSTER config in P2PP. Note that you will have to supply the ADVANCED_LENGTH, ADVANCED_FAN and ADVANCED_SPEED parameters in order to use this feature

- `BLOBSTER_ADVANCED_LENGTH` (Advanced mode only)  
BLOBSTER_ADVANCED_LENGTH is a list of lengths in mm. The sum of all these values defines the size of ONE blob. For each element in the list, there needs to be a corresponding element in the BLOBSTER_ADVANCED_SPEED and BLOBSTER_ADVANCED_FAN list that defines the fan speed and purge speed of that section. Purpose of these settings is to get better control over the BLOB formation, specially with larger blobs All values must be WHOLE numbers separated by a comma

- `BLOBSTER_ADVANCED_SPEED` (Advanced mode only)  
BLOBSTER_ADVANCED_SPEED defines the speed in mm/min at which the specific segment of the blob will be printed. The number of elements in this list needs to match the number of elements in the BLOBSTER_ADVANCED_LENGTH list.
All values must WHOLE numbers separated by a comma

- `BLOBSTER_ADVANCED_FAN` (Advanced mode only)  
BLOBSTER_ADVANCED_FAN defines the fan speed in % for a specific section of the blob. It allows for tweaking the cooling applied already during the generation of the blob. The number of elements in this list needs to match the number of elements in the BLOBSTER_ADVANCED_LENGTH list.
All values must WHOLE numbers in range of [0-100] separated by a comma

- `BLOBSTER_PURGEPOSITION`  
Sets the X-coordinate of the purge position. Before producing a blob, the printer will move the head into that position before starting to purge

- `BLOBSTER_COOLINGTIME`  
Defines the cooling time after the blob is generated with the fan blowing at full speed of ver blob. This will allow the blob to solidify and be pushed off afterwards.

- `BLOBSTER_CLEARANCE_MM`  
When printing lower layers, BLOBSTER will sit underneath the bed. In order to engage, the hardware must move in place over the bed to the print head will need to raise a few mm to make room for BLOBSTER. This amount can be altered by using the BLOBSTER_CLEARANCE_MM command. The default of 30mm should just be fine, but you may beed to change in case you make changes to the BLOBSTER hardware yourself

- `BLOBSTER_ENGAGETIME`  
BLOBSTER uses servo motors to put the arm in place. Therefor it takes a short while for the arm to engage after the print head moves into the purging position. This parameter defines the number of miliseconds the printer waits to start purging after the head has been moved into it's purging position.

- `BLOBSTER_RETRACT`  
Defines the amount of retract implemented during the moved between the purging position and the print. You can play with this variable if you encounter stringing.

- `BLOBSTER_BLOBSIZE` (Standard mode only)  
Defines the amount of filament deposited in one BLOB. The amount is specified in mm

- `BLOBSTER_BLOBSPEED` (Standard mode only)  
Defines the speed in mm/min at which the blob will be printed. The amount is specified in mm/min

- `BLOBSTER_PRIME_BLOBS`
Since the rower needs to be put besides the print bed in BLOBSTER mode, there is no option to use a skirt because that would partially print off the bed. When getting a short splice warning, you can then add one or more PRIME_BLOBS. These are blobs generated right before the actual print starts so the first splice will become longer.


# Good luck & happy printing !!!