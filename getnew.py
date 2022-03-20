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
ERROR_MARGIN = 0.01 # 1%


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
    factor = 50
    isFactored = False
    while (size>final_size and factor>5):
        isFactored = True

        # image_rescaled = rescale(img, factor, anti_aliasing=False)
        # imsave(host + "/reduced_" + image, image_rescaled)
        os.system("convert " + host + "/" + orig + " -quality " + str(factor) + "% " + host + "/" + new)
        size = os.path.getsize(host + "/" + new)
        if (size == ((ERROR_MARGIN*final_size)-final_size) or size == ((ERROR_MARGIN*final_size)+final_size) or factor <= 5):
            break
        #print('factor {} image of size {}'.format(factor,size))
        if(size > final_size):
            factor = math.floor(factor / 2)
        else:
            factor = math.floor(0.75*2*factor)
    return factor, isFactored, size

def reduce_to(image, final_size):
    final_size = final_size*1024
    print(image)
    # img = iio.imread(host + "/" + image)
    # os.system("convert " + host + "/" + image + " -quality " + str(5) + "% " + host + "/reduced_"+ image)
    # smallest_possible_size = os.path.getsize(host + "/reduced_" + image)
    
    # Get original size
    size = os.path.getsize(host + "/" + image)
    
    # Make new image (reduced)
    org_width, org_height = (Image.open(host + "/" + image)).size
    os.system("cp " + host + "/" + image + " " + host + "/reduced_" + image)
    
    # STEP 1: Reduce quality 
    factor, isFactored, size = reduceQuality(size, final_size, image, "reduced_"+image)

    print('factor {} image of size {}'.format(factor,size))
    
    # STEP 2: Change colors
    isBlack = False
    if(size>final_size):
        isBlack = True
        # img = PIL.Image.open("./" + host + "/reduced_" + image)
        # info = img.info
        # img1 = img.convert("RGBA").convert("L")
        # img1.show()
        # img1.save("./" + host + "/reduced_" + image, **info)
        # os.system("convert " + host + "/reduced_" + image +  " -set colorspace Gray -separate -average " + host + "/reduced_" + image)
        # os.system("convert -colors " + str(colors)  + " " + host + "/reduced_" + image + " " + host + "/reduced_" + image)
        os.system("convert -colors 2 " + host + "/reduced_" + image + " " + host + "/reduced_" + image)
        
        size = os.path.getsize(host + "/reduced_" + image)
        print(size)
 
        
    os.system("cp " + host + "/reduced_" + image + " " + host + "/copy_reduced_" + image)
    factor, _, size = reduceQuality(size, final_size, "copy_reduced_" + image, "reduced_" + image)
    os.system("rm " + host + "/copy_reduced_" + image)
    # scale = 90
    # isScaled = False
    # while(size>final_size):
    #     isScaled = True
    #     os.system("convert " + host + "/reduced_" + image + " -scale " + str(scale) + "% " + "-resize "+ str(org_width) + "x" + str(org_height) +" "+ host + "/reduced_"+ image)
    #     size = os.path.getsize(host + "/reduced_" + image)
    #     if (size == ((ERROR_MARGIN*final_size)-final_size) or size == ((ERROR_MARGIN*final_size)+final_size)):
    #         break
    #     print('scale {} image of size {}'.format(scale,size))
    #     if scale < 5:
    #         scale = scale - scale*0.05
    #     else:
    #         if(size > final_size):
    #             scale = math.floor(scale / 2)
    #         else:
    #             scale = math.floor(0.75*2*scale)
    
        # scale = scale - scale*0.05
    isRemoved = False
    if(size>final_size):
        
        isRemoved = True
        # img = PIL.Image.open("./" + host + "/reduced_" + image)
        # img1 = img.convert('RGBA').convert("P", palette=PIL.Image.ADAPTIVE, colors=1)
        # img1.save("./" + host + "/reduced_" + image)
        os.system("convert -size "+ str(org_width)+ "x" + str(org_height) +" xc:transparent " + host + "/reduced_" + image)

    if not isFactored:
        factor = 100
    # if not isScaled:
    #     scale = 100
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
        target = results.loc[image,"Target Size of Image"]
        
        # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
        results.loc[image,"Reduced Size of Image"], results.loc[image,"Factor"], removed,results.loc[image,"Black and White"] = reduce_to(image,target)
        results.loc[image,"Removed"] = removed
        to_replace = results.loc[image,"Image Source"]
        print(to_replace)
        replace_with = "https://localhost:4696/"+host+"/reduced_"+ image
        
        html = html.replace(to_replace, replace_with)
        print("replaced")
        # if removed:
        #     to_replace = "https://localhost:4696/"+host+"/reduced_"+ image + "\" "
        #     replace_with = "https://localhost:4696/"+host+"/reduced_"+ image + "\" " + "style=\"display:none\""
        sys.stdout.flush()
    except Exception as e:
        print("ERROR:",e)

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

# html = html.replace("srcset=")


driver.execute_script("document.body.innerHTML = arguments[0]", html)

# Manually remove srcset, forcing it use the image we give
images = driver.find_elements(By.TAG_NAME, 'img')
for element in images:
    driver.execute_script("arguments[0].removeAttribute('srcset')", element)
    
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
results.to_csv(host+"/results.csv")