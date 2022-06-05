from shutil import register_unpack_format
import PIL.Image
from pickletools import optimize
from urllib.parse import urlparse
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
ERROR_MARGIN = 0.1

# Calculating SSIMS


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
        return mse_value, ssim_value


# Generating new images
def reduceQuality(size,final_size, orig, new, host):
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

def lossyWebp(size, final_size, orig, new, host):
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

def try_webp_reduce(image, final_size, host):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true reduced_" + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/reduced_" + new_image_name)
    print("LOSSLESS", old_size, new_size)
    if (new_size <= final_size+final_size*ERROR_MARGIN):
        # results.loc[image, "New Name"] = image
        # results.loc[image, "New Size (KB)"] = old_size
        # os.system("cd " + host + " && rm " + new_image_name )
        return new_size/1024, 100, False, False, True, "reduced_"+new_image_name, 100
        
    else:
        # os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
        # new_size = os.path.getsize(host + "/" + new_image_name)
        factor, isfactor, new_size = lossyWebp(old_size, final_size, image, "reduced_"+ new_image_name, host)
        if(new_size <= final_size+final_size*ERROR_MARGIN):
            return new_size/1024, 100, False, False, True, "reduced_"+new_image_name, factor
    return new_size/1024, 100, False, False, False, image, "-"

def webp_lossless(image, final_size, host):
    new_image_name = image.split(".")[0] + ".webp"
    os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    # size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossless)"] = size
    # webpFile.loc[image,"New Size (KB) (Lossless)"] = new_size
    
    return new_image_name, new_size

def webp_lossy(image, final_size, host):
    new_image_name = image.split(".")[0] + ".webp"
    # os.system("cd " + host + " && convert " +image +" -define webp:lossless=true " + new_image_name)
    #os.system("cd " + host + " && convert " +image +" -define webp:target-size="+str(final_size) + " " + new_image_name)
    # path = "./"+host+"/"+image
    # im = Image.open(path)
    # im.save("./"+host+"/"+new_image_name, "WEBP", quality=50, optimize=True, lossless=False)
    old_size = os.path.getsize(host + "/" + image)
    
    factor, isfactor, new_size = lossyWebp(old_size, final_size, image, new_image_name, host)
    # webpFile.loc[image,"New Size (KB) (Lossless)"] = new_size
    
    # new_size = os.path.getsize(host + "/" + new_image_name)
    # size , _, _,_, name = reduce_to(new_image_name,final_size)
    # newFile.loc[image,"New Size (KB) (Lossy)"] = size
    return new_image_name, new_size

def jpeg_reduce(image, final_size, host):
    new_image_name = image.split(".")[0] + ".jpg"
    os.system("cd " + host + " && convert " + image + " " +  new_image_name)
    
    old_size = os.path.getsize(host + "/" + image)
    new_size = os.path.getsize(host + "/" + new_image_name)
    size , factor, isRemoved, isBlack, new_image_name = reduce_to(new_image_name,final_size, host)
    # return end_size/1024, factor, isRemoved, isBlack, "reduced_" + image
    # os.system("cp " + host + "/" + new_image_name + " " + host + "/reduced_" + new_image_name)
    
    # newFile.loc[image,"New Size (KB) (JPEG)"] = size
    return size , factor, isRemoved, isBlack, new_image_name

def reduce_to(image, final_size, host):
    
    print(image)

    
    # Get original size
    size = os.path.getsize(host + "/" + image)
    
    # Make new image (reduced)
    org_width, org_height = (Image.open(host + "/" + image)).size
    os.system("cp " + host + "/" + image + " " + host + "/reduced_" + image)
    
    # STEP 1: Reduce quality 
    factor, isFactored, size = reduceQuality(size, final_size, image, "reduced_" +image, host)

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
    _, _, size = reduceQuality(size, final_size, "copy_reduced_" + image, "reduced_" + image, host)
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
    