from os import listdir
from os.path import isfile, join
import random
import math
import sys
import xml.etree.cElementTree as ET
from tkinter import filedialog
from tkinter import *


#import pillow
try:
    import PIL
    from PIL import Image
except ImportError:
    from pip._internal import main
    main(['install', '--user','Pillow'])
    import PIL
    from PIL import Image


extenstions = [".png", ".jpg", ".tif", ".PNG", ".JPG", ".TIF"]

def Create_XML_File(xml_to_copy, image_name, bnd1, bnd2, bnd3, bnd4, image_number):
    
    old_tree = ET.parse(xml_to_copy)
    old_root = old_tree.getroot()

    extension = image_name[image_name.rfind("."):]
    
    file_number = -1
    if(image_number < 10000):
        file_number = f'{image_number:04}'
    else:
        file_number = str(image_number)


    root = ET.Element("annotation")
    folder = ET.SubElement(root, "folder").text = old_root.find("folder").text
    filename = ET.SubElement(root, "filename").text = get_base_name(image_name) + file_number + extension
    path = ET.SubElement(root, "path").text = folderEntry.get() + get_base_name(image_name) + file_number + extension
    source = ET.SubElement(root, "source")
    database = ET.SubElement(source, "database").text = old_root.find("source").find("database").text

    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width").text = old_root.find("size").find("width").text
    height = ET.SubElement(size, "height").text = old_root.find("size").find("height").text
    depth = ET.SubElement(size, "depth").text = old_root.find("size").find("depth").text

    segmented = ET.SubElement(root, "segmented").text = old_root.find("segmented").text

    object = ET.SubElement(root, "object")
    name = ET.SubElement(object, "name").text = old_root.find("object").find("name").text
    pose = ET.SubElement(object, "pose").text = old_root.find("object").find("pose").text
    truncated = ET.SubElement(object, "truncated").text = old_root.find("object").find("truncated").text
    difficult = ET.SubElement(object, "difficult").text = old_root.find("object").find("difficult").text
    bndbox = ET.SubElement(object, "bndbox")
    xmin = ET.SubElement(bndbox, "xmin").text = str(bnd1)
    ymin = ET.SubElement(bndbox, "ymin").text = str(bnd2)
    xmax = ET.SubElement(bndbox, "xmax").text = str(bnd3)
    ymax = ET.SubElement(bndbox, "ymax").text = str(bnd4)

    tree = ET.ElementTree(root)
    tree.write(folderEntry.get() + get_base_name(image_name) + file_number + ".xml")


def Create_Image(original_image, image_number, pos_x, pos_y, size_x, size_y):

    img = PIL.Image.open(folderEntry.get() + original_image)

    img2 = img.crop((pos_x, pos_y, pos_x + size_x, pos_y + size_y))
    img2 = img2.resize(img.size)

    file_number = -1
    if(image_number < 10000):
        file_number = f'{image_number:04}'
    else:
        file_number = str(image_number)

    img_name = get_base_name(original_image)
    extension = original_image[original_image.rfind("."):]
    new_img_name = img_name + file_number + extension

    #create img & xml
    img2.save(folderEntry.get() + new_img_name)


def get_last_number(files):
    #get number of last image
    number_list = []
    for x in files:   
        #make list of extenstions and search for them
        if(x[x.rfind("."):] in extenstions):
            base_file = x[:x.rfind(".")]
            number_list.append(int(base_file[-4:]))

    return max(number_list) + 1


def get_new_bnd(old_xml, posx, posy, width, height, resolutionx, resolutiony):
    tree = ET.parse(folderEntry.get() + old_xml)
    root = tree.getroot()

    box = root.find("object").find("bndbox")
    old_x_min = int(box.find("xmin").text)
    old_y_min = int(box.find("ymin").text)
    old_x_max = int(box.find("xmax").text)
    old_y_max = int(box.find("ymax").text)

    x_min = clamp(round(((old_x_min - posx)/width) * resolutionx), 0, resolutionx)
    y_min = clamp(round(((old_y_min - posy)/height) * resolutiony), 0, resolutiony)
    x_max = clamp(round(((old_x_max - posx)/width) * resolutionx), 0, resolutionx)
    y_max = clamp(round(((old_y_max - posy)/height) * resolutiony), 0, resolutiony)


    return [x_min, y_min, x_max, y_max]


def clamp(num, min, max):
    if(num < min):
        return min
    if(num > max):
        return max
    return num


def get_base_name(image_name):
    #input = name with number + extension
    #output = name
    name_number = image_name[:image_name.rfind(".")]

    i = 1
    while True:
        try:
            int(name_number[-i:])
            i += 1
        except:
            return name_number[:-i+1]

    return "base_name_error"


#~~~~~~~~~~~~~~~~~~~~~~~GUI~~~~~~~~~~~~~~~~~~~~~~~~~
root = Tk()
root.title("Create Partial Images")


def directory_button():
    directory = filedialog.askdirectory()
    if (sys.platform.startswith("win")):
        directory = directory.replace("/", "\\") + "\\"
    else:
        directory = directory + "/"
    folderEntry.delete(0,END)
    folderEntry.insert(0,directory)

    files = [f for f in listdir(directory) if isfile(join(directory, f))]

    #fill in information
    starting_number = get_last_number(files)
    starting_numberEntry.delete(0,END)
    starting_numberEntry.insert(0, starting_number)
    
    img_name = get_base_name(files[0])
    base_nameEntry.delete(0,END)
    base_nameEntry.insert(0, img_name)

def update_vars(keypress):
    directory = folderEntry.get()
    files = [f for f in listdir(directory) if isfile(join(directory, f))]

    #fill in information
    starting_number = get_last_number(files)
    starting_numberEntry.delete(0,END)
    starting_numberEntry.insert(0, starting_number)
    
    img_name = get_base_name(files[0])
    base_nameEntry.delete(0,END)
    base_nameEntry.insert(0, img_name)

def submit_button():
    #error check
    if(folderEntry.get() == ""):
        infoLabel.config(text="A directory must be selected", fg="red")
        return
    if(new_imageEntry.get() == ""):
        infoLabel.config(text="\"Number of New Images\" cannot be empty", fg="red")
        return
    if(min_sizeEntry.get() == ""):
        infoLabel.config(text="\"Minimum size\" cannot be empty", fg="red")
        return
    if(max_sizeEntry.get() == ""):
        infoLabel.config(text="\"Maximum size\" cannot be empty", fg="red")
        return
    if(base_nameEntry.get() == ""):
        infoLabel.config(text="\"Base Name\" cannot be empty", fg="red")
        return
    if(starting_numberEntry.get() == ""):
        infoLabel.config(text="\"Starting Number\" cannot be empty", fg="red")
        return

    if(float(min_sizeEntry.get()) < 0 or float(min_sizeEntry.get()) > float(max_sizeEntry.get())):
        infoLabel.config(text="\"Minimum size\" must be greater than 0 and less than \"Maximum size\"", fg="red")
        return
    if(float(max_sizeEntry.get()) > 1 or float(min_sizeEntry.get()) > float(max_sizeEntry.get())):
        infoLabel.config(text="\"Maximum size\" must be less than 1 and greater than \"Minimum size\"", fg="red")
        return

    try:
        directory = folderEntry.get()
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        img_number = int(starting_numberEntry.get())-1

        base_image_count = 0
        for i in files:
            if(i[i.rfind("."):] in extenstions):
                base_image_count += 1

        total_images = int(new_imageEntry.get()) * base_image_count

        #loop through original images
        for image in files:
            if(image[image.rfind("."):] in extenstions):
                #get xml file
                xml_name = image[:image.rfind(".")] + ".xml"
                
                resolution = Image.open(directory + image).size

                for i in range(int(new_imageEntry.get())):
                    img_number += 1

                    size = random.uniform(float(min_sizeEntry.get()), float(max_sizeEntry.get()))
                    size_x = math.floor(resolution[0] * size)
                    size_y = math.floor(resolution[1] * size)
                    pos_x = random.randrange(0,resolution[0]-size_x)
                    pos_y = random.randrange(0,resolution[1]-size_y)

                    Create_Image(image, img_number, pos_x, pos_y, size_x, size_y)
                    bnd_box = get_new_bnd(xml_name, pos_x, pos_y, size_x, size_y, resolution[0], resolution[1])
                    Create_XML_File(directory + xml_name, image, bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3], img_number)

                    #info
                    infoLabel.config(text="Created " + str(total_images) + " images", fg="green")




    except Exception as e:
        infoLabel.config(text=e, fg="red")



folderLabel = Label(root, text="Folder:")
folderLabel.grid(row=0, column=0,  pady=10, sticky=E)

folderEntry = Entry(root, width=70)
folderEntry.grid(row=0, column=1, columnspan=3)
folderEntry.bind("<Return>", update_vars)

folderButton = Button(root, text="Select Folder", command=directory_button)
folderButton.grid(row=0, column = 4)



optionsLabel = Label(root, text="Options:")
optionsLabel.grid(row=1, column=0, pady=(20,10))

new_imageLabel = Label(root, text="Number of New Images")
new_imageLabel.grid(row=2, column=0, sticky=E)

min_sizeLabel = Label(root, text="Minimum size")
min_sizeLabel.grid(row=3, column=0, sticky=E)

max_sizeLabel = Label(root, text="Maximum size")
max_sizeLabel.grid(row=4, column=0, sticky=E)


new_imageEntry = Entry(root)
new_imageEntry.grid(row=2, column=1)

min_sizeEntry = Entry(root)
min_sizeEntry.grid(row=3, column=1)

max_sizeEntry = Entry(root)
max_sizeEntry.grid(row=4, column=1)



base_nameLabel = Label(root, text="Base Name")
base_nameLabel.grid(row=2, column=2, sticky=E)


starting_numberLabel = Label(root, text="Starting Number")
starting_numberLabel.grid(row=3, column=2, sticky=E, padx=(20,5))


base_nameEntry = Entry(root)
base_nameEntry.grid(row=2, column=3)

starting_numberEntry = Entry(root)
starting_numberEntry.grid(row=3, column=3)


infoLabel = Label(root, text="Hover over field for info", fg="grey", bg="light gray", width=80, height=5, anchor=NW, justify=LEFT)
infoLabel.grid(row=5, column=0, columnspan=4, padx=(20,10), pady=(80,0))


submit_button = Button(root, text="Create Images", bg="light green", command=submit_button)
submit_button.grid(row=6, column=4, pady=(30, 10), padx=(0,10))



#info label
folderLabel.bind("<Enter>", lambda x: infoLabel.config(text="Directory of images to create occluded images from.", fg="black"))
folderLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

folderEntry.bind("<Enter>", lambda x: infoLabel.config(text="Directory of images to create occluded images from.", fg="black"))
folderEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

base_nameLabel.bind("<Enter>", lambda x: infoLabel.config(text="Name of base image. \n(e.g. if images are named object0001.jpg, then base name is object)", fg="black"))
base_nameLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

base_nameEntry.bind("<Enter>", lambda x: infoLabel.config(text="Name of base image. \n(e.g. if images are named object0001.jpg, then base name is object)", fg="black"))
base_nameEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

starting_numberLabel.bind("<Enter>", lambda x: infoLabel.config(text="The number the new images should begin at. \n(e.g. if the last image is object1296.jpg, then the starting number should be 1297)", fg="black"))
starting_numberLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

starting_numberEntry.bind("<Enter>", lambda x: infoLabel.config(text="The number the new images should begin at. \n(e.g. if the last image is object1296.jpg, then the starting number should be 1297)", fg="black"))
starting_numberEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

new_imageLabel.bind("<Enter>", lambda x: infoLabel.config(text="The number of occluded images to be created from each base image.", fg="black"))
new_imageLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

new_imageEntry.bind("<Enter>", lambda x: infoLabel.config(text="The number of occluded images to be created from each base image.", fg="black"))
new_imageEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

min_sizeLabel.bind("<Enter>", lambda x: infoLabel.config(text="Minimum size of occluded image in percent.", fg="black"))
min_sizeLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

min_sizeEntry.bind("<Enter>", lambda x: infoLabel.config(text="Minimum size of occluded image in percent.", fg="black"))
min_sizeEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

max_sizeLabel.bind("<Enter>", lambda x: infoLabel.config(text="Maximum size of occluded image in percent.", fg="black"))
max_sizeLabel.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

max_sizeEntry.bind("<Enter>", lambda x: infoLabel.config(text="Maximum size of occluded image in percent.", fg="black"))
max_sizeEntry.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

submit_button.bind("<Enter>", lambda x: infoLabel.config(text="Create " + str(image_count()) +  " images. \nThis will take ~" + str(image_time(image_count())) + " minute(s).", fg="green"))
submit_button.bind("<Leave>", lambda x: infoLabel.config(text="Hover over field for info", fg="grey"))

def image_count():
    try:
        directory = folderEntry.get()
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        base_image_count = 0
        for i in files:
            if(i[i.rfind("."):] in extenstions):
                base_image_count += 1

        return int(new_imageEntry.get()) * base_image_count
    except:
        return 0

def image_time(n):
    return int(math.ceil(n * .0006))

root.mainloop()
