from numpy import imag
from selenium import webdriver
import re
from urllib.parse import urlparse
import urllib.request, io
from urllib.error import HTTPError
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import pandas as pd
import json
from colorama import Fore
from tqdm import tqdm
''' 
STEP ONE:
Scrape images from the URL
Sample usage:
python getsrc.py https://google.com/

'''
page_data = {}

BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)
# Set options for web scraper
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

# Performance metrics setup for websize 
logging_prefs = {'performance' : 'INFO'}    
caps = webdriver.DesiredCapabilities.CHROME.copy()
caps['goog:loggingPrefs'] = logging_prefs

# Mobile emulation, currently configured for Nexus 5
mobile_emulation = {
        "deviceMetrics": { "width": PHONE_WIDTH, "height": PHONE_HEIGHT, "pixelRatio": PIXEL_RATIO},
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
options.add_experimental_option("mobileEmulation", mobile_emulation)

# Chrome web driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options,desired_capabilities=caps)


# URL settings, to be replaced with text file of URLs (possible)
url = sys.argv[1]

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
print("===== HOSTNAME =====")
page_data["host"] = host
print(host)

driver.get(url)

# Get all elements labelled 'img'
images = driver.find_elements(By.TAG_NAME, 'img')

print("===== GETTING WEBPAGE SIZE =====")
total_bytes = []
for entry in tqdm(driver.get_log('performance'), bar_format=PROGRESS_BAR):
    if "Network.dataReceived" in str(entry):
        r = re.search(r'encodedDataLength\":(.*?),', str(entry))
        total_bytes.append(int(r.group(1)))
        kb = round((float(sum(total_bytes) / BYTE_SIZE)), 2)
print(kb, "KBs")
page_data["kiloBytesIn"] = kb

# Make directory for this website, in case it doesn't exist. If this gives you a syntax error then reformat the website name.
try:
    os.system("mkdir -p " + host)
except:
    pass

num_img = 0
results = pd.DataFrame(columns=("Image Source", "Image Name", "Original Size (KB)"))
print("===== SCRAPING IMAGES =====")
with open(host+"/images.txt", "w") as f:
    for image in tqdm(images, bar_format=PROGRESS_BAR):
        i = image.get_attribute('src')
        try:
            # Write to images
            f.write(i + "\n")
            path = urllib.request.urlopen(i)
            meta = path.info()
            # Image name for dataframe
            image_name = i.split("/")[-1]
            # Get original image size
            img_size = int(meta.get(name="Content-Length"))/BYTE_SIZE
            # Add data to results
            results.loc[num_img] = [i, image_name, img_size]
            num_img+=1
        except HTTPError as e:
            if e.code == 403:
                print(e)
                print("Cannot analyse this site. Aborting...")
                sys.exit()
        except Exception as e:
            pass
                
        # Writes image URL source to a file labelled images.txt in the host directory
page_data["numImages"] = num_img

'''
TO DO:
- Use wget to download all images from the images.txt file into the directory of the host
- Possible command (for linux):
'''
print("===== DOWNLOADING IMAGES =====")
os.system("cd " + host + " && wget -q --show-progress -i images.txt")

image_names = os.listdir(host)
for image in image_names:
    if image == "page_data.json" or image == "results.csv" or image == "images.txt":
        continue
    os.system("cd " + host + " && magick " +image +" -define webp:lossless=true " + image.split(".")[0] + ".webp && rm " +image)


# Dump outputs to physical memory
f = open(host+"/page_data.json", "w")
json.dump(page_data, f)
f.close()

results.to_csv(host+"/results.csv")

driver.close()

print("===== GET SRC COMPLETE =====")