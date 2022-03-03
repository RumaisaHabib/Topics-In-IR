import PIL.Image
from urllib.parse import urlparse
import os
import sys
from jinja2 import pass_environment
import numpy as np
from numpy import imag
from selenium import webdriver
import re
from urllib.parse import urlparse
import urllib.request, io
from urllib.error import HTTPError
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
from tqdm import tqdm
from colorama import Fore
from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2
import argparse
import pandas as pd
import json
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)

url = sys.argv[1]


# results = pd.DataFrame(columns=("SSIM Value", "Area/1000", "Value"))
qualities = [25, 50, 75]
listOfReducedImages = []
originalImages = []
ssimVals = []
areaVals = []
imageVals = []
reductionFactor = []
# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])

f = open(host+'/page_data.json') 
page_data = json.load(f)
scrollArea = page_data["scrollHeight"] * page_data["scrollWidth"]

image_names = os.listdir(host)

for image in image_names:
    # os.system("cd " + host)
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue
    for i in qualities:
        # os.system("magick " +image +" -define webp:lossless=true " + image.split(".")[0] + ".webp && rm " +image)
        os.system("cd " + host + "&& convert " + image + " -quality " + str(i) + "% " + str(i)+"_"+image)
        listOfReducedImages.append(str(i)+"_"+image)
    originalImages.append(image)

# def options():
#  parser = argparse.ArgumentParser(description="Read image metadata")
#  parser.add_argument("-o", "--first", help="Input image file.", required=True)
#  parser.add_argument("-c", "--second", help="Input image file.", required=True)
#  args = parser.parse_args()
#  return args

def mse(imageA, imageB):
 # the 'Mean Squared Error' between the two images is the sum of the squared difference between the two images
 mse_error = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
 mse_error /= float(imageA.shape[0] * imageA.shape[1])
	
 # return the MSE. The lower the error, the more "similar" the two images are.
 return mse_error

def compare(imageA, imageB):
 # Calculate the MSE and SSIM
 m = mse(imageA, imageB)
 s = ssim(imageA, imageB)

 # Return the SSIM. The higher the value, the more "similar" the two images are.
 return s


def findSSIM(first, second):

    # Import images
    image1 = cv2.imread(first)
    image2 = cv2.imread(second, 1)

    # Convert the images to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Check for same size and ratio and report accordingly
    ho, wo, _ = image1.shape
    hc, wc, _ = image2.shape
    ratio_orig = ho/wo
    ratio_comp = hc/wc
    dim = (wc, hc)

    if round(ratio_orig, 2) != round(ratio_comp, 2):
        print("\nImages not of the same dimension. Check input.")
        exit()

    # Resize first image if the second image is smaller
    elif ho > hc and wo > wc:
        print("\nResizing original image for analysis...")
        gray1 = cv2.resize(gray1, dim)

    elif ho < hc and wo < wc:
        print("\nCompressed image has a larger dimension than the original. Check input.")
        exit()

    if round(ratio_orig, 2) == round(ratio_comp, 2):
        mse_value = mse(gray1, gray2)
        ssim_value = compare(gray1, gray2)
        # print("MSE:", mse_value)
        # print("SSIM:", ssim_value)
        return mse_value, ssim_value


print("===== CALCULATING VALUES =====")
imageNum = 0
results = pd.read_csv(host+"/results.csv").set_index("WebP Name")
results["1/SSIM Value"] = np.nan
results["Area/1000"] = np.nan
results["Normalized Area"] = np.nan
results["Image Value"] = np.nan

for original in tqdm(originalImages, bar_format=PROGRESS_BAR):
    sumSSIM = 0;
    originalPath = "./"+host+"/"+original
    for i in qualities:
        # print("ORGINAL AND " + str(i))
        
        reducedPath = "./"+host+"/"+listOfReducedImages[0]

        originalPath = "./"+host+"/"+original
        # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        mseval, ssimval = findSSIM(originalPath, reducedPath)
        sumSSIM = sumSSIM + ssimval
        # os.system("cd "+host+"&& identify -format " + "\"Pixel Size: %w x %h\n\"" + original)
        # os.system("cd "+host+"&& identify -format " + "\"Pixel Size: %w x %h\n\"" + listOfReducedImages[0])
        # originalImage = PIL.Image.open(originalPath)
        # reducedImage = PIL.Image.open(reducedPath)
        # print("original size: ", type(originalImage.size), "reduced size: ", reducedImage.size)
        os.system("cd " + host + "&& rm " + listOfReducedImages[0])
        listOfReducedImages.pop(0)
    area = int((PIL.Image.open(originalPath)).size[0]) * int((PIL.Image.open(originalPath)).size[1])
    results.loc[original, "1/SSIM Value"] = 1/(sumSSIM/len(qualities))
    results.loc[original, "Area/1000"] = area/1000
    results.loc[original, "Normalized Area"] = area/scrollArea
    results.loc[original, "Image Value"] = (1/(sumSSIM/len(qualities)))+ area/scrollArea
    # results.loc[imageNum] = [ssimVals[-1], areaVals[-1], imageVals[-1]]
    imageNum = imageNum + 1


total = results["Image Value"].sum()
results["Reduction Factor"] = results["Image Value"]/total
results.to_csv(host+"/results.csv")


print("===== GET VALUES COMPLETE =====")
