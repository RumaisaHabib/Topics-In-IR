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

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
    
image_names = os.listdir(host)
results = pd.read_csv(host+"/results.csv").set_index("Image Name")
for image in image_names:
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue