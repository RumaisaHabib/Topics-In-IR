from PIL import Image
img = Image.open("./googlelogo_color_160x56dp.webp")
img1 = img.convert('RGBA').convert("P", palette=Image.ADAPTIVE, colors=1)

img1.save("./temp.png")
img1.save("./temp.webp")