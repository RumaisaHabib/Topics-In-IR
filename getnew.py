from pickletools import optimize
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
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np

def mse(imageA, imageB):
 # the 'Mean Squared Error' between the two images is the sum of the squared difference between the two images
 mse_error = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
 mse_error /= float(imageA.shape[0] * imageA.shape[1])
	
 # return the MSE. The lower the error, the more "similar" the two images are.
 return mse_error

def compare(imageA, imageB):
 # Calculate the MSE and SSIM
 m = mse(imageA, imageB)
 s = ssim(imageA, imageB)

 # Return the SSIM. The higher the value, the more "similar" the two images are.
 return s


def findSSIM(first, second):

    # Import images
    image1 = cv2.imread(first)
    image2 = cv2.imread(second, 1)

    # Convert the images to grayscale
    try:
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    except Exception:
        pass

    # Check for same size and ratio and report accordingly
    ho, wo, _ = image1.shape
    hc, wc, _ = image2.shape
    ratio_orig = ho/wo
    ratio_comp = hc/wc
    dim = (wc, hc)

    if round(ratio_orig, 2) != round(ratio_comp, 2):
        print("\nImages not of the same dimension. Check input.")
        exit()

    # Resize first image if the second image is smaller
    elif ho > hc and wo > wc:
        print("\nResizing original image for analysis...")
        gray1 = cv2.resize(gray1, dim)

    elif ho < hc and wo < wc:
        print("\nCompressed image has a larger dimension than the original. Check input.")
        exit()

    if round(ratio_orig, 2) == round(ratio_comp, 2):
        mse_value = mse(gray1, gray2)
        ssim_value = compare(gray1, gray2)
        # print("MSE:", mse_value)
        # print("SSIM:", ssim_value)
        return mse_value, ssim_value

BYTE_SIZE = 1024
PHONE_WIDTH = 360
PHONE_HEIGHT = 640
PIXEL_RATIO = 3.0
PROGRESS_BAR = "{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)
ERROR_MARGIN = 0.1 # 5%


url = sys.argv[1]

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
    while (factor>6.25):
        isFactored = True
        # im = Image.open("./"+host+"/"+orig)
        # image_rescaled = rescale(img, factor, anti_aliasing=False)
        # imsave(host + "/reduced_" + image, image_rescaled)
        print("FACTOIR: ", factor," " )
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

def lossyWebp(size, final_size, orig, new):
    if (size<=final_size+final_size*ERROR_MARGIN):
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
        # os.system("convert " + host + "/" + orig + " -quality " + str(factor) + "% " + host + "/" + new)
        path = "./" + host + "/" + orig
        # new_image_name = image.split(".")[0] + ".webp"
        im = Image.open(path)
        print("LOSSY FACTOR: ", factor)
        im.save("./"+host+"/"+ new, "WEBP", quality=factor, optimize=True, lossless=False)
        size = os.path.getsize(host + "/" + new)
        # size = os.path.getsize(host + "/" + new)
        if (size == (final_size-(ERROR_MARGIN*final_size)) or size == ((ERROR_MARGIN*final_size)+final_size) or factor <= 5):
            break
        if old_size == new_size:
            break
        old_size = new_size
        new_size = size
        #print('factor {} image of size {}'.format(factor,size))
        print("WEBP", size, factor)
        if(size > final_size):
            max = factor
        else:
            min = factor
        factor = round(((min+max)/2),4)

    return factor, isFactored, size

def try_webp_reduce(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true reduced_" + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/reduced_" + new_image_name)
    print("LOSSLESS", old_size, new_size)
    if (new_size <= final_size+final_size*ERROR_MARGIN):
        # results.loc[image, "New Name"] = image
        # results.loc[image, "New Size (KB)"] = old_size
        # os.system("cd " + host + " && rm " + new_image_name )
        return new_size/1024, 100, False, False, True, new_image_name, 100
        
    else:
        # os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
        # new_size = os.path.getsize(host + "/" + new_image_name)
        factor, isfactor, new_size = lossyWebp(old_size, final_size, image, "reduced_"+ new_image_name)
        if(new_size <= final_size+final_size*ERROR_MARGIN):
            return new_size/1024, 100, False, False, True, "reduced_"+new_image_name, factor
    return new_size/1024, 100, False, False, False, image, "-"

