# First Print Calibration


## Introduction


Undoubtedly, the first print calibration is vital for your success in printing with a Palette device. If this is not done correctly and accurately, you'll have a very difficult time ahead.

The first print calibration is done per printer profile which is assigned a unique value called the `PrinterID`. The PrinterID is sent to the Palette device via GCODE when you start a print. This in turn instructs the Palette to recall calibration data from your printer profile to be reused in the new print.

These values can be found simply by navigating to them via the Palettes settings screen: Settings -> Preferences -> Printer Profiles.


### Loading offset "LO"

The value Palette devices use to determine the exact distance from the extruder gears and all the way down to the tip of the nozzle.

### Historical Modifier "HM"

A percentage of drift from pings/pongs and saved calibration data from successful prints.


## Crucial information for success

**Before you proceed, I cannot stress these points enough:**

1. DO NOT RUSH AHEAD  

2. DO NOT PRESS NEXT BEFORE YOU'VE COMPLETED THE TASK ON THE SCREEN  

3. CALIBRATE EXTRUDER E-STEPS - [https://mattshub.com/2017/04/19/extruder-calibration/](https://mattshub.com/2017/04/19/extruder-calibration/)  

4. CALIBRATE EXTRUSION RATIO(s) FOR YOUR FILAMENT - also [https://mattshub.com/2017/04/19/extruder-calibration/](https://mattshub.com/2017/04/19/extruder-calibration/)  

5. DISABLE AUTO FILAMENT LOAD on your printer. You'll NEVER be able to calibrate with it on.  

6. Splice tuning is crucial, unless you like failed prints and filament jams.  

7. The USB Connector on the Palettes end is VERY fragile. Don't use it as a clothes-line. If you need to unplug the USB cable, do it from the Raspberry Pi/Canvas Hub/PC Side.


## The Process

Read "Crucial information for success", twice. Proceed only after this is completed.


### Preliminary Instructions


If you've come here because you've already tried and failed, These are the steps I recommend:

1. Factory Default your Palette device: Settings -> Preferences -> Reset to Factory Defaults

2. Unplug the USB Cable for your Palette device from Raspberry Pi/PC/Canvas Hub

3. Power Cycle the Palette device (Turn Off Wait 5+seconds, Turn On)

4. Return USB Cable

5. When asked, ensure you enter the correct length for the out-going tube.

6. Calibrate Palette: Settings -> Calibrate Palette. When Calibrating Palette you will be asked to Pull the filament a few times during the process. Its crucial that you pull **VERY** slowly, that you **DO NOT RUSH** and when you've pulled the filament and it's hit the buffer switch that you **STOP PULLING IMMEDIATELY**. Only pull the filament again when asked.


### First print calibration


1. Start the print as you normally would. You should get the "First Print" wizard on the Palettes Screen.

2. Clear the Output as requested - Press Next

3. Load the filaments as requested

4. You should now be at the screen where it asks you to load Clear filament. Remain on this screen until my instructions tell you to proceed.

5. Pre-heat your hotend. Load White, clear or the complete opposite colour to any of the colours in your first print into your extruder.

6. Extrude this filament all the way into the nozzle and extrude at least 5cm of filament. Remove the wasted extruded filament.

7. Eject the filament from the hot end normally. DO NOT cold pull, eject it normally.

8. Palette should have finished making filament at this stage.

9. Press NEXT on the Palette Screen to proceed past the "Load clear" screen.

10. You should now be at the "Load Filament into the extruder Gears" screen. It means exactly as it says. If you have Auto Filament load enabled, you're going to have a very hard time at this step. You need to disable that feature (You read the instructions above, right?). You want to load the filament into the gears so that the extruder gears have JUST grabbed the filament. It should look like this:

                |                |
        YES:   O|O       NO:    O|O
                                 |
                                 |

11. Once you've confirmed you've not over-loaded your filament, you can press Next/Continue.

12. Clip the Outgoing tube into the Extruder as instructed and press Next/Continue.

13. The next step is to slowly jog the filament so that it is feeding down into the nozzle. At this step, Palette is measuring the distance from the extruder gears to the nozzle. You must **STOP** when you see **ANY** sign of the new filament.

!!! tip

    Jog the filament 1-2mm at a time and wait a second or so to see if there is any filament extruded. Keep doing this until you start to see the light/white/clear filament starting to extrude. Slow down jogging to .1 - 1mm at a time. **Stop immediately** when you see the colour change.

14. Press Next and follow the remainder of the steps on the screen to start your print.


That should be it! your Palette should be calibrated for your printer!
