
# Rethinking Web for Affordability and Inclusion
## ⭐Transcoding Service for webpage reduction⭐

### Introduction:
Collaborators:
 - Rumaisa Habib 🐸
 - Sarah Tanveer 🌻

This project is a work in progress to debloat webpages (specifically through image transcoding) to make webpages lighter, and hence more affordable. This was made specifically as a guide for web developers who may undertake our reccomended changes to update their webpages.

### Steps:
 - [x] Scraping images from webpages 
	 - [x] Getting all image sources from given website programmatically
	 - [x] Downloading all images from text file
 - [x] Calculating SSIM and image size (in px) of all images and assigning values to each image (and hence their reduction factor)
 - [x] Calculating webpage size (and target)
	 - [x] Get sum of all incoming bytes (= webpage size) and image sizes
	 - [x] Calculate target size using location (?) or specific metrics such as 1.5x reduction, 2x, 3x, etc.
	 	- Used user-defined target ratio to current total
 - [ ] Reducing image quality
	 - [x] Convert images to WebP
	 - [x] Reducing resolution (proportional reduction)
	 	- [x] Naive reduction
	 	- [x] Optimize time taken
 - [x] Replacing image source with reduced versions for sample reduced webpages
	 - [x] Where to store images?
	 	- Locally, and hosted on localhost
	 - [x] How to replace images programmatically?
	 	- Fetch from localhost, string replacement
 - [ ] Creating a clean tool to generate an affordability report for any given website
	 - [ ] Look into possible hosting sites e.g pythonanywhere, or a django application
	 - [ ] Design a UI for the report 

### How to run:
```
git clone https://github.com/RumaisaHabib/Topics-In-IR.git
python3 server.py
```
It will ask for a pass code, which is ```boom```
```
bash affordability_report <URL> <Target size ratio>
```

### Outputs:
- page_data.json: Overall page statistics
- results.csv: Individual image statistics (including their value, reductions, sizes, sources, etc)
- original.png: original page screenshot
- original.html: original page html
- reduced.png: reduced page screenshot
- reduced.html: reduced page html
- report.pdf: TBD

### Current limitations:
- Currently does not support batch website reduction
- It does not present a usable webpage
- It only affects images, hence the limit of reduction is less than may be actually possible.
