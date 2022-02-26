
# Rethinking Web for Affordability and Inclusion
## ⭐Transcoding Service for webpage reduction⭐

Collaborators:
 - Rumaisa Habib 🐸
 - Sarah Tanveer 🌻

This project is a work in progress to debloat webpages (specifically through image transcoding) to make webpages lighter, and hence more affordable. 

Steps:

 - [x] Scraping images from webpages 
	 - [x] Getting all image sources from given website programmatically
	 - [x] Downloading all images from text file
 - [ ] Calculating SSIM and image size (in px) of all images and assigning values to each image (and hence their reduction factor)
 - [ ] Calculating webpage size (and target)
	 - [x] Get sum of all incoming bytes (= webpage size) and image sizes
	 - [ ] Calculate target size using location (?) or specific metrics such as 1.5x reduction, 2x, 3x, etc.
 - [ ] Reducing image quality
	 - [x] Convert images to WebP
	 - [ ] Reducing resolution (proportional reduction)
 - [ ] Replacing image source with reduced versions for sample reduced webpages
	 - [ ] Where to store images?
	 - [ ] How to replace images programmatically?
 - [ ] Creating a clean tool to generate an affordability report for any given website
	 - [ ] Look into possible hosting sites e.g pythonanywhere, or a django application
	 - [ ] Design a UI for the report 
