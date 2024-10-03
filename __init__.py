import bpy

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

import bpy

from . LAZY_BoneManager import LAZY_BoneManager

class LazyTailorPanel(bpy.types.Panel):
    bl_label = "BG3 Lazy Tailor"
    bl_idname = "POSE_PT_LazyTailor"
    bl_category = "LazyTailor"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "posemode"

    def draw(self, context):
        layout = self.layout
        layout.operator("view3d.LAZY_BoneManager")

def register():
    bpy.utils.register_class(LazyTailorPanel)
    bpy.utils.register_class(LAZY_BoneManager)


def unregister():
    bpy.utils.unregister_class(LazyTailorPanel)
    bpy.utils.unregister_class(LAZY_BoneManager)


if __name__ == "__main__":
    register()

