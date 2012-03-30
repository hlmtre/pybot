'''
ASCII Art maker
Creates an ascii art image from an arbitrary image
Created on 7 Sep 2009

@author: Steven Kay
'''

from PIL import Image
import random
from bisect import bisect
import urllib
import datetime
import string
import os

# greyscale.. the following strings represent
# 7 tonal ranges, from lighter to darker.
# for a given pixel tonal level, choose a character
# at random from that range.

greyscale = [
            " ",
            " ",
            ".,-",
            "_ivc=!/|\\~",
            "gjez]/(YL)t[+TVf",
            "mdKZGbNDXYP*Q",
            "WKMA",
            "#%$"
            ]
			
			
irccolors = [
			(204, 204, 204),
			(0, 0, 0),
			(54, 54, 178),
			(42, 140, 42),
			(195, 59, 59),
			(199, 50, 50),
			(128, 37, 127),
			(102, 54, 31),
			(217, 166, 65),
			(61, 204, 61),
			(26, 85, 85),
			(47, 140, 116),
			(69, 69, 230),
			(176, 55, 176),
			(76, 76, 76),
			(149, 149, 149)
			]
			
			

# using the bisect class to put luminosity values
# in various ranges.
# these are the luminosity cut-off points for each
# of the 7 tonal levels. At the moment, these are 7 bands
# of even width, but they could be changed to boost
# contrast or change gamma, for example.

zonebounds=[36,72,108,144,180,216,252]

# open image and resize
# experiment with aspect ratios according to font

def colorDistance(c1, c2):
	return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])

def sanitize(filename):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	return ''.join(c for c in filename if c in valid_chars)

def rainbow():
	s = ""
	for x in range(0, 16):
		s += setcolor(0, x)
		s += " "
	s += clearcolor()
	return s
		
	
def setcolor(fg, bg):
	return "\x03" + str(fg) + "," + str(bg)
	
def clearcolor():
	return "\x03"
	
def getlum(pixel):
	return 255 - int((pixel[0] + pixel[1] + pixel[2]) * 1.0 / 3)
	
def findcolor(pixel):
	global irccolors
	for x in range(0, len(irccolors)):
		col = irccolors[x]
		if colorDistance(col, pixel) < 70:
			if getlum(pixel) > getlum(col):
				return setcolor(1, x)
			else:
				return setcolor(0, x)
	return ""
	
def asciify(url):
	print "asciifying..."
	downloader = urllib.URLopener()
	time = str(datetime.datetime.now())
	filename = sanitize(time + url)
	path = "./" + filename
	print "path: " + path
	downloader.retrieve(url, path)
	print "downloaded"
	im=Image.open(path)
	print "opened"
	ratio = im.size[0] * 2.4 / im.size[1]
	width = int(ratio * 10)
	im = im.resize((width, 10), Image.BILINEAR)
	#im = im.convert("L") # convert to mono

	# now, work our way over the pixels
	# build up str

	arr = []
	
	line = "+"
	for x in range(0,im.size[0]):
		line = line + "-"
	line = line + "+"
	arr.append(line)
	
	for y in range(0,im.size[1]):
		line = "|"
		for x in range(0,im.size[0]):
			pixel = im.getpixel((x,y))
			lum = getlum(pixel)
			row = bisect(zonebounds,lum)
			possibles = greyscale[row]
			line = line + findcolor(pixel)
			line = line + possibles[random.randint(0, len(possibles) - 1)]
			line = line + clearcolor()
		line = line + "|"
		arr.append(line)
	
	line = "+"
	for x in range(0,im.size[0]):
		line = line + "-"
	line = line + "+"
	arr.append(line)
	
	os.remove(path)

	return arr
