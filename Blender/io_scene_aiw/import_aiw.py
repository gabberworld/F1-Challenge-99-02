import bpy
import re

def point_cloud(ob_name, coords, edges=[], faces=[]):
    me = bpy.data.meshes.new(ob_name)
    ob = bpy.data.objects.new(ob_name, me)
    me.from_pydata(coords, edges, faces)
    ob.show_name = False
    me.update()
    return ob

def readaiw(context, filepath):
    f = open(filepath, 'r', encoding='ansi')
    
    filen = re.search("^.*[(/|\\\\|\\)](.*)\.(.*)$", filepath)
    
    if filen:
       filen = filen[1]
    else:
       filen = "TrackCurve" 
         
    Lines = f.readlines()
    
    vertcount = 0
    pitlanevertcount = 0
    garagecount = 0
    gridcount = 0
    
    aiw_data = []
    aiw_data_fast = []
    aiw_data_pitlane = []
    aiw_data_garage = []
    aiw_data_grid = []
    
    dwp_pos = namedtuple('dwp_pos', ['y', 'z', 'x'])
    dwp_perp = namedtuple('dwp_perp', ['y', 'z', 'x'])
    dwp_width = namedtuple('dwp_width', ['left', 'rigth', 'far_left','far_right'])
    dwp_path = namedtuple('dwp_path', ['fast', 'wet'])
    dwp_branchID = 0     
    
    for line in Lines:
        lis = line.strip()
        
        wp_pos          = re.search('^wp_pos\=\((.*?)\,(.*?)\,(.*?)\)', lis,  re.IGNORECASE)
        wp_perp         = re.search('^wp_perp\=\((.*?)\,(.*?)\,(.*?)\)', lis, re.IGNORECASE)
        wp_branchID     = re.search('^wp_branchID\=\((.*?)\)', lis, re.IGNORECASE)
        WP_PTRS         = re.search('^wp_ptrs\=\((.*?)\,(.*?)\,(.*?)\,(.*?)\)', lis, re.IGNORECASE) 
        wp_path         = re.search('^wp_path\=\((.*?)\,(.*?)', lis, re.IGNORECASE)    
        
        if wp_pos:
            d = dwp_pos(wp_pos[1],wp_pos[2],wp_pos[3]) 
        elif wp_perp:
            pd = dwp_perp(wp_perp[1],wp_perp[2],wp_perp[3])                         
        elif wp_branchID:
            dwp_branchID = wp_branchID[1]
        elif wp_path:
             sfp= dwp_path(wp_path[1],wp_path[2])                   
        elif WP_PTRS:
            if dwp_branchID == '0':
              vertcount += 1    
              cords = (float(d.y)+float(pd.y), float(d.x)+float(pd.x), float(d.z)+float(pd.z))
              aiw_data.append(cords)
              cordsf = (float(d.y)+float(pd.y)*float(sfp.fast), float(d.x)+float(pd.x)*float(sfp.fast), float(d.z)+float(pd.z)*float(sfp.fast))
              aiw_data_fast.append(cordsf) 
            if dwp_branchID == '1':
              pitlanevertcount += 1    
              cords = (float(d.y)+float(pd.y), float(d.x)+float(pd.x), float(d.z)+float(pd.z))
              aiw_data_pitlane.append(cords)
            if int(dwp_branchID) > 105:
              garagecount += 1    
              cords = (float(d.y)+float(pd.y), float(d.x)+float(pd.x), float(d.z)+float(pd.z))
              aiw_data_garage.append(cords) 
            if int(dwp_branchID) > 1 and int(dwp_branchID) < 106:
              gridcount += 1    
              cords = (float(d.y)+float(pd.y), float(d.x)+float(pd.x), float(d.z)+float(pd.z))
              aiw_data_grid.append(cords)               
                                                       
    f.close()

    if vertcount == 0:    
     ShowMessageBox("failed read WP_PTRS data", "WP_PTRS", 'ERROR')
     return {'FINISHED'}
    
    saved_location = bpy.context.scene.cursor.location.xyz
    bpy.context.scene.cursor.location =(0.0,0.0,0.0)
    
    aiw_coll = bpy.data.collections.new(filen)
    bpy.context.scene.collection.children.link(aiw_coll)

   # Pitlane
    
    if pitlanevertcount > 0:
     
     edges2 = []    
     
     for i in range(pitlanevertcount-1):
       ce = i;
       ne = i+1;
       edges2.append((ce,ne))
     
     oo2 = point_cloud(filen+"_pitlane",aiw_data_pitlane,edges2,[])
     
     aiw_coll.objects.link(oo2)
     oo2.select_set(True) 
  #  bpy.data.objects[oo2.name].select_set(state = True, view_layer = bpy.context.view_layer)
     bpy.context.view_layer.objects.active = oo2
     bpy.ops.object.convert(target='CURVE')
     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
     
    # Track
     
    if vertcount > 0:
     
     edges3 = []
     
     for i in range(vertcount-1):
        ce = i;
        ne = i+1;
        edges3.append((ce,ne))
     edges3.append((vertcount-1,0))
     
     oo4 = point_cloud(filen+"_track_fastline",aiw_data_fast,edges3,[])
     
     aiw_coll.objects.link(oo4)
     oo4.select_set(True) 
   # bpy.data.objects[oo4.name].select_set(state = True, view_layer = bpy.context.view_layer)
     bpy.context.view_layer.objects.active = oo4
     bpy.ops.object.convert(target='CURVE')
     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
     
    #
     
    # Track
     
     edges = []
     
     for i in range(vertcount-1):
        ce = i;
        ne = i+1;
        edges.append((ce,ne))
     edges.append((vertcount-1,0))
     
     oo = point_cloud(filen+"_track",aiw_data,edges,[])
     
     aiw_coll.objects.link(oo)
     oo.select_set(True) 
     bpy.data.objects[oo.name].select_set(state = True, view_layer = bpy.context.view_layer)
     bpy.context.view_layer.objects.active = oo
     bpy.ops.object.convert(target='CURVE')
     bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    
    #
    
    oo3 = point_cloud(filen+"_pitstop",aiw_data_garage,[],[])    
    aiw_coll.objects.link(oo3)
    oo3.select_set(True)
    
    # 
    
    oo4 = point_cloud(filen+"_grid",aiw_data_grid,[],[])    
    aiw_coll.objects.link(oo4)
    oo4.select_set(True) 
    
    
    bpy.context.scene.cursor.location.xyz = saved_location  


from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from collections import namedtuple

def load(self, context):

    readaiw(context, self.filepath)
    return {'FINISHED'}

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)


