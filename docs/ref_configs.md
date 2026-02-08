# Reference Configurations


!!! note

    This page offers reference configurations for several printers as well as tips and tricks to make your installation as seamless as possible. If you notice mistakes or have suggestions for additional information to be added onto this page feel free to post on the Facebook P2PP Community Help Page or update the docs yourself.


!!! warning 

    Make sure to carefully review the configurations before applying them to your setup. Some settings on one printer may not have the same result on your printer. All material on this page is provided as is with no warranty nor responsibility from out side.


## General Information

### Basic Printer Configuration

Make sure the printer is properly setup to printing single color before trying to move to multi-color printing.

- [ ] Set the Correct bed shape and size
- [ ] Calibrate your extruder
- [ ] Level bed and calibrate first layer
- [ ] Before printing assign colors to the extruders
- [ ] Don't forget to set the purge lengths - they are reset when you close the PrusaSlicer - this has nothing to do with P2PP.


**These settings will be NEEDED for all printers. Below are the basic needed settings.**

1. Start by loading your printer default profile in Prusa Slicer.

2. Set Prusa Slicer to expert mode so some of the below settings can be entered.

3. Start with the Printers Tab in Prusa Slicer

4. Go to `General > Capabilities > Extruders` Change to 4/8 and check box for `Single Extruder Multi Material`


For a more extensive setup guide, go to [P2PP Configuration](p2pp_config.md).


## Sample Configuration from members


### Prusa

#### MK3(S) - direct drive

!!! note

    Config provided by **Marc Siegel**

##### Bed Size

    Rectangular Origin-(0,0)  Size-(250,210)

##### Startup G-code


This code should be added at the end of the Prusa Slicer Printers Tab, under `Custom G-code / Startup G-Code`


    ;P2PP PRINTERPROFILE=<enter your printerprofile id here>

    ;P2PP EXTRAENDFILAMENT=120
    ;P2PP LINEARPINGLENGTH=350

    ;P2PP MATERIAL_DEFAULT_0_0_0
    ;P2PP MATERIAL_PVA_PVA_0_0_0
    ;P2PP MATERIAL_PVA_PLA_0_0_0
    ;P2PP MATERIAL_PLA_PLA_0_0_0
    ;P2PP MATERIAL_PET_PET_0_0_0

    ;P2PP CONSOLEWAIT


### Creality


#### Ender 5 S1 + CR Sonic Pad (Klipper)


!!! note

    Config provided by **JD-c0de**


##### Bed Size

    Rectangular Origin-(-5,0)  Size-(210,220)

##### Startup G-code


This code should be added at the end of the Prusa Slicer Printers Tab, under `Custom G-code / Startup G-Code`


    ;Palette 3 Pro config
    ;P2PP PALETTE3_PRO

    ;Use Accessory mode because of Klipper
    ;P2PP ACCESSORYMODE_MAFX

    ;Parameters for uploading to Palette
    ;P2PP P3_UPLOADFILE
    ;P2PP P3_SHOWPRINTERPAGE
    ;P2PP P3_HOSTNAME=<enter palettes ip-address here>

    ;P2PP PRINTERPROFILE=<enter your printerprofile id here>
    ;P2PP KLIPPER_TOOLCHANGE
    ;P2PP LINEARPINGLENGTH=350
    ;P2PP SPLICEOFFSET=80
    ;P2PP MINSTARTSPLICE=130
    ;P2PP MINSPLICE=90
    ;P2PP PURGETOPSPEED=70

    ;P2PP EXTRAENDFILAMENT=200

    ;Filament splice settings
    ; DEFAULT
    ;P2PP MATERIAL_DEFAULT_0_0_0
    ; TESTED (Stable)
    ;P2PP MATERIAL_PLA_PLA_2_1_2
    ; UNTESTED
    ;P2PP MATERIAL_ABS_ABS_4_0_0
    ; TESTED (Stable)
    ;P2PP MATERIAL_PETG_PETG_2_1_4
    ; UNTESTED
    ;P2PP MATERIAL_TPU_TPU_2_6_10
    ; TESTED (Unstable)
    ;P2PP MATERIAL_PLA_PETG_3_4_9
    ; TESTED (Stable)
    ;P2PP MATERIAL_PETG_PLA_5_2_7
    ; UNTESTED
    ;P2PP MATERIAL_PLA_PVA_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_PVA_PLA_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_PETG_PVA_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_PVA_PETG_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_TPU_PVA_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_PVA_TPU_2_6_11
    ; UNTESTED
    ;P2PP MATERIAL_PLA_TPU_2_6_10
    ; UNTESTED
    ;P2PP MATERIAL_TPU_PLA_2_6_10
    ; UNTESTED
    ;P2PP MATERIAL_PETG_TPU_2_4_10
    ; UNTESTED
    ;P2PP MATERIAL_TPU_PETG_2_4_10


### Voxellab

#### Aquila (Ender E3V2 Clone)


!!! note

    Config provided by **Casey Eberle**  
    Extruder: Bowden (490mm)


##### Bed Size

    Rectangular Origin-(0,0)  Size-(220,220)

##### Startup G-code


This code should be added at the end of the Prusa Slicer Printers Tab, under `Custom G-code / Startup G-Code`


    ; Remove the next 2 lines if you want have a PALETTE 2
    ;P2PP PALETTE3_PRO
    ;P2PP P3_PROCESSPREHEAT

    ;P2PP PRINTERPROFILE=<enter your printerprofile id here>
    ;P2PP SPLICEOFFSET=30
    ;P2PP MINSTARTSPLICE=135
    ;P2PP MINSPLICE=90
    ;P2PP MATERIAL_DEFAULT_0_0_0
    ;P2PP MATERIAL_PVA_PVA_0_0_0
    ;P2PP MATERIAL_PVA_PLA_0_0_0
    ;P2PP MATERIAL_PLA_PLA_2_0_2
    ;P2PP MATERIAL_PET_PET_0_0_0
    ;P2PP LINEARPINGLENGTH=350
    ; Adapt to the length of your bowden tube
    ;P2PP EXTRAENDFILAMENT=500