def webp_lossless(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    # size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossless)"] = size
    # webpFile.loc[image,"New Size (KB) (Lossless)"] = new_size
    
    return new_image_name, new_size

def webp_lossy(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    # os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    #os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
    # path = "./"+host+"/"+image
    # im = Image.open(path)
    # im.save("./"+host+"/"+new_image_name, "WEBP", quality=50, optimize=True, lossless=False)
    old_size = os.path.getsize(host + "/" + image)
    
    factor, isfactor, new_size = lossyWebp(old_size, final_size, image, new_image_name)
    # webpFile.loc[image,"New Size (KB) (Lossless)"] = new_size
    
    # new_size = os.path.getsize(host + "/" + new_image_name)
    # size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossy)"] = size
    return new_image_name, new_size

def jpeg_reduce(image, final_size):
    new_image_name = image.split(".")[0] + ".jpg"
    os.system("cd " + host + " && convert " + image + " " + new_image_name)
    
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    size , factor, isRemoved, isBlack, new_image_name = reduce_to(new_image_name,final_size)
    # return end_size/1024, factor, isRemoved, isBlack, "reduced_" + image
    
    # newFile.loc[image,"New Size (KB) (JPEG)"] = size
    return size , factor, isRemoved, isBlack, new_image_name

# def jpeg_convert(image, final_size):
#     new_image_name = image.split(".")[0] + ".jpg"
#     os.system("cd " + host + " && convert " + image + " " + new_image_name)
#     reduce_to(new_image_name, final_size)

def reduce_to(image, final_size):
    
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
    if(size>final_size+final_size*ERROR_MARGIN):
        isBlack = True
        print("TRYING TO COLOR")
        try:
            os.system("convert -colors 2 " + host + "/reduced_" + image + " " + host + "/reduced_" + image)
        except Exception:
            print("CANT COLOR")
        size = os.path.getsize(host + "/reduced_" + image)
        print(size)
 
        
    os.system("cp " + host + "/reduced_" + image + " " + host + "/copy_reduced_" + image)
    _, _, size = reduceQuality(size, final_size, "copy_reduced_" + image, "reduced_" + image)
    os.system("rm " + host + "/copy_reduced_" + image)
    
    # STEP 3: Remove image MOVE THIS
    isRemoved = False
    if(size>final_size+final_size*ERROR_MARGIN):
        isRemoved = True

    if not isFactored:
        factor = 100
        
    end_size = os.path.getsize(host + "/reduced_" + image)
    if isRemoved:
        end_size = 0
    return size/1024, factor, isRemoved, isBlack, "reduced_" + image
    
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
        # newFile.loc[image,"Target Size (KB)"] = target/1024
        # moreFile.loc[image, "Target Size (KB)"] = target/1024
        # siteFile.loc[image, "Target Size (KB)"] = target/1024
        
            
        # if(image.split('.')[-1] == "png"):
        
        #     name, size = webp_lossless(image, target)
        #     print(image, name)
        #     if(size>target+target*ERROR_MARGIN): # target not reached remove image so ssim = 0
        #         newFile.loc[image,"SSIM Lossless"] = 0
        #         siteFile.loc[image,"SSIM Lossless"] = 0
                
        #     else:
        #         reducedPath = "./"+host+"/"+name

        #         originalPath = "./"+host+"/"+image
        #         # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #         mseval, ssimval = findSSIM(originalPath, reducedPath)
        #         newFile.loc[image,"SSIM Lossless"] = ssimval
        #         siteFile.loc[image,"SSIM Lossless"] = ssimval
                
            
            
        #     name, size = webp_lossy(image, target)
        #     if(size>target+target*ERROR_MARGIN): # target not reached remove image so ssim = 0
        #         newFile.loc[image,"SSIM Lossy"] = 0
        #         siteFile.loc[image,"SSIM Lossy"] = 0
                
        #     else: 
        #         reducedPath = "./"+host+"/"+name

        #         originalPath = "./"+host+"/"+image
        #         # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #         mseval, ssimval = findSSIM(originalPath, reducedPath)
        #         newFile.loc[image,"SSIM Lossy"] = ssimval
        #         siteFile.loc[image,"SSIM Lossy"] = ssimval
                
            
        #     size, _, _, _, name = reduce_to(image, target)
        #     # newFile.loc[image,"New Size (KB) (Original)"] = size
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     newFile.loc[image,"SSIM Original"] = ssimval
        #     siteFile.loc[image,"SSIM Original"] = ssimval
            
            
        #     _, _, _, _, name = jpeg_reduce(image, target)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     siteFile.loc[image,"SSIM JPEG"] = ssimval
        
        
        
        # if(image.split('.')[-1] == "jpg"):
        
        #     name, size = webp_lossless(image, target)
        #     print(image, name)
        #     if(size>target+target*ERROR_MARGIN): # target not reached remove image so ssim = 0
        #         moreFile.loc[image,"SSIM Lossless"] = 0
        #         siteFile.loc[image,"SSIM Lossless"] = 0
                
        #     else:
        #         reducedPath = "./"+host+"/"+name

        #         originalPath = "./"+host+"/"+image
        #         # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #         mseval, ssimval = findSSIM(originalPath, reducedPath)
        #         siteFile.loc[image,"SSIM Lossless"] = ssimval
            
            
        #     name, size = webp_lossy(image, target)
        #     if(size>target+target*ERROR_MARGIN): # target not reached remove image so ssim = 0
        #         moreFile.loc[image,"SSIM Lossy"] = 0
        #         siteFile.loc[image,"SSIM Lossy"] = 0
                
        #     else: 
        #         reducedPath = "./"+host+"/"+name

        #         originalPath = "./"+host+"/"+image
        #         # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #         mseval, ssimval = findSSIM(originalPath, reducedPath)
        #         moreFile.loc[image,"SSIM Lossy"] = ssimval
        #         siteFile.loc[image,"SSIM Lossy"] = ssimval
                
            
        #     size, _, _, _, name = reduce_to(image, target)
        #     # newFile.loc[image,"New Size (KB) (Original)"] = size
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM Original"] = ssimval
        #     siteFile.loc[image,"SSIM Original"] = ssimval
            
            
        #     _, _, _, _, name = jpeg_reduce(image, target)
        #     # name = jpeg_reduce(image, target)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM JPEG"] = ssimval
        #     siteFile.loc[image,"SSIM JPEG"] = ssimval
            
        
        
        # if(image.split('.')[-1] == "png"):
        #     newFile.loc[image,"Target Size (KB)"] = target/1024
            
            
        #     name = webp_lossless(image, target)
        #     print(image, name)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     newFile.loc[image,"SSIM Lossless"] = ssimval
            
        #     name = webp_lossy(image, target)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     newFile.loc[image,"SSIM Lossy"] = ssimval
            
        #     size, _, _, _, name = reduce_to(image, target)
        #     # newFile.loc[image,"New Size (KB) (Original)"] = size
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     newFile.loc[image,"SSIM Original"] = ssimval
            
        #     name = jpeg_reduce(image, target)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     newFile.loc[image,"SSIM JPEG"] = ssimval
        
        # if(image.split('.')[-1] == "jpg"):
        #     print("JPGshbrgfhdfgsrgh")
        #     moreFile.loc[image,"Target Size (KB)"] = target/1024
            
            
        #     name = webp_lossless(image, target)
        #     print(image, name)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM Lossless"] = ssimval
            
        #     name = webp_lossy(image, target)
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM Lossy"] = ssimval
            
        #     size, _, _, _, name = reduce_to(image, target)
        #     # newFile.loc[image,"New Size (KB) (Original)"] = size
        #     reducedPath = "./"+host+"/"+name

        #     originalPath = "./"+host+"/"+image
        #     # reducedPath = "./"+host+"/"+listOfReducedImages[0]
        #     mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM Original"] = ssimval
            
        #     name = jpeg_reduce(image, target)
            # reducedPath = "./"+host+"/"+name

            # originalPath = "./"+host+"/"+image
            # # reducedPath = "./"+host+"/"+listOfReducedImages[0]
            # mseval, ssimval = findSSIM(originalPath, reducedPath)
        #     moreFile.loc[image,"SSIM JPEG"] = ssimval
        
        
        
        # name = webp_lossless(image, target)
        # print(image, name)
        
        # name = webp_lossy(image, target)
        
        
        # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
        webp_size, webp_factor, webp_removed, webp_color, webpTrue, webp_image, encoding_quality = try_webp_reduce(image, target)
        jpg_size , jpg_factor, jpg_removed, jpg_color, jpg_image = jpeg_reduce(image, target)
        
        # jpg_size, jpg_factor, jpg_removed, jpg_color, jpg_image = reduce_to(image,target)
        print("IMAGES: ", image, webp_image, jpg_image)
        try:
            _, webp_ssim = findSSIM("./"+host+"/"+image, "./"+host+"/"+webp_image)
            _, jpg_ssim = findSSIM("./"+host+"/"+image, "./"+host+"/"+jpg_image)
        except Exception:
            print("NO SSIM")
        final_ssim = None
        final_size = None
        
        
        if not webpTrue and jpg_removed:
            removed = True
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"] = 0, 0, jpg_removed, 0
            results.loc[image,"Removed"] = True
            final_ssim = 0
            
        elif not webpTrue or jpg_ssim > webp_ssim:

            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"], removed,results.loc[image,"Color Depth Reduction"] = jpg_size, jpg_factor, jpg_removed, jpg_color
            results.loc[image, "WEBP"] = False
            results.loc[image,"Removed"] = jpg_removed
            final_ssim = jpg_ssim
            result = jpg_image
        else:                
            removed = webp_removed
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Quality Factor"],results.loc[image,"Color Depth Reduction"], results.loc[image, "WEBP"] = webp_size, encoding_quality, False, True
            results.loc[image,"Removed"] = webp_removed
            results.loc[image,"WEBP Encoding Quality"] = encoding_quality
            final_ssim = webp_ssim
            
            result = webp_image
        
        results.loc[image,"Final SSIM"] = final_ssim
        
        
        print("FINAL SSIM")
        if(final_ssim < 0.6):
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
        replace_with = "https://localhost:4696/"+host+ "redeuced_"+ result
        
        html = html.replace(to_replace, replace_with)
        print("replaced")
        sys.stdout.flush()
    except Exception as e:
        print("ERROR:",e)

# newFile.to_csv(host+"/newFile.csv")
# moreFile.to_csv(host+"/jpgFile.csv")
# siteFile.to_csv(host+"/webpFile.csv")





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
