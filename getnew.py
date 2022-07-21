from urllib.parse import urlparse
import os
import pqual
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
import time
from skimage.metrics import structural_similarity as ssim
import VCPR
BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)
ERROR_MARGIN = 0.1 # 5%


url = sys.argv[1]
a = float(sys.argv[2]) #IAS
b = float(sys.argv[3]) #Area
c = float(sys.argv[4]) #Location
d = float(sys.argv[5]) #OG Size

# newFile = pd.DataFrame(columns=("Image Name", "Original Size (KB)", "Target Size (KB)", "New Size (KB) (Lossy)", "New Size (KB) (Lossless)", "New Size (KB) (Original)", "New Size (KB) (JPEG)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")
newFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")
moreFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")
# webpFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "New Size Lossy (KB)", "New Size Lossless (KB)"))
# webpGoalFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "New Size Lossy (KB)", "New Size Lossless (KB)"))
siteFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
if len(host.split("."))>1:
    host = ".".join(parsed.netloc.split(".")[-3:])
    
with open(host+"/source.html", "r", encoding='utf-8') as f:
    html= f.read()
    
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
        # target = webpFile.loc[image,"Target Size (KB)"]
        
        target = target*1024
        
        # REMOVE
        og = sum(results["Original Size (KB)"])
        red = sum(results["Target Size of Image"])
        target = (results.loc[image,"Original Size (KB)"] * 1024) / (og/red)
        # REMOVE
        
        # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
        webp_size, webp_factor, webp_removed, webp_color, webpTrue, webp_image, encoding_quality = VCPR.try_webp_reduce(image, target, host)
        jpg_size , jpg_factor, jpg_removed, jpg_color, jpg_image = VCPR.jpeg_reduce(image, target, host)
        
        # jpg_size, jpg_factor, jpg_removed, jpg_color, jpg_image = reduce_to(image,target)
        print("IMAGES: ", image, webp_image, jpg_image)
        try:
            _, webp_ssim = VCPR.findSSIM("./"+host+"/"+image, "./"+host+"/"+webp_image)
            _, jpg_ssim = VCPR.findSSIM("./"+host+"/"+image, "./"+host+"/"+jpg_image)
        except Exception:
            print("NO SSIM")
        final_ssim = None
        final_size = None
        
        
        if not webpTrue and jpg_removed:
            removed = True
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"] = 0, 0, jpg_removed, 0
            results.loc[image,"Removed"] = True
            results.loc[image, "JPG"] = False
            results.loc[image, "WEBP"] = False
            final_ssim = 0
            
        elif webpTrue and not jpg_removed and (abs(jpg_ssim-webp_ssim) <= 0.15 or webp_ssim > jpg_ssim):
            removed = webp_removed
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"],results.loc[image,"Color Depth Reduction"], results.loc[image, "WEBP"] = webp_size, encoding_quality, False, True
            results.loc[image,"Removed"] = webp_removed
            results.loc[image, "JPG"] = False
            results.loc[image,"WEBP Encoding Quality"] = encoding_quality
            final_ssim = webp_ssim
            
            result = webp_image
            
        elif not webpTrue or jpg_ssim > webp_ssim:

            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"] = jpg_size, jpg_factor, jpg_removed, jpg_color
            results.loc[image, "JPG"] = True
            results.loc[image, "WEBP"] = False
            results.loc[image,"Removed"] = jpg_removed
            final_ssim = jpg_ssim
            result = jpg_image
        else:                
            removed = webp_removed
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"],results.loc[image,"Color Depth Reduction"], results.loc[image, "WEBP"] = webp_size, encoding_quality, False, True
            results.loc[image,"Removed"] = webp_removed
            results.loc[image, "JPG"] = False
            results.loc[image,"WEBP Encoding Quality"] = encoding_quality
            final_ssim = webp_ssim
            
            result = webp_image
        
        results.loc[image,"Final SSIM"] = final_ssim
        
        
        print("FINAL SSIM")
        if(final_ssim < 0.01):
            removed = True
            results.loc[image,"Removed"] = removed
        
        to_replace = results.loc[image,"Image Source"]
        
        if (removed):
            src_str = "src=\""+ to_replace + "\""
            replace_with = src_str + " style=\"display:none\""
            html = html.replace(src_str, "")
            print(replace_with)
            continue
            
        print(to_replace)
        replace_with = "https://localhost:4696/"+host+"/" +result
        
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
#driver.execute_script("document.body.style.zoom='10%'")
driver.save_screenshot(host+"/reduced.png")
# ob=Screenshot_Clipping.Screenshot()
# img=ob.full_Screenshot(driver,save_path=os.getcwd()+"/"+host,image_name="reduced.png")
driver.close()

f_mse, f_ssim = VCPR.findSSIM(host+"/reduced.png", host+"/original.png")
print("(" + str(f_mse) + " " + str(f_ssim) + ")")
results['Reduced Size of Image'] = results['Reduced Size of Image'].replace('', pd.NA).fillna(results['Target Size of Image'])
results['Final SSIM'] = results['Final SSIM'].replace('', pd.NA).fillna(0)
results["Error"] = results["Target Size of Image"] - results["Reduced Size of Image"]
QSS = pqual.compare(host+"/original.png", host+"/reduced.png",mode="screenshot")
our_qss = sum(results["Final SSIM"]*results["Normalized Area"])/sum(results["Normalized Area"])
qss_file = host+'_QSS_test.csv'
if (os.path.isfile(qss_file)):
    qss_df = pd.read_csv(qss_file, index_col=0)
    qss_df.loc[len(qss_df)] = [a,b,c,d,QSS,f_ssim, our_qss]
    qss_df.to_csv(qss_file)
else:
    pd.DataFrame([[a,b,c,d,QSS,f_ssim, our_qss]], columns=["IAS", "Area", "Location", "Original Size", "QSS", "SSIM", "Our QSS"]).to_csv(qss_file)


results.to_csv(host+"/results.csv")
