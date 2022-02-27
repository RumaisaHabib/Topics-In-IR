from selenium import webdriver
import re
from urllib.parse import urlparse
import urllib.request, io
import os
import sys
import json
import pandas as pd
from sympy import per

url = sys.argv[1]
goal = float(sys.argv[2]) # Target reduction in percentage e.g 0.5

if goal >= 1:
    print("Please enter a target percentage less than 1")
    print("Aborting...")
    sys.exit()

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
print("===== HOSTNAME =====")
print(host)

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