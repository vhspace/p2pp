# Purge Length Calculation


## Introduction

Getting the right purge length is crucial for successful prints without "rogue lines" or colour bleeding. Traditionally we've used a "Test Print" block to muck around with trying to find the right length. My approach is a little different and so far has worked very well to get me great prints every time.


## The Process


My process is a simple one and can be done outside of Palettes splicing. For ease of reference, I'll refer to the two filaments as "A" and "B". The goal is to figure out the purge length required to transition from A to B.

1. Preheat your nozzle for the hotter of the two filaments we're looking to determine the purge for. While you're at it raise your Z-Axis up so you can see the nozzle and what's going on.

2. Load filament A

3. Extrude 5cm of filament A out of the extruder nozzle.

4. Eject filament A

5. Load Filament B using the jog wheel. Load only till you see filament A extruding/moving a little extruding out of the nozzle. Stop immediately.

6. Place a mark on the filament 150mm from the top of your extruder. (You may need more if it's a strong colour)

7. Both Methods: Slowly jog the filament until you see the filament change from A to B.

8. Look at the extrusion. Is it clean? Is it the correct colour? Is it free from remnants of the previous filament colour? if no, continue at step 7. If yes, proceed to step 9.

9. Measure the consumed filament from the top of the extruder to the mark you placed on step 6.

10. We're done. you can repeat again from step 4 to do the reverse purge calculation (from B to A) if you like.


## Math Time!


1. Take the length you used in step 6 above and subtract the length you measured in step 9.

    E.g. $150 - 100 = 50$

2. Add 30% for an error buffer (This can be later decreased when you're confident)

    $50 \cdot 1.3 = 65$

3. For Slic3r, remember the values are in mm3. We need to multiply this value by ~2.4 for filament with a 1.75 mm diameter.

    $65 \cdot 2.4 = 156$

4. This value is what should be used in the "Loaded" box when swapping from filament A to Filament B.