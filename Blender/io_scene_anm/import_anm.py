import bpy
import struct

HEADER_FMT = "<16sifii"
FILEHEADER_FMT = "<36si"
CORDDATA_FMT = "<8f"

HEADER_SIZE = struct.calcsize(HEADER_FMT)
FILEHEADER_SIZE = struct.calcsize(FILEHEADER_FMT)
CORDDATA_SIZE = struct.calcsize(CORDDATA_FMT)

def readanm(context, filepath):
    with open(filepath, "rb") as f:
    
        # Read Header
        version,dunnod,speed,unknown,file_count = struct.unpack(HEADER_FMT, f.read(HEADER_SIZE))
        
        for i in range(file_count):
           # Read FileHeader
            name_bytes, record_count = struct.unpack(FILEHEADER_FMT,f.read(FILEHEADER_SIZE))
            name = name_bytes.split(b"\x00")[0].decode("ascii", errors="ignore") 
            
            localScene = bpy.context.scene
            
            mesh = bpy.data.meshes.new(name)
            obj = bpy.data.objects.new(name, mesh)
            bpy.context.collection.objects.link(obj)
            obj.rotation_mode = 'QUATERNION'        

            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
           
            for j in range(record_count):

                values = struct.unpack(CORDDATA_FMT,f.read(CORDDATA_SIZE))

                data1, dataLX, dataLZ, datalY, dataQX, dataQZ, dataQY, dataQW = values
                
                obj.location = (dataLX, datalY, dataLZ)
                obj.rotation_quaternion = (dataQW,dataQX,dataQY,dataQZ)
                
                obj.keyframe_insert(data_path="location", frame=j)  
                obj.keyframe_insert(data_path="rotation_quaternion",frame=j)
                

            action = obj.animation_data.action 
            if action:
                action["Speed"] = speed               


            bpy.context.scene.frame_end = record_count
            bpy.context.scene.frame_set(0)   


    bpy.context.view_layer.update()


from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from collections import namedtuple

def load(self, context):

    readanm(context, self.filepath)
    return {'FINISHED'}

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


