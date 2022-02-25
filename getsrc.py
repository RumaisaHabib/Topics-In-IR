from selenium import webdriver
import re
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
import os
import sys
from selenium.webdriver.common.by import By


''' 
STEP ONE:
Scrape images from the URL

'''

# Set options for web scraper
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")

# Mobile emulation, currently configured for Nexus 5
mobile_emulation = {
        "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
options.add_experimental_option("mobileEmulation", mobile_emulation)
# options.add_argument('--user-agent=Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19')

# options.binary_location = "/usr/bin/chromium"

# Chrome web driver
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)


# URL settings, to be replaced with text file of URLs (possible)
url = sys.argv[1]

# Get website name
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
print(host)

driver.get(url)

# Get all elements labelled 'img'. This line gives a 'The syntax of the command is incorrect.' warning but still works (lol).
images = driver.find_elements(By.TAG_NAME, 'img')



# Make directory for this website, in case it doesn't exist
try:
    os.system("mkdir " + host)
except:
    pass


print("===== IMAGES =====")
with open(host+"/images.txt", "w") as f:
    for image in images:
        i = image.get_attribute('src')
        print(i)
        # Writes image URL source to a file labelled images.txt in the host directory
        f.write(i + "\n")

'''
TO DO:
- Use wget to download all images from the images.txt file into the directory of the host
- Possible command (for linux):
os.system("cd " + host + " && cat images.txt | parallel --gnu \"wget {}\"")
'''
driver.close()