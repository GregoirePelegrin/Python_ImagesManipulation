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

numSegments = int(args["nbSegments"])
segments = slic(image, start_label = 1, n_segments = numSegments, sigma = 5)
print("SLIC done")
segmentedImage = np.zeros(image.shape, dtype = float)
rectedImage = np.zeros(image.shape, dtype=float)
# Loop through all possible values for segments[x][y] (0->numSegments)
for label in range(numSegments):
	# For each value, get the xs and ys for the correspondant area
	xs = []
	ys = []
	for x in range(len(segments)):
		for y in range(len(segments[x])):
			if segments[x][y] == label:
				xs.append(x)
				ys.append(y)
	if(len(xs) == 0 or len(ys) == 0):
		if label % 10 == 0:
			print("{}/{}".format(label, numSegments))
		continue
	# 1/ Areas with same color
	# Get the mean values for red, green and blue in the image for these xs and ys (values between 0 and 1)
	red = 0
	green = 0
	blue = 0
	for x,y in zip(xs,ys):
		red += image[x][y][0]
		green += image[x][y][1]
		blue += image[x][y][2]
	red /= len(xs)
	green /= len(xs)
	blue /= len(xs)
	# Modify new image
	for x,y in zip(xs,ys):
		segmentedImage[x][y][0] = red
		segmentedImage[x][y][1] = green
		segmentedImage[x][y][2] = blue
	# 2/ Big squares instead of wobbly shapes
	# May be necessary to plot the bigger squares first with an external list and plotting outside the for loop
	# Pay attention to the fact that in this case, i'd need a list for the colors to be displayed
	minX = xs[0]
	minY = ys[0]
	maxX = xs[0]
	maxY = ys[0]
	for x,y in zip(xs,ys):
		if x < minX:
			minX = x
		elif x > maxX:
			maxX = x
		if y < minY:
			minY = y
		elif y > maxY:
			maxY = y
	for x in range(minX, maxX+1):
		for y in range(minY, maxY+1):
			rectedImage[x][y][0] = red
			rectedImage[x][y][1] = green
			rectedImage[x][y][2] = blue
	# Display the progress
	if label % 10 == 0:
		print("{}/{}".format(label, numSegments))

fig = plt.figure("Superpixels -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(segmentedImage)
plt.axis("off")
fig = plt.figure("RectedImage -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(rectedImage)
plt.axis("off")
plt.show()