import bpy
import math
import sys
import platform
import random
import os.path
from mathutils import Vector
import xml.etree.cElementTree as ET

bl_info = {
    "name": "Create Pascal VOC xml",
    "category": "Object",
    "author": "Joel White",
    "version": (1, 0, 0),
    "blender": (2,80,0),
    "location": "Object>Create Pascal VOC xml"
}

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


#converts world coord to pixel coord
def World_To_Screen_Coord(
        world_point,
        camera_to_world,
        canvas_width,
        canvas_height,
        image_width,
        image_height):
    
    world_to_camera = camera_to_world.inverted()
    camera_point = world_to_camera @ world_point
    
    canvas_point = {}
    canvas_point[0] = camera_point.x / -camera_point.z
    canvas_point[1] = camera_point.y / -camera_point.z
    
    normalized_point = {}
    normalized_point[0] = (canvas_point[0] + canvas_width / 2) / canvas_width
    normalized_point[1] = (canvas_point[1] + canvas_height / 2) / canvas_height
    
    
    image_point = {}
    image_point[0] = math.floor(normalized_point[0] * image_width)
    image_point[1] = math.floor((1 - normalized_point[1]) * image_height)
    
    return image_point




#creates xml file for each image in current animation timeline
def Create_XML_File(p_filepath, p_database, p_segmented, p_pose, p_truncated, p_difficult, p_occluded, file_number, bndbox_list, test_numbers, file_extension, obj_list, resolution_x, resolution_y):
    
    is_test = False
    if int(file_number) in test_numbers:
        is_test = True
        
    
    if sys.platform.startswith('win'):
        if is_test:
            image_name = p_filepath[p_filepath.rfind("\\")+1:] + file_number
            file_path = p_filepath[:p_filepath.rfind("\\")] + "\\testing\\" + image_name
            folder_name = "testing"
        else:
            image_name = p_filepath[p_filepath.rfind("\\")+1:] + file_number
            file_path = p_filepath[:p_filepath.rfind("\\")] + "\\training\\" + image_name
            folder_name = "training"
    else:
        if is_test:
            image_name = p_filepath[p_filepath.rfind("/")+1:] + file_number
            file_path = p_filepath[:p_filepath.rfind("/")] + "/testing/" + image_name
            folder_name = "testing"
        else:
            image_name = p_filepath[p_filepath.rfind("/")+1:] + file_number
            file_path = p_filepath[:p_filepath.rfind("/")] + "/training/" + image_name
            folder_name = "training"
            
    
    root = ET.Element("annotation")
    folder = ET.SubElement(root, "folder").text = folder_name
    filename = ET.SubElement(root, "filename").text = image_name
    path = ET.SubElement(root, "path").text = file_path + file_extension
    source = ET.SubElement(root, "source")
    database = ET.SubElement(source, "database").text = p_database

    size = ET.SubElement(root, "size")
    width = ET.SubElement(size, "width").text = str(resolution_x)[:-2]
    height = ET.SubElement(size, "height").text = str(resolution_y)[:-2]
    depth = ET.SubElement(size, "depth").text = "3"

    segmented = ET.SubElement(root, "segmented").text = p_segmented

    for i in range(len(obj_list)):
        object = ET.SubElement(root, "object")
        name = ET.SubElement(object, "name").text = obj_list[i].name
        pose = ET.SubElement(object, "pose").text = p_pose
        truncated = ET.SubElement(object, "truncated").text = p_truncated
        difficult = ET.SubElement(object, "difficult").text = p_difficult
        occluded = ET.SubElement(object, "occluded").text = p_occluded
        bndbox = ET.SubElement(object, "bndbox")
        xmin = ET.SubElement(bndbox, "xmin").text = str(bndbox_list[i][0])
        xmax = ET.SubElement(bndbox, "xmax").text = str(bndbox_list[i][1])
        ymin = ET.SubElement(bndbox, "ymin").text = str(bndbox_list[i][2])
        ymax = ET.SubElement(bndbox, "ymax").text = str(bndbox_list[i][3])

    tree = ET.ElementTree(root)
    tree.write(file_path + ".xml")
    
    print("Created " + file_path + ".xml")




def Move_Images(p_filepath, test_numbers, file_extension):
    
    for i in range(bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1):
        number = ""
        if(i < 10000):
            number = f'{i:04}'
        else:
            number = str(file_number)
            
        if sys.platform.startswith('win'):
            if i in test_numbers:
                image_name = p_filepath[p_filepath.rfind("\\")+1:] + number
                file_path = p_filepath[:p_filepath.rfind("\\")] + "\\testing\\" + image_name
                os.rename(p_filepath + number + file_extension, file_path + file_extension)
            else:
                image_name = p_filepath[p_filepath.rfind("\\")+1:] + number
                file_path = p_filepath[:p_filepath.rfind("\\")] + "\\training\\" + image_name
                os.rename(p_filepath + number + file_extension, file_path + file_extension)
        else:
            if i in test_numbers:
                image_name = p_filepath[p_filepath.rfind("/")+1:] + number
                file_path = p_filepath[:p_filepath.rfind("/")] + "/testing/" + image_name
                os.rename(p_filepath + number + file_extension, file_path + file_extension)
            else:
                image_name = p_filepath[p_filepath.rfind("/")+1:] + number
                file_path = p_filepath[:p_filepath.rfind("/")] + "/training/" + image_name
                os.rename(p_filepath + number + file_extension, file_path + file_extension)
    


def Main_Function(p_filepath, p_database, p_segmented, p_pose, p_truncated, p_difficult, p_occluded, p_training_percent):

    #set scene vars
    obj_list = bpy.context.selected_objects
    resolution_x = bpy.context.scene.render.resolution_x * (bpy.context.scene.render.resolution_percentage/100)
    resolution_y = bpy.context.scene.render.resolution_y * (bpy.context.scene.render.resolution_percentage/100)
    camera = bpy.context.scene.camera
    
    if(bpy.context.scene.render.image_settings.file_format == 'TIFF'):
        file_extension = ".tif"
    if(bpy.context.scene.render.image_settings.file_format == 'PNG'):
        file_extension = ".png"
    if(bpy.context.scene.render.image_settings.file_format == 'BMP'):
        file_extension = ".bmp"
    if(bpy.context.scene.render.image_settings.file_format == 'JPEG'):
        file_extension = ".jpg"
    if(bpy.context.scene.render.image_settings.file_format == 'TARGA'):
        file_extension = ".tga"
    if(bpy.context.scene.render.image_settings.file_format == 'OPEN_EXR'):
        file_extension = ".exr"


    #create folders
    # Create target Directory if don't exist
    if sys.platform.startswith('win'):
        filepath = p_filepath  #full path, no extension
        image_name = filepath[filepath.rfind("\\")+1:]              #name
        folder_name = filepath[:-len(image_name) - 1]               #remove image name
        
        if not os.path.exists(folder_name + "\\training"):
            os.mkdir(folder_name + "\\training")
            print("Directory ", folder_name + "\\training",  " Created ")
        else:    
            print("Directory ", folder_name + "\\training",  " already exists")
            
        if not os.path.exists(folder_name + "\\testing"):
            os.mkdir(folder_name + "\\testing")
            print("Directory ", folder_name + "\\testing",  " Created ")
        else:    
            print("Directory ", folder_name + "\\testing",  " already exists")
    else:
        filepath = p_filepath  #full path, no extension
        image_name = filepath[filepath.rfind("/")+1:]               #name
        folder_name = filepath[:-len(image_name) - 1]               #remove image name
        
        if not os.path.exists(folder_name + "/training"):
            os.mkdir(folder_name + "/training")
            print("Directory ", folder_name + "/training",  " Created ")
        else:    
            print("Directory ", folder_name + "/training",  " already exists")
            
        if not os.path.exists(folder_name + "/testing"):
            os.mkdir(folder_name + "/testing")
            print("Directory ", folder_name + "/testing",  " Created ")
        else:    
            print("Directory ", folder_name + "/testing",  " already exists")

    
    #select random files for training/testing
    test_numbers = []
    for i in range(int((bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1) * ((100 - p_training_percent)/100))):
        num = -1
        while True:
            num = random.randrange(bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1)
            if not (num in test_numbers):
                break
            
        test_numbers.append(num)


    c_width = 2 * math.tan(camera.data.angle/2)
    c_height = c_width * (resolution_y/resolution_x)


    #convert local coords to world coords
    world_vertices = []
    for i in range(len(obj_list)):
    
        obj_vertices = []
        for k in range(len(obj_list[i].data.vertices)):
            obj_vertices.append(obj_list[i].matrix_world @ obj_list[i].data.vertices[k].co)
    
        world_vertices.append(obj_vertices)



    #create xml files for each frame
    for i in range(bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1):

        bpy.context.scene.frame_set(i)
    
        bndbox_list = [] #list of x/y min/max

        for k in range(len(obj_list)):
        
            #initilize vars
            x_min = sys.maxsize
            x_max = -sys.maxsize - 1
            y_min = sys.maxsize
            y_max = -sys.maxsize - 1
        
        
            #find min/max x/y
            min_max_list = []
            for x in range(len(world_vertices[k])):
    
                pos = World_To_Screen_Coord(world_vertices[k][x], camera.matrix_world, c_width, c_height, resolution_x, resolution_y)
     
                if(pos[0] < x_min):
                    x_min = pos[0]
                if(pos[0] > x_max):
                    x_max = pos[0]
                if(pos[1] < y_min):
                    y_min = pos[1]
                if(pos[1] > y_max):
                    y_max = pos[1]
                
                min_max_list = [x_min,x_max,y_min,y_max]
        
            bndbox_list.append(min_max_list)
        

    
        file_number = i + bpy.context.scene.frame_start;
        if(file_number < 10000):
            file_number = f'{file_number:04}'
        else:
            file_number = str(file_number)
    
        Create_XML_File(p_filepath, p_database, p_segmented, p_pose, p_truncated, p_difficult, p_occluded, file_number, bndbox_list, test_numbers, file_extension, obj_list, resolution_x, resolution_y);
    
    try:
        Move_Images(p_filepath, test_numbers, file_extension)
    except:
        ShowMessageBox("Unable to move images into 'training'/'testing' folders", "Pascal VOC xml Warning", 'ERROR')




class VOCxml(bpy.types.Operator):
    """Create Pascal VOC xml Files"""
    bl_idname = "object.pascal_voc_xml"
    bl_label = "Create Pascal VOC xml Files"
    bl_options = {'REGISTER', 'UNDO'}
    
    training_percentage = bpy.props.FloatProperty(name="Training Percentage", subtype="PERCENTAGE", precision=1, min=0, max=100, default=80)
    filepath = bpy.props.StringProperty(name="File Path", subtype="FILE_PATH", options={"HIDDEN"})
    database = bpy.props.StringProperty(name="Database", default="Unspecified")
    segmented = bpy.props.StringProperty(name="Segmented", default="0")
    pose = bpy.props.StringProperty(name="Pose", default="Unspecified")
    truncated = bpy.props.StringProperty(name="Truncated", default="0")
    difficult = bpy.props.StringProperty(name="Difficult", default="0")
    occluded = bpy.props.StringProperty(name="Occluded", default="0")
    
    @classmethod
    def poll(cls, context):
        return context.object.select_get() and context.object.type == 'MESH'
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        #return context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        print("PATH: " + self.filepath)
        print("DATABASE: " + self.database)
        print("SEGMENTED: " + self.segmented)
        print("POSE: " + self.pose)
        print("TRUNCATED: " + self.truncated)
        print("DIFFICULT: " + self.difficult)
        print("OCCLUDED: " + self.occluded)
        Main_Function(self.filepath, self.database, self.segmented, self.pose, self.truncated, self.difficult, self.occluded, self.training_percentage)
        return {'FINISHED'}
    
    

# function to convert 2.7x code to work without warnings in 2.8x
def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


def menu_func(self, context):
    self.layout.operator(VOCxml.bl_idname)
    
    
classes = (VOCxml,)


def register():
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)
        
    bpy.types.VIEW3D_MT_object.append(menu_func)

    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)






if __name__ == "__main__":
    register()