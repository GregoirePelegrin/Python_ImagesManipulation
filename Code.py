from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from datetime import datetime
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-s", "--nbSegments", required = True, help = "Nbr of areas to split the image")
args = vars(ap.parse_args())

image = img_as_float(io.imread(args["image"]))

print("Doing SLIC")
numSegments = int(args["nbSegments"])
segments = slic(image, start_label = 1, n_segments = numSegments, sigma = 5)
print("SLIC done")
segmentedImage = np.zeros(image.shape, dtype = float)
rectedImage = np.zeros(image.shape, dtype=float)

# Form xs, ys, reds, greens, blues lists
xs = []
ys = []
reds = []
greens = []
blues = []
for i in range(numSegments):
	xs.append([])
	ys.append([])
	reds.append([])
	greens.append([])
	blues.append([])
for x in range(image.shape[0]):
	for y in range(image.shape[1]):
		xs[segments[x][y]].append(x)
		ys[segments[x][y]].append(y)
		reds[segments[x][y]].append(image[x][y][0])
		greens[segments[x][y]].append(image[x][y][1])
		blues[segments[x][y]].append(image[x][y][2])
	if x % (int(image.shape[0]/100)) == 0:
		print("[Step 1-Lists Creation]: {0:.1f}%".format(x / image.shape[0] * 100))
print("[Step 1]: 100% Complete")

# Form meanReds, meanGreens, meanBlues lists
meanReds = []
meanGreens = []
meanBlues = []
for _reds,_greens,_blues in zip(reds,greens,blues):
	red = 0
	green = 0
	blue = 0
	for _red,_green,_blue in zip(_reds,_greens,_blues):
		red += _red
		green += _green
		blue += _blue
	if len(_reds) == 0:
		meanReds.append(0)
	else:
		meanReds.append(red / len(_reds))
	if len(_greens) == 0:
		meanGreens.append(0)
	else:
		meanGreens.append(green / len(_greens))
	if len(_blues) == 0:
		meanBlues.append(0)
	else:
		meanBlues.append(blue / len(_blues))

# Modify new images
i = 0
for _xs,_ys,red,green,blue in zip(xs, ys,meanReds,meanGreens,meanBlues):
	if(len(_xs) != 0 and len(_ys) != 0):
		minX = _xs[0]
		minY = _ys[0]
		maxX = _xs[0]
		maxY = _ys[0]
	for x,y in zip(_xs,_ys):
		segmentedImage[x][y][0] = red
		segmentedImage[x][y][1] = green
		segmentedImage[x][y][2] = blue

		if(len(_xs) != 0 and len(_ys) != 0):
			if x < minX:
				minX = x
			elif x > maxX:
				maxX = x
			if y < minY:
				minY = y
			elif y > maxY:
				maxY = y
	if(len(_xs) != 0 and len(_ys) != 0):
		for x in range(minX, maxX+1):
			for y in range(minY, maxY+1):
				rectedImage[x][y][0] = red
				rectedImage[x][y][1] = green
				rectedImage[x][y][2] = blue
	if i % (int(len(xs)/100)) == 0:		# [100] must be < to numSegments
		print("[Step 2-Image Modification]: {}%".format(i / len(xs) * 100))
	i += 1
print("[Step 2]: 100% Complete")

name = "OutputImage\\Optimized_Image"
date = datetime.now()
print("Display Images")
fig = plt.figure("Optimized Superpixels -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(segmentedImage)
plt.axis("off")
nameSave = "{}--Superpixels_{}-{}_{}_{}-{}_{}_{}.png".format(name, numSegments,
	date.day, date.month, date.year, date.second, date.minute, date.hour)
plt.savefig(nameSave)
fig = plt.figure("Optimized RectedImage -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(rectedImage)
plt.axis("off")
nameSave = "{}--Rected_{}-{}_{}_{}-{}_{}_{}.png".format(name, numSegments,
	date.day, date.month, date.year, date.second, date.minute, date.hour)
plt.savefig(nameSave)
plt.show()