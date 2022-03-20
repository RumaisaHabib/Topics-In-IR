from PIL import Image
img = Image.open("./googlelogo_color_160x56dp.webp")
info = img.info
img1 = img.convert('RGBA').convert("P", palette=Image.ADAPTIVE, colors=1)

img1.show()
img1.save("./temp.webp", **info)