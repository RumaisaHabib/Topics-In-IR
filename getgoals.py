import re
from urllib.parse import urlparse
import urllib.request, io
import os
import sys
import json
import pandas as pd
from sympy import per

url = sys.argv[1]
goal = float(sys.argv[2]) # Target size e.g 0.5

if goal >= 1 or goal <= 0:
    print("Please enter a target percentage less than 1 and greater than 0")
    print("Aborting...")
    sys.exit()

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])


f = open(host+'/page_data.json') 
page_data = json.load(f)

results = pd.read_csv(host+"/results.csv")

page_size = page_data['kiloBytesIn']
total_image_size = results["Original Size (KB)"].sum()
percent_img = total_image_size/page_size*100
print("===== INFO =====")
print("Page size:", page_size, "KBs")
print("Image content total size:",round(total_image_size,2), "KBs")
print("Image content makes up", round(percent_img,2), "% of total page bytes")
if percent_img/100 < (1-goal):
    print("Cannot reduce to this size with images alone. Please choose a higher target.")
    print("Aborting...")
    sys.exit()
target_img_bytes = total_image_size- ((1-goal)*page_size)
print("Target total image size", round(target_img_bytes,2),"KBs")

results["Target Size of Image"] = results["Reduction Factor"] * target_img_bytes


# for i in list(results["WebP Size (KB)"]):
#     results.loc[results["Target Size of Image"] > i, "Target Size of Image"] = i
prunedsize = 0 
newtotalvals = 0
prunedindices = []
for index, row in results.iterrows():
    if row["WebP Size (KB)"] < row["Target Size of Image"]:
        results.loc[index, "Target Size of Image"] = row["WebP Size (KB)"]
        results.loc[index,"Reduction Factor"] = "-"
        prunedsize += row["WebP Size (KB)"]
        prunedindices.append(index)
        
target_img_bytes = target_img_bytes - prunedsize

for index, row in results.iterrows():
    if index not in prunedindices:
        newtotalvals += results.loc[index,"Image Value"]

for index, row in results.iterrows():
    if index not in prunedindices:
        results.loc[index,"Reduction Factor"] = results.loc[index,"Image Value"]/newtotalvals
        results.loc[index, "Target Size of Image"] = results.loc[index,"Reduction Factor"] * target_img_bytes


# RE CALC REDUCTION FACTOR !!!!!
        # row["Target Size of Image"] = 
# results.loc[]
results.to_csv(host+"/results.csv", index=False)
#print(results["Target Size of Image"][0], )
# lastCol = pd.read_csv(gost+"/results.csv", usecols[-1])
print("===== TARGETS CALCULATED =====")