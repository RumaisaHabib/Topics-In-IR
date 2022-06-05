from shutil import register_unpack_format
import PIL.Image
from pickletools import optimize
from urllib.parse import urlparse
import os
import sys
from tqdm import tqdm
from colorama import Fore
import pandas as pd
from PIL import Image
import time
import VCPR
import math
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)

host = sys.argv[1]
# target is target in image bytes reduction percentage
target_img_perc= float(sys.argv[2])
scrollArea = int(sys.argv[3])
result_array = []
# Get image names from local directory
image_names = os.listdir(host)
# Files to ignore in this step
ignore = ["page_data.json", "results.csv", "images.txt" , "source.html" , "original.png"]
for image in image_names:
    if image in ignore:
        continue
    if len(image.split("?"))>1:
        # To keep file names short, remove the query from the image names
        os.rename(host + "/" +image, host + "/" + image.split("?")[0])
        image = image.split("?")[0]
        
    old_size = os.path.getsize(host + "/" + image)/1024
    if "svg" in image: # Try converting svg to webp
        new_image_name=image.split(".")[0] + ".webp"

        os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
        new_size = os.path.getsize(host + "/" + new_image_name)/1024
        if (old_size < new_size):
            result_array.append([image, old_size, old_size])
            # results.loc[image, "New Name"] = image
            # results.loc[image, "New Size (KB)"] = old_size
            os.system("cd " + host + " && rm " + new_image_name )
            
        else:
            result_array.append([new_image_name, old_size, new_size])
            # results.loc[image, "New Name"] = new_image_name
            # results.loc[image, "New Size (KB)"] = new_size
            os.system("cd " + host + " && rm " +image )
    else:
        result_array.append([image, old_size, old_size])
        # results.loc[image, "New Name"] = image
        # results.loc[image, "New Size (KB)"] = old_size
results = pd.DataFrame(result_array, columns=["New Name", "Original Size (KB)", "New Size (KB)"]).set_index("New Name")
results.dropna(axis=0,inplace=True)
results.to_csv(host+"/results.csv")


qualities = [25, 50, 75]
listOfReducedImages = []
originalImages = []
ssimVals = []
areaVals = []
imageVals = []
reductionFactor = []

for image in image_names:
    # os.system("cd " + host)
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue
    for i in qualities:
        # os.system("magick " +image +" -define webp:lossless=true " + image.split(".")[0] + ".webp && rm " +image)
        os.system("cd " + host + "&& convert " + image + " -quality " + str(i) + "% " + str(i)+"_"+image)
        listOfReducedImages.append(str(i)+"_"+image)
    originalImages.append(image)


print("===== CALCULATING VALUES =====")
results = pd.read_csv(host+"/results.csv").set_index("New Name")

for original in tqdm(originalImages, bar_format=PROGRESS_BAR):
    sumSSIM = 0
    originalPath = "./"+host+"/"+original
    for i in qualities:
        reducedPath = "./"+host+"/"+listOfReducedImages[0]

        originalPath = "./"+host+"/"+original
        mseval, ssimval = VCPR.findSSIM(originalPath, reducedPath)
        sumSSIM = sumSSIM + ssimval
        os.system("cd " + host + "&& rm " + listOfReducedImages[0])
        listOfReducedImages.pop(0)
    area = int((PIL.Image.open(originalPath)).size[0]) * int((PIL.Image.open(originalPath)).size[1])
    # results.loc[original, "IAS"] = 1/(sumSSIM/len(qualities))
    results.loc[original, "IAS"] = 1- (sumSSIM/len(qualities))
    results.loc[original, "Normalized Area"] = area/scrollArea

results["Image Value"] = results["IAS"] + results["Normalized Area"] + results["New Size (KB)"]/10
total = results["Image Value"].sum()
results["Reduction Factor"] = results["Image Value"]/total
results.to_csv(host+"/results.csv")


print("===== GET VALUES COMPLETE =====")
target_img_bytes = sum(results["Original Size (KB)"]) * target_img_perc
results["Target Size of Image"] = results["Reduction Factor"] * target_img_bytes

prunedsize = 0 
newtotalvals = 0
prunedindices = []
for index, row in results.iterrows():
    if row["New Size (KB)"] < row["Target Size of Image"]:
        results.loc[index, "Target Size of Image"] = row["New Size (KB)"]
        results.loc[index,"Reduction Factor"] = "-"
        prunedsize += row["New Size (KB)"]
        prunedindices.append(index)
        
target_img_bytes = target_img_bytes - prunedsize

for index, row in results.iterrows():
    if index not in prunedindices:
        newtotalvals += results.loc[index,"Image Value"]

for index, row in results.iterrows():
    if index not in prunedindices:
        results.loc[index,"Reduction Factor"] = results.loc[index,"Image Value"]/newtotalvals
        results.loc[index, "Target Size of Image"] = results.loc[index,"Reduction Factor"] * target_img_bytes

print("===== TARGETS CALCULATED =====")

image_names = os.listdir(host)

for image in tqdm(image_names, bar_format=PROGRESS_BAR):
    try:
        if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
            continue
        if results.loc[image,"Reduction Factor"] == "-":
            continue
        target = results.loc[image,"Target Size of Image"]
        target = target*BYTE_SIZE
        
        size, factor, removed, color, webpTrue, webp_image, encoding_quality = VCPR.try_webp_reduce(image, target, host)
        if not webpTrue:

            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"], _ = VCPR.reduce_to(image,target, host)
            results.loc[image, "WEBP"] = False
            results.loc[image,"Removed"] = removed
            result = image
        else:
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"],results.loc[image,"Color Depth Reduction"], results.loc[image, "WEBP"] = size, factor, color, True
            results.loc[image,"Removed"] = removed
            results.loc[image,"WEBP Encoding Quality"] = encoding_quality
            result = webp_image
    except Exception as e:
        print("ERROR:",e)
            
results['Reduced Size of Image'] = results['Reduced Size of Image'].replace('', pd.NA).fillna(results['Target Size of Image'])
results["Error"] = results["Target Size of Image"] - results["Reduced Size of Image"]
results.to_csv(host+"/results.csv")