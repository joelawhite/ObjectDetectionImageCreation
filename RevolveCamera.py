import bpy

from math import pi, radians

bl_info = {
    "name": "Automated Camera Rotation",
    "category": "Object",
    "author": "Joel White/Jack Hurley",
    "version": (1, 0, 0),
    "blender": (2,80,0),
    "location": "Object > Create Automated Camera Rotation"
}

def createRotation(distance, horizontalSteps, verticalSteps, isHalfRotation):

    #create camera and CameraPath to rotate camera around
    bpy.ops.object.camera_add(location=(0,0,distance), align='VIEW', rotation=(0,0,0))
    camera = bpy.context.object 
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    CameraPath = bpy.context.object
    CameraPath.name = "Camera Rotator"
    camera.parent = CameraPath
    camera.matrix_parent_inverse = CameraPath.matrix_world.inverted()


    #Top frame
    bpy.context.scene.frame_set(0)                          #set keyframe
    CameraPath.rotation_euler = (0,0,0)                     #rotate camera
    CameraPath.keyframe_insert(data_path="rotation_euler")  #add keyframe


    #loop for vertical rotation
    for i in range(verticalSteps - 1):

        #beginning keyframe
        bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)            #set keyframe
        CameraPath.rotation_euler = (radians((180/verticalSteps) * (i + 1)),0,0)    #rotate camera
        CameraPath.keyframe_insert(data_path="rotation_euler")                      #add keyframe

        #ending keyframe
        bpy.context.scene.frame_set(bpy.context.scene.frame_current + horizontalSteps - 1)                          #set keyframe
        if(not isHalfRotation):
            CameraPath.rotation_euler = (radians((180/verticalSteps) * (i + 1)),0,radians(360 - (360/horizontalSteps))) #rotate camera
        else:
            CameraPath.rotation_euler = (radians((180/verticalSteps) * (i + 1)),0,radians(360 - (360/horizontalSteps))/2) #rotate camera
        CameraPath.keyframe_insert(data_path="rotation_euler")                                                      #add keyframe



    #Bottom frame
    bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)    #set keyframe
    CameraPath.rotation_euler = (pi,0,0)                                #rotate camera
    CameraPath.keyframe_insert(data_path="rotation_euler")              #add keyframe

    #set frame length to total length
    bpy.context.scene.frame_end = (bpy.context.scene.frame_current)
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_set(0)

    #make all animations linear
    fcurves = CameraPath.animation_data.action.fcurves
    for fcurve in fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'


class CameraRotation(bpy.types.Operator):
    """Create camera rotation animation"""          #tooltip for menu items and buttons.
    bl_idname = "object.automated_camera_rotation"  # Unique identifier for buttons and menu items to reference.
    bl_label = "Create Automated Camera Rotation"   # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}               # Enable undo for the operator.
    
    distance = bpy.props.FloatProperty(name="Distance", default=5, soft_min=0)
    horizontalSteps = bpy.props.IntProperty(name="Horizontal Steps", default=24, min=1)
    verticalSteps = bpy.props.IntProperty(name="Vertical Steps", default=12, min=1)
    isHalfRotation = bpy.props.BoolProperty(name="Use Half Rotation", default=False)

    def draw(self, context):
        layout = self.layout
        
        layout.prop(self, "distance")
        layout.separator()
        if(self.isHalfRotation):
            layout.label(text="Horizontal Angle: " + str(round(180/self.horizontalSteps, 3)))
        else:
            layout.label(text="Horizontal Angle: " + str(round(360/self.horizontalSteps, 3)))
        
        layout.prop(self, "horizontalSteps")
        layout.separator()
        layout.label(text="Verical Angle: " + str(round(180/self.verticalSteps,3)))
        layout.prop(self, "verticalSteps")
        layout.separator()
        layout.prop(self, "isHalfRotation")

    
    def execute(self, context):        # execute() is called when running the operator.

        # The original script

        createRotation(self.distance,self.horizontalSteps,self.verticalSteps, self.isHalfRotation)

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.



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
    self.layout.operator(CameraRotation.bl_idname)


classes = (CameraRotation,)


def register():
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_object.append(menu_func)
    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

 
# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()











