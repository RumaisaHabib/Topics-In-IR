from numpy import imag
from selenium import webdriver
import re
from urllib.parse import urlparse
import urllib.request, io
from urllib.error import HTTPError
from webdriver_manager.chrome import ChromeDriverManager
import os
import numpy as np
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pandas as pd
import time
import json
from colorama import Fore
from tqdm import tqdm
from PIL import Image
''' 
STEP ONE:
Scrape images from the URL
Sample usage:
python getsrc.py https://www.google.com (no slash at the end)

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
options.add_argument('--allow-file-access-from-file')
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
options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

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
# Make directory for this website, in case it doesn't exist. If this gives you a syntax error then reformat the website name.
try:
    os.system("mkdir -p " + host)
except:
    pass


driver.get(url)

# save source html
# html = driver.find_element(By.XPATH, '//*')
# html = html.get_attribute('innerHTML')

# html = driver.page_source
# time.sleep(20)



# Get all elements labelled 'img'
images = driver.find_elements(By.TAG_NAME, 'img')
image_srcs = [i.get_attribute('src') for i in images]


print("===== GETTING WEBPAGE SIZE =====")
total_bytes = []
for entry in tqdm(driver.get_log('performance'), bar_format=PROGRESS_BAR):
    if "Network.dataReceived" in str(entry):
        r = re.search(r'encodedDataLength\":(.*?),', str(entry))
        total_bytes.append(int(r.group(1)))
        kb = round((float(sum(total_bytes) / BYTE_SIZE)), 2)
print(kb, "KBs")
page_data["kiloBytesIn"] = kb

page_data["scrollHeight"] = driver.execute_script("return document.body.scrollHeight")
page_data["scrollWidth"] = driver.execute_script("return document.body.scrollWidth") 

num_img = 0
results = pd.DataFrame(columns=("Image Source", "Image Name", "Original Size (KB)", "New Size (KB)")).set_index("Image Name")
all_sources = []
print("===== SCRAPING IMAGES =====")
with open(host+"/images.txt", "w") as f:
    for i in tqdm(set(image_srcs), bar_format=PROGRESS_BAR):
        # i = image.get_attribute('src')
        if not i or i in all_sources:
            continue
        all_sources.append(i)
        try:
            # image_name = i.split("/")[-1]
            path,image_name=os.path.split(i)
            image_name = image_name.split("?")[0]
            if image_name[-3:] == "gif" or os.path.exists(host + "/" +image_name):
                continue
            # Write to images
            try:
                os.system("cd " + host + " && wget -q --show-progress " + i)
            except:
                continue
            f.write(i + "\n")
            path = urllib.request.urlopen(i)
            meta = path.info()
            # Image name for dataframe
            
            # Get original image size
            img_size = int(meta.get(name="Content-Length"))/BYTE_SIZE
            # Add data to results
            print(i)
            results.loc[image_name] = [i, img_size, "-"]
            num_img+=1
        except HTTPError as e:
            if e.code == 403:
                print(e)
                print("Cannot analyse this site. Aborting...")
                sys.exit()
        except Exception as e:
            print(e)
                
        # Writes image URL source to a file labelled images.txt in the host directory
page_data["numImages"] = num_img

# print("===== DOWNLOADING IMAGES =====")
# os.system("cd " + host + " && wget -q --show-progress -i images.txt")
results = results[~results.index.duplicated(keep='first')]

lines = open(host+'/images.txt', 'r').readlines()
lines_set = set(lines)
out  = open(host+'/images.txt', 'w')

for line in lines_set:
    out.write(line)

image_names = os.listdir(host)
for image in image_names:
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue
    if len(image.split("?"))>1:
        os.rename(host + "/" +image, host + "/" + image.split("?")[0])
        image = image.split("?")[0]
    new_image_name=image.split(".")[0] + ".webp"
    # format = Image.open(host + "/" +image).format
    # print("cd " + host + " && convert " +format + ":" + image +" -define webp:lossless=true " + new_image_name + " && rm " +image)
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    old_size = os.path.getsize(host + "/" + image)/1024
    new_size = os.path.getsize(host + "/" + new_image_name)/1024
    if (old_size < new_size):
        results.loc[image, "New Name"] = image
        results.loc[image, "New Size (KB)"] = old_size
        os.system("cd " + host + " && rm " + new_image_name )
        
    else:
        results.loc[image, "New Name"] = new_image_name
        results.loc[image, "New Size (KB)"] = new_size
        os.system("cd " + host + " && rm " +image )
    # results.loc[image, "New Size (KB)"] = os.stat(host + "/" + new_image_name).st_size/1024
# Dump outputs to physical memory
f = open(host+"/page_data.json", "w")
json.dump(page_data, f)
f.close()

results.dropna(axis=0,inplace=True)
results.to_csv(host+"/results.csv")
# os.system("cd " + host + " && python3 -m http.server 8000")

# html_file = os.getcwd() + "//" + host + "//source.html"
# driver.get("file:///" + html_file)
html = driver.execute_script("return document.body.innerHTML")
# html = driver.find_element_by_xpath("//*").get_attribute("outerHTML")
html = re.sub("src=\"//", "src=\"https://",html)
html = re.sub("src=\"/", "src=\""+ url + "/",html)
html = re.sub("src=\"portal/", "src=\"" + url + "/portal/",html)
html = re.sub("srcset=\"portal/", "srcset=\"" + url + "/portal/",html)
html = re.sub(", portal/", ", " + url + "/portal/",html)
f = open(host+"/source.html", "w")
f.write(html)
f.close()

driver.save_screenshot(host+"/original.png")
# # driver.save_screenshot(host+"/original.png")
driver.close()


print("===== GET SRC COMPLETE =====")
