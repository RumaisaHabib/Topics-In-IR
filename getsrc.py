from selenium import webdriver
import re
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager
import os

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("--test-type")
mobile_emulation = {
        "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" }
options.add_experimental_option("mobileEmulation", mobile_emulation)
# options.add_argument('--user-agent=Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19')

# options.binary_location = "/usr/bin/chromium"
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

url = 'https://google.com/'
parsed = urlparse(url)
domain = parsed.netloc.split(".")[-2:]
host = ".".join(domain)
print(host)

driver.get(url)

images = driver.find_elements_by_tag_name('img')
try:
    os.system("mkdir " + host)
except:
    pass
print("===== IMAGES =====")
with open(host+"/images.txt", "w") as f:
    for image in images:
        i = image.get_attribute('src')
        print(i)
        f.write(i + "\n")
os.system("cd " + host + " && cat images.txt | parallel --gnu \"wget {}\"")



driver.close()