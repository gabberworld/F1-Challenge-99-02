# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
)
import bpy
bl_info = {
    "name": "image space incorporated AIW Format",
    "author": "Evilclip",
    "version": (1, 0, 5),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "description": "Import AIW",
    "category": "Import",
}

if "bpy" in locals():
    import importlib
    if "import_aiw" in locals():
        importlib.reload(import_aiw)

@orientation_helper(axis_forward='Y', axis_up='Z')
class ImportAIW(bpy.types.Operator, ImportHelper):
    """Import from AIW file format (.aiw)"""
    bl_idname = "import_scene.isi_aiw"
    bl_label = 'Import AIW'
    bl_options = {'UNDO'}

    filename_ext = ".aiw"
    filter_glob: StringProperty(default="*.aiw", options={'HIDDEN'})

    def execute(self, context):
        from . import import_aiw


        return import_aiw.load(self, context)


# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(ImportAIW.bl_idname, text="ISI (.aiw)")


def register():
    bpy.utils.register_class(ImportAIW)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportAIW)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
