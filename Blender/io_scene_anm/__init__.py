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
    "name": "image space incorporated ANM Format",
    "author": "Evilclip",
    "version": (1, 0, 2),
    "blender": (3, 0, 0),
    "location": "File > Import",
    "description": "Import/Export ANM file",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_anm" in locals():
        importlib.reload(import_anm)
    if "export_anm" in locals():
        importlib.reload(export_anm)

@orientation_helper(axis_forward='Y', axis_up='Z')
class Importanm(bpy.types.Operator, ImportHelper):
    """Import from anm file format (.anm)"""
    bl_idname = "import_scene.isi_anm"
    bl_label = 'Import ANM'
    bl_options = {'UNDO'}

    filename_ext = ".anm"
    filter_glob: StringProperty(default="*.anm", options={'HIDDEN'})

    def execute(self, context):
        from . import import_anm
        return import_anm.load(self, context)

class Exportanm(bpy.types.Operator, ImportHelper):
    """Export to anm file format (.anm)"""
    bl_idname = "export_scene.isi_anm"
    bl_label = 'Export anm'
    bl_options = {'UNDO'}

    filename_ext = ".anm"
    filter_glob: StringProperty(default="*.anm", options={'HIDDEN'})

    def execute(self, context):
        from . import export_anm
        return export_anm.save(self, context)


# Add to a menu
def menu_func_import(self, context):
    self.layout.operator(Importanm.bl_idname, text="ISI (.anm)")

def menu_func_export(self, context):
    self.layout.operator(Exportanm.bl_idname, text="ISI (.anm)")


def register():
    bpy.utils.register_class(Importanm)
    bpy.utils.register_class(Exportanm)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(Importanm)
    bpy.utils.unregister_class(Exportanm)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
