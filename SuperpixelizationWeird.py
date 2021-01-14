from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from datetime import datetime
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.util import img_as_float
from skimage import io
from tqdm import tqdm
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required = True, help = "Path to the image")
ap.add_argument("-s", "--nbSegments", required = True, help = "Nbr of areas to split the image")
args = vars(ap.parse_args())

image = img_as_float(io.imread(args["image"]))

numSegments = int(args["nbSegments"])
segments = slic(image, start_label = 1, n_segments = numSegments, sigma = 5)
print("SLIC done")
segmentedImage = np.zeros(image.shape, dtype = float)
reds, greens, blues, labels, xss, yss = [], [], [], [], [], []
# Loop through all possible values for segments[x][y] (0->numSegments)
for progress,label in zip(tqdm(range(numSegments), desc="Progress", ascii=True, ncols=125),range(numSegments)):
	# For each value, get the xs and ys for the correspondant area
	xs = []
	ys = []
	labels.append(label)
	for x in range(len(segments)):
		for y in range(len(segments[x])):
			if segments[x][y] == label:
				xs.append(x)
				ys.append(y)
	if(len(xs) == 0 or len(ys) == 0):
		continue
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
	reds.append(red)
	greens.append(green)
	blues.append(blue)

# Modify new image
for xs,ys,label in zip(xss,yss,labels):
	for x, y in zip(xs, ys):
		segmentedImage[x][y][0] = reds[label]
		segmentedImage[x][y][1] = green[label]
		segmentedImage[x][y][2] = blue[label]

name = "OutputImage\\Superpixelize"
date = datetime.now()
fig = plt.figure("Superpixels -- {} segments".format(numSegments))
ax = fig.add_subplot(1, 1, 1)
ax.imshow(segmentedImage)
plt.axis("off")
nameSave = "{}--Superpixeled_{}-{}_{}_{}-{}_{}_{}.png".format(name, numSegments,
	date.day, date.month, date.year, date.second, date.minute, date.hour)
plt.savefig(nameSave)
plt.show()