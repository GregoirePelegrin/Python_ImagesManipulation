# Add prints during execution

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io
import argparse
import matplotlib.pyplot as plt
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-s", "--nbSegments", required = True, help = "Nbr of areas to split the image")
args = vars(ap.parse_args())

image = img_as_float(io.imread(args["image"]))

print("Doing SLIC")
numSegments = int(args["nbSegments"])
segments = slic(image, start_label = 1, n_segments = numSegments, sigma = 5)
print("SLIC done")
rectedImage = np.zeros(image.shape, dtype=float)

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

rectList = []
for _xs,_ys,red,green,blue in zip(xs, ys,meanReds,meanGreens,meanBlues):
	if(len(_xs) != 0 and len(_ys) != 0):
		minX = _xs[0]
		minY = _ys[0]
		maxX = _xs[0]
		maxY = _ys[0]
	for x,y in zip(_xs,_ys):
		if(len(_xs) != 0 and len(_ys) != 0):
			if x < minX:
				minX = x
			elif x > maxX:
				maxX = x
			if y < minY:
				minY = y
			elif y > maxY:
				maxY = y
		rectList.append((minX, maxX, minY, maxY, red, green, blue))

def insertion(list1, list2):
	for i in range(len(list2)):
		element1 = list2[i]
		element2 = list1[i]
		j = i
		while j>0 and list2[j-1]>element1:
			list2[j] = list2[j-1]
			list1[j] = list1[j-1]
			j -= 1
		list2[j] = element1
		list1[j] = element2

# Sorting rectList
def sorting(inputList):
	calcList = []
	for rect in inputList:
		calcList.append(rect[1]-rect[0] * rect[3]-rect[2])
	# Tri non récursif
	insertion(inputList, calcList)

sorting(rectList)

# Display rectList
for rect in rectList:
	for x in range(rect[0], rect[1] + 1):
		for y in range(rect[2], rect[3] + 1):
			rectedImage[x][y][0] = rect[4]
			rectedImage[x][y][1] = rect[5]
			rectedImage[x][y][2] = rect[6]

print("Display Image")
fig = plt.figure("Sorted RectedImage -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(rectedImage)
plt.axis("off")
plt.show()