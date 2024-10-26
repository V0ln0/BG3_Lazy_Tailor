import bpy
from . Skeleton_Manager import *

bl_info = {
        "name": "BG3 Lazy Tailor",
        "description": "A tool aimed at making the proccsess of refiting outfits for various races/bodytypes for use in Baldur's Gate 3 easier.",
        "author": "Volno",
        "version": (1, 0, 0),
        "blender": (4, 2, 2),
        "location": "Pose Mode > Sidebar > BG3LazyTailor Tools tab",
        "warning": "baby's first Blender addon",
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "3D View"
        }







class LazyTailorPanelMain(bpy.types.Panel):
    bl_label = "BG3 Lazy Talior"
    bl_idname = "OBJECT_PT_lazytalior"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lazy Talior"

    
    def draw(self, context):
        layout = self.layout

        obj = context.object
        
        row = layout.row()
        row.label(text="Hello world!", icon='WORLD_DATA')

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.operator("mesh.primitive_cube_add")

def register():
    bpy.utils.register_class(LazyTailorPanelMain)


def unregister():
    bpy.utils.unregister_class(LazyTailorPanelMain)

if __name__ == "__main__":
    register()
