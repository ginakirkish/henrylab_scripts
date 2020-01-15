__author__ = 'gkirkish'

from glob import glob
from pbr.base import _get_output
from subprocess import Popen, PIPE
import json
import shutil
from subprocess import check_call
import subprocess
import PIL
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def get_t1(mse):
    t1_file = ""
    with open(_get_output(mse)+"/"+mse+"/alignment/status.json") as data_file:
        data = json.load(data_file)
        if len(data["t1_files"]) > 0:
            t1_file = data["t1_files"][-1]
    return t1_file

def get_first(mse):
    first = glob("{}/{}/first_all/*firstseg*".format(_get_output(mse),mse))
    if len(first) > 0:
        first = first[-1]
    #else:
        #first = ""
    return first


def convert2jpg(file, o ):
    output = "{}/{}/med2img/".format(_get_output(mse),mse)
    print(output)
    cmd = ["med2image", "-i", file,  "-d", output,  "-o", "jpg","-o",o, "-s","m"]
    print("med2image", "-i", file,  "-d", output,  "-o", "jpg","-o",o, "-s","m")
    Popen(cmd).wait()
    return output
   


def overlay(t1_png, first_png):
    # generate gray scale image
    import scipy.misc
    # read in image
    im = plt.imread(first_png)
    # plot image in color
    plt.imshow(im.mean(2), cmap="jet_r")
    #save image in color
    color_first = "{}/color-first.png".format(output)
    plt.imsave(color_first, im.mean(2), cmap="BuPu")# "prism")#"BuPu")
    img = Image.open(first_png)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save("img2.png", "PNG")
    #plt.imsave("img2.png", im.mean(2), cmap="BuPu")
    o = "{}/overlay.png".format(output)
    cmd = ["composite", "-blend", "60",  t1_png, "img2.png", o]
    print(cmd)
    Popen(cmd).wait()


def overlay_test(t1_png, first_png):
    plt.imshow(t1_png, cmap='gray') # I would add interpolation='none'
    plt.imshow(first_png, cmap='jet', alpha=0.5) # interpolation='none'
    Image2_mask = ma.masked_array(t1_png > 0, first_png)
    plt.figure()
    plt.subplot(1,2,1)
plt.imshow(im, 'gray', interpolation='none')
plt.subplot(1,2,2)
plt.imshow(im, 'gray', interpolation='none')
plt.imshow(masked, 'jet', interpolation='none', alpha=0.7)
plt.show()

mse_list = ["mse1230"]
for mse in mse_list:
    t1 = get_t1(mse)
    first = get_first(mse)
    print(t1)
    print(first)

    convert2jpg(t1, "t1") 
    convert2jpg(first, "first")
    output =  "{}/{}/med2img/".format(_get_output(mse),mse)
    t1_png = glob("{}/t1*.png".format(output))[0]
    first_png = glob("{}/first*.png".format(output))[0]
    print(t1_png, first_png)
    overlay(t1_png, first_png)




    

    
    


    

    


