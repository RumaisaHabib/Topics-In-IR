from urllib.parse import urlparse
import os
import sys
from selenium import webdriver
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import os
import sys
from tqdm import tqdm
from colorama import Fore
import pandas as pd
from PIL import Image
import time
import math


BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)
ERROR_MARGIN = 0.1 # 10%


url = sys.argv[1]

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
    
with open(host+"/source.html", "r", encoding='utf-8') as f:
    html= f.read()
    
def reduceQuality(size,final_size, orig, new):
    if (size<=final_size):
        return 100, False, size
    factor = 50
    min = 0
    max = 100
    isFactored = False
    old_size = size
    new_size = 0
    print("new image")
    while (factor>5):
        isFactored = True

        # image_rescaled = rescale(img, factor, anti_aliasing=False)
        # imsave(host + "/reduced_" + image, image_rescaled)
        os.system("convert " + host + "/" + orig + " -quality " + str(factor) + "% " + host + "/" + new)
        size = os.path.getsize(host + "/" + new)
        if (size == (final_size-(ERROR_MARGIN*final_size)) or size == ((ERROR_MARGIN*final_size)+final_size) or factor <= 5):
            break
        if old_size == new_size:
            break
        old_size = new_size
        new_size = size
        #print('factor {} image of size {}'.format(factor,size))
        print(size, factor)
        if(size > final_size):
            max = factor
        else:
            min = factor
        factor = round(((min+max)/2),4)

    return factor, isFactored, size

def try_webp_reduce(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    if (new_size <= final_size):
        # results.loc[image, "New Name"] = image
        # results.loc[image, "New Size (KB)"] = old_size
        # os.system("cd " + host + " && rm " + new_image_name )
        return new_size/1024, 100, False, False, True
        
    else:
        os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
        new_size = os.path.getsize(host + "/" + new_image_name)
        
        if(new_size <= final_size):
            return new_size/1024, 100, False, False, True
    return new_size/1024, 100, False, False, False


def reduce_to(image, final_size):
    final_size = final_size*1024
    print(image)
    
    # Get original size
    size = os.path.getsize(host + "/" + image)
    
    # Make new image (reduced)
    org_width, org_height = (Image.open(host + "/" + image)).size
    os.system("cp " + host + "/" + image + " " + host + "/reduced_" + image)
    
    # STEP 1: Reduce quality 
    factor, isFactored, size = reduceQuality(size, final_size, image, "reduced_" +image)

    print('factor {} image of size {}'.format(factor,size))
    
    # STEP 2: Change colors
    isBlack = False
    if(size>final_size):
        isBlack = True
        os.system("convert -colors 2 " + host + "/reduced_" + image + " " + host + "/reduced_" + image)
        size = os.path.getsize(host + "/reduced_" + image)
        print(size)
 
        
    os.system("cp " + host + "/reduced_" + image + " " + host + "/copy_reduced_" + image)
    _, _, size = reduceQuality(size, final_size, "copy_reduced_" + image, "reduced_" + image)
    os.system("rm " + host + "/copy_reduced_" + image)
    
    # STEP 3: Remove image
    isRemoved = False
    if(size>final_size):
        isRemoved = True

    if not isFactored:
        factor = 100
        
    end_size = os.path.getsize(host + "/reduced_" + image)
    if isRemoved:
        end_size = 0
    return end_size/1024, factor, isRemoved, isBlack
    
image_names = os.listdir(host)
results = pd.read_csv(host+"/results.csv").set_index("New Name")
results = results[~results.index.duplicated(keep='first')]

print("===== GENERATING NEW WEBPAGE =====")
for image in tqdm(image_names, bar_format=PROGRESS_BAR):
    try:
        if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
            continue
        if results.loc[image,"Reduction Factor"] == "-":
            continue
        target = results.loc[image,"Target Size of Image"]
        
        # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
        size, factor, removed, color, webpTrue = try_webp_reduce(image, target)
        if not webpTrue:
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"] = reduce_to(image,target)
            results.loc[image,"Removed"] = removed
        else:
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"],results.loc[image,"Color Depth Reduction"] = size, factor, color
            results.loc[image,"Removed"] = removed
            
        
        to_replace = results.loc[image,"Image Source"]
        if (removed):
            src_str = "src=\""+ to_replace + "\""
            replace_with = src_str + " style=\"display:none\""
            html = html.replace(src_str, "")
            print(replace_with)
            continue
            
        print(to_replace)
        replace_with = "https://localhost:4696/"+host+"/reduced_"+ image
        
        html = html.replace(to_replace, replace_with)
        print("replaced")
        sys.stdout.flush()
    except Exception as e:
        print("ERROR:",e)


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
driver.get(url)
driver.execute_script("document.body.innerHTML = arguments[0]", html)

# Manually remove srcset, forcing it use the image we give
images = driver.find_elements(By.TAG_NAME, 'img')
for element in images:
    driver.execute_script("arguments[0].removeAttribute('srcset')", element)
    
f = open(host+"/reduced.html", "w")
f.write(driver.page_source)
f.close()

time.sleep(10)
driver.save_screenshot(host+"/reduced.png")
driver.close()
results['Reduced Size of Image'] = results['Reduced Size of Image'].replace('', pd.NA).fillna(results['Target Size of Image'])
results["Error"] = results["Target Size of Image"] - results["Reduced Size of Image"]
results.to_csv(host+"/results.csv")
