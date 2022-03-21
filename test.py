from PIL import Image
import os
# img = Image.open("./googlelogo_color_160x56dp.webp")
# info = img.info
# img1 = img.convert('RGBA').convert("P", palette=Image.ADAPTIVE, colors=1)

# img1.save("./temp.webp", **info)
image_name = "ae8dae936955122bd324f0d744d17c3b.jpg"
print(os.path.getsize(image_name))

os.system("convert -depth 2 " + image_name + " temp.webp")
os.system("convert "  + image_name + " -set colorspace Gray -separate -average temp.webp")
print(os.path.getsize("temp.webp"))