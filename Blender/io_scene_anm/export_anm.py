import bpy
import struct
import random

def saveanm(context, filepath):
    HEADER_FMT = "<16sifii"
    FILEHEADER_FMT = "<36si"
    CORDDATA_FMT = "<8f"
    MAX_NAME_LEN = 12 
    
    obj = bpy.context.active_object
    action = obj.animation_data.action
    start_frame = bpy.context.scene.frame_start
    end_frame = bpy.context.scene.frame_end
    
    with open(filepath, "wb") as f:
        
        # Header
        version = ("Blender%06d" % random.randint(0, 999999)).encode("ascii")
        version = version.ljust(16, b"\x00")

        dunnod = 1 #default is 1
        speed = float(action.get("Speed", 1.0))
        unknown = 0
        file_count = 1 # as we currently don't support different animation then it's 1 as default

        f.write(struct.pack(HEADER_FMT,version,dunnod,speed,unknown,file_count))

        name = obj.name[:MAX_NAME_LEN]

        # Example FileHeader
        name_bytes = name.encode("ascii")[:35]
        name_bytes = name_bytes.ljust(36, b"\x00")

        record_count = end_frame - start_frame + 1

        f.write(struct.pack(FILEHEADER_FMT, name_bytes, record_count))

        for frame in range(start_frame, end_frame + 1):
            bpy.context.scene.frame_set(frame)

            x = obj.location.x
            y = obj.location.y
            z = obj.location.z

            q = obj.rotation_quaternion

            rot_w = q.w
            rot_x = q.x
            rot_y = q.y
            rot_z = q.z

            f.write(struct.pack(CORDDATA_FMT,float(frame),x,z,y,rot_x,rot_z,rot_y,rot_w,))    


from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from collections import namedtuple

def save(self, context):
    saveanm(context, self.filepath)
    return {'FINISHED'}

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


