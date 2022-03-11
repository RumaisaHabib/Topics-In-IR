from urllib.parse import urlparse
import os
import sys
from selenium import webdriver
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import sys
from tqdm import tqdm
import imageio as iio
import re
from colorama import Fore
import pandas as pd
from skimage.io import imread, imshow
from skimage.transform import rescale, resize, downscale_local_mean
from skimage.io import imsave
import PIL
import time
BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)



url = sys.argv[1]

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
    
with open(host+"/source.html", "r", encoding='utf-8') as f:
    html= f.read()
    
def reduce_to(image, final_size):
    final_size = final_size*1024
    print(image)
    # img = iio.imread(host + "/" + image)
    os.system("convert " + host + "/" + image + " -quality " + str(5) + "% " + host + "/reduced_"+ image)
    smallest_possible_size = os.path.getsize(host + "/reduced_" + image)
    
    size = os.path.getsize(host + "/" + image)
    factor = 99
    
    org_width, org_height = (PIL.Image.open(host + "/" + image)).size
    
    if (final_size>smallest_possible_size):
        while(size>final_size and factor>5):
            # image_rescaled = rescale(img, factor, anti_aliasing=False)
            # imsave(host + "/reduced_" + image, image_rescaled)
            os.system("convert " + host + "/" + image + " -quality " + str(factor) + "% " + host + "/reduced_"+ image)
            size = os.path.getsize(host + "/reduced_" + image)
            #print('factor {} image of size {}'.format(factor,size))
            factor = factor - 0.05
    print('factor {} image of size {}'.format(factor,size))
    
    scale = 90
    while(size>final_size):
        os.system("convert " + host + "/" + image + " -scale " + str(scale) + "% " + "-resize "+ str(org_width) + "x" + str(org_height) +" "+ host + "/reduced_"+ image)
        size = os.path.getsize(host + "/reduced_" + image)
        #print('scale {} image of size {}'.format(scale,size))
        scale = scale - scale*0.05

    end_size = os.path.getsize(host + "/reduced_" + image)
    print(end_size)
    
image_names = os.listdir(host)
results = pd.read_csv(host+"/results.csv").set_index("WebP Name")

print("===== GENERATING NEW WEBPAGE =====")
for image in tqdm(image_names, bar_format=PROGRESS_BAR):
    if image == "page_data.json" or image == "results.csv" or image == "images.txt" or image=="source.html" or image=="original.png":
        continue
    target = results.loc[image,"Target Size of Image"]
    # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
    reduce_to(image,target)
    to_replace = results.loc[image,"Image Source"]
    replace_with = "https://localhost:4696/"+host+"/reduced_"+ image
    html = html.replace(to_replace, replace_with)

# f = open(host+"/reduced.html", "w")
# f.write(html)
# f.close()


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


f = open(host+"/2.txt", "w")
f.write(driver.execute_script("return document.body.innerHTML"))
f.close()

driver.execute_script("document.body.innerHTML = arguments[0]", html)

f = open(host+"/reduced.html", "w")
f.write(driver.page_source)
f.close()

# html_file = os.getcwd() + "//" + host + "//reduced.html"
# driver.get("file:///" + html_file)
# html = re.sub("(<html[^<]+>)", "", html)
# html = html.replace("<html>", "")
# html = html.replace("</html>", "")
# driver.refresh()
time.sleep(10)
driver.save_screenshot(host+"/reduced.png")
driver.close()
