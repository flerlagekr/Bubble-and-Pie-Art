#  This code will take an SVG created by the Arjan Westerdiep's Circle Packer (https://drububu.com/miscellaneous/shapepacker/index.html) 
#  Note: The packer should be run with a simple circle SVG (fill), rotation enabled, and background color disabled.
#  Then extract each circle and create a file, Bubbles.csv which contains the coordinates and size (area) of each.
#  It will then look up the color from the original image, then create multiple slight variants of that color...
#  ...in order to create multiple slices of a pie chart.
#  The code will also write a separate file, Colors.csv which will include the color palette.
#  The goal fo the code is to allow you to thn visualize the pie chart art in Tableau.
#
#  Written by Ken Flerlage, March, 2020
#
#  This code is in the public domain
#----------------------------------------------------------------------------------------------------------------------------------------

from xml.dom import minidom
from base64 import b16encode
import math
import sys
import os
import random
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from tkinter import Tk
 
#---------------------------------------------------------------------------------------------------------------------------------------- 
# Prompt for the input svg file.
#---------------------------------------------------------------------------------------------------------------------------------------- 
def get_svg_file():
    root = Tk()
    root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select SVG File from Packer",filetypes = (("Scalable Vector Graphic","*.svg"),("All Files","*.*")))
    root.withdraw()

    return root.filename 

#---------------------------------------------------------------------------------------------------------------------------------------- 
# Prompt for the input svg file.
#---------------------------------------------------------------------------------------------------------------------------------------- 
def get_image_file():
    root = Tk()
    root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select Original Image File",filetypes = (("Portable Network Graphic","*.png"),("JPEG Image","*.jpg"),("All Files","*.*")))
    root.withdraw()

    return root.filename 

#---------------------------------------------------------------------------------------------------------------------------------------- 
# Convert RGB to hex
#---------------------------------------------------------------------------------------------------------------------------------------- 
def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

#---------------------------------------------------------------------------------------------------------------------------------------- 
# Round to nearest N.
#---------------------------------------------------------------------------------------------------------------------------------------- 
def roundX(x, base=10):
    return base * round(x/base)

#---------------------------------------------------------------------------------------------------------------------------------------- 
# Convert RGB to hex
#---------------------------------------------------------------------------------------------------------------------------------------- 
def rand_color_change(colorValue, randomizeMax):
    rand = int(random.random()*randomizeMax)
    sign = random.random()
    
    if (colorValue + rand) > 255:
        # Always subtract
        sign = 0

    if (colorValue - rand) < 0:
        # Always add
        sign = 1

    if sign < 0.5:
        # Subtract the random number
        rand = -rand   
    
    valueTemp = colorValue + rand

    # Rounding to avoid having too many colors in the palette.
    valueTemp = roundX(valueTemp, 5)
    
    if valueTemp < 0:
        valueTemp = 0

    if valueTemp > 255:
        valueTemp = 255

    return valueTemp

#----------------------------------------------------------------------------------------------------------------------------------------
# # Main processing routine.
#----------------------------------------------------------------------------------------------------------------------------------------

# Initiatlize variables and constants.
bubbleNum = 1
colorList = []
colorVariance = 10
sliceCount = 4

# Prompt for the SVG and original image files.
xmlin = get_svg_file()

if xmlin == "":
    messagebox.showinfo("Error", "No file selected. Program will now quit.")
    sys.exit()

imgin = get_image_file()

if imgin == "":
    messagebox.showinfo("Error", "No file selected. Program will now quit.")
    sys.exit()

# Set output files to write to the same folder.
filepath = os.path.dirname(xmlin)
if filepath[-1:] != "/":
    filepath += "/"

outFile = filepath + 'Bubbles.csv'
colorFile = filepath + 'Colors.csv'

out = open(outFile,'w') 
outColor = open(colorFile,'w') 

# Write header of the bubbles csv file.
outString = 'ID,X,Y,Size,Slice,Color ID,Slice Size'
out.write (outString)
out.write('\n')

# Write header of the color csv file.
outString = 'Color ID,Hex Color'
outColor.write (outString)
outColor.write('\n')

xmldoc = minidom.parse(xmlin)

# Open the image so we can get pixel colors
img = Image.open(imgin, 'r')
img = img.convert('RGB')
width = img.size[0] 
height = img.size[1]

# Loop through each line of the file and parse it into xml components
with open(xmlin) as f:
    lines = f.readlines()

for line in lines:

    if line[0:12]==' <use xlink:':
        # Break the string at the translate function.
        lTemp = line.split("translate(")

        # Break by commas to get the X coordinate.
        lTemp = lTemp[1].split(",")
        centerX = float(lTemp[0])

        # Break by ) to get the Y coordinate.
        lTemp = lTemp[1].split(") scale(")
        centerY = float(lTemp[0])

        # Break by ) to get the scale (radius).
        lTemp = lTemp[1].split(")")
        radius = float(lTemp[0])

        # Calculate area based on radius.
        area = math.pi*math.pow(radius,2)

        # Get the color of this point from the original file.
        RGB = img.getpixel((centerX, centerY))
        R = RGB[0]
        G = RGB[1]
        B = RGB[2]

        # Write colors for each of the pie slices, including the original
        hexColor = rgb_to_hex(RGB)

        # Is this color already in the list?
        try:
            ind = colorList.index(hexColor)
        except ValueError:
            colorList.append(hexColor)

        # Write the index to the file.
        sliceSize = random.random()
        ind = colorList.index(hexColor)
        outString = str(bubbleNum) + ',' + str(centerX) + ',' + str(centerY) + ',' + str(area) + ',A,' + str(ind) + ',' + str(sliceSize)
        out.write (outString)
        out.write('\n')

        # Write the rest of the slices
        for i in range(2, sliceCount+1):
            R1 = rand_color_change(R, colorVariance)
            G1 = rand_color_change(G, colorVariance)
            B1 = rand_color_change(B, colorVariance)

            RGBNew = (R1, G1, B1)
            hexColorNew = rgb_to_hex(RGBNew)

            # Is this color already in the list?
            try:
                ind = colorList.index(hexColorNew)
            except ValueError:
                colorList.append(hexColorNew)

            # Write the index to the file.
            sliceSize = random.random()
            ind = colorList.index(hexColorNew)

            outString = str(bubbleNum) + ',' + str(centerX) + ',' + str(centerY) + ',' + str(area) + ',' + chr(64+i) + ',' + str(ind) + ',' + str(sliceSize)
            out.write (outString)
            out.write('\n')

        bubbleNum += 1

out.close()
f.close

# Write the final color file.
ind = 0
for color in colorList:
    outString = str(ind) + ',<color>#' + color + '</color>'
    outColor.write (outString)
    outColor.write('\n')
    ind += 1

outColor.close()

messagebox.showinfo('Complete', 'Output files, bubbles.csv, slices, and colors.csv have been written to the following directory: ' + filepath)
