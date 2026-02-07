# Troubleshooting

## Introduction


Palette 2/3 (Pro) are a wonderful pieces of equipment but they need to be operated in a well defined setup. While P3 (Pro) has intelligence to learn about the printers behaviour, it cannot cope with a lot of randomness... so even though some corrections may be possible, the overall performance of the printer must consistent to start with.  

In this section we'll look at some issues you may encounter and try to identify possible solutions.


## Pings


Pings are a way of palette to communicate status of an ongoing print. Pings indicate the amount of filament used vs the amount of filament required according to the Gcode file. Though ideally this number should be around 100% the actual value itself is not so important... what is important is that it is constant (+/- 0.5% over the entire print)

P2PP eg by default makes ping-checks every 350mm so a deviation of +/-1.75mm is enough to already get you out of this tolerances

Sources of deviations in pings can be:

- **Loading issue:** if the filament is not at the end of the nozzle when loading is performed, either some filament will be already extruded or extrusion will not start right away when the print starts.

- **Extruder issues:** if the extruder if losing steps, or filament is slipping in the extruder (P3 generates quite a bit of drag on the filament, so extra tensioning may be required).

- **Splice Issues:** Splices should be very consistent and very close to your filament diameter, fast splices may generate extra drag or cause blockings in the extruder that result in under usage, thin splices may break easier but also may cause slippage when passing through the extruder gears causing under extrusion there.

- **P3 Scroll Wheel Issue:** if the P3 is not correctly registering the amount of filament passing the measurements will obviously be off as well.


## Splices

### Multi material

Sometimes certain materials are not quite compatible (such as *from* PETG *to* PLA). First, try to get the same material, different colors working before attempting multi material prints.  

### Single material

If single material prints fail, check if the splices are strong and good as per mosaics guide. If your filament snaps, but it is not at the splice, it could be indicative to moisture in the filament. You could try to dry the faulty filament before attempting your next print or you could avoid that spool all together for multi color (multi material) printing.


## Klipper

When using Klipper it is recommended to use your palette in **Accessory mode**. You could try projects such as [Klipperotchy](https://github.com/shishu94/Klipperotchy) to get your Palette working into connected mode, but in my experience, I find that Klipper still is not very compatible with connected mode. My guess is that the command buffer of Klipper is just too large to be able to synchronize with the pings of the Palette (even with `M400` commands). Reducing this buffer in Klipper would not quite solve the problem because it is used for features such as pressure advance, etc.


## Saving prints

Whenever a print finishes, P3 will ask if the print was successful. It does this to determine if it should update the learning information with the newly gathered info from this print. In general: If there have been no mechanical issues and the object comes out as expected (regardless of any color issues) you should save the print. Next time you print things should get better. If you have any technical issue with the print (first layer issues, loading offset not being correct, ...) don't save the print!


# Further Troubleshooting

If you're still having trouble, head over to: [https://support.mosaicmfg.com/hc/en-us/articles/360014656533-Calibration-Print-Troubleshooting](https://support.mosaicmfg.com/hc/en-us/articles/360014656533-Calibration-Print-Troubleshooting) or [https://support.mosaicmfg.com/hc/en-us/articles/360012678493-Calibration-Print-with-CANVAS-Hub-OctoPrint-CANVAS-Plugin](https://support.mosaicmfg.com/hc/en-us/articles/360012678493-Calibration-Print-with-CANVAS-Hub-OctoPrint-CANVAS-Plugin)