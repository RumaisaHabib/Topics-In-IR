from shutil import register_unpack_format
import PIL.Image
from urllib.parse import urlparse
import os
import sys
import numpy as np
from urllib.parse import urlparse
import os
import sys
from tqdm import tqdm
from colorama import Fore
from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2
import pandas as pd
import json
import VCPR
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)

url = sys.argv[1]
a = float(sys.argv[2]) #IAS
b = float(sys.argv[3]) #Area
c = float(sys.argv[4]) #Location
d = float(sys.argv[5]) #OG Size


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
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue
    for i in qualities:
        os.system("cd " + host + "&& convert " + image + " -quality " + str(i) + "% " + str(i)+"_"+image)
        listOfReducedImages.append(str(i)+"_"+image)
    originalImages.append(image)


print("===== CALCULATING VALUES =====")
imageNum = 0
results = pd.read_csv(host+"/results.csv").set_index("New Name")
results["IAS"] = np.nan
results["Area/1000"] = np.nan
results["Normalized Area"] = np.nan
results["Image Value"] = np.nan

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
    results.loc[original, "IAS"] = 1- (sumSSIM/len(qualities))
    results.loc[original, "Area/1000"] = area/1000
    results.loc[original, "Normalized Area"] = area/scrollArea
    imageNum = imageNum + 1

results["Image Value"] = a*results["IAS"] + b*results["Normalized Area"] + c*(1-results["Location"]) + d*results["New Size (KB)"]
total = results["Image Value"].sum()
results["Reduction Factor"] = results["Image Value"]/total
results.to_csv(host+"/results.csv")


print("===== GET VALUES COMPLETE =====")
