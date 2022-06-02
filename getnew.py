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
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

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
ERROR_MARGIN = 0.1 # 10%


url = sys.argv[1]

# newFile = pd.DataFrame(columns=("Image Name", "Original Size (KB)", "Target Size (KB)", "New Size (KB) (Lossy)", "New Size (KB) (Lossless)", "New Size (KB) (Original)", "New Size (KB) (JPEG)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")
newFile = pd.DataFrame(columns=("Image Name", "Target Size (KB)", "SSIM Lossy", "SSIM Lossless", "SSIM Original", "SSIM JPEG")).set_index("Image Name")

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

def lossyWebp(size, final_size, orig, new):
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
        # os.system("convert " + host + "/" + orig + " -quality " + str(factor) + "% " + host + "/" + new)
        path = "./" + host + "/" + orig
        # new_image_name = image.split(".")[0] + ".webp"
        
        im = Image.open(path)
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
        # os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
        # new_size = os.path.getsize(host + "/" + new_image_name)
        factor, isfactor, new_size = lossyWebp(old_size, final_size, image, new_image_name)
        if(new_size <= final_size):
            return new_size/1024, 100, False, False, True
    return new_size/1024, 100, False, False, False

def webp_lossless(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossless)"] = size
    return name

def webp_lossy(image, final_size):
    new_image_name = image.split(".")[0] + ".webp"
    # os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    #os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
    # path = "./"+host+"/"+image
    # im = Image.open(path)
    # im.save("./"+host+"/"+new_image_name, "WEBP", quality=50, optimize=True, lossless=False)
    old_size = os.path.getsize(host + "/" + image)
    
    factor, isfactor, new_size = lossyWebp(old_size, final_size, image, new_image_name)
    
    # new_size = os.path.getsize(host + "/" + new_image_name)
    size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossy)"] = size
    return name

def jpeg_reduce(image, final_size):
    new_image_name = image.split(".")[0] + ".jpg"
    os.system("cd " + host + " && convert " + image + " " + new_image_name)
    
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (JPEG)"] = size
    return name
    



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
    factor, isFactored, size = reduceQuality(size, final_size, image, "reduced_" +image)

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
    return end_size/1024, factor, isRemoved, isBlack, "reduced_" + image
    
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
        
        # if(image.split('.')[-1] == "png"):
        #     newFile.loc[image,"Target Size (KB)"] = target
            
            
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
            
        
        # os.system("convert " + host + "/" + image + " -define webp:extent=" + str(round(target,2)) + "kb " + host + "/reduced_"+ image)
        size, factor, removed, color, webpTrue = try_webp_reduce(image, target)
        if not webpTrue:
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Factor"], removed,results.loc[image,"Color Depth Reduction"], _ = reduce_to(image,target)
            results.loc[image,"Removed"] = removed
        else:
            results.loc[image,"Reduced Size of Image"], results.loc[image,"Factor"],results.loc[image,"Color Depth Reduction"] = size, factor, color
            results.loc[image,"Removed"] = removed
            
        
        to_replace = results.loc[image,"Image Source"]
        if (removed):
            # html_list = html.split()
            # insert_at = html_list.index("src=\""+ to_replace + "\"") + 1
            # html_list[insert_at:insert_at] = ["style=display:none"]
            # html = " ".join(html_list)
            src_str = "src=\""+ to_replace + "\""
            html = html.replace(src_str, src_str + " style=display:none")
            continue
            
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
newFile.to_csv(host+"/newFile.csv")
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
