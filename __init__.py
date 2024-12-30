'''
Copyright (C) 2024 VOLNO
https://github.com/V0ln0

Created by Volno

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Warning: this is both my first Blender addon and my first "big" project in Python
# also I am dyslexic, typos abound
import bpy

from . Skeleton_Manager import *
from . Skeleton_Closet import *
from . LazyTalior_Prop import *
from . LazyTalior_UI_Icons import *



bl_info = {
    "name": "BG3 Lazy Tailor(BETA)",
    "description": "A tool aimed at making the proccsess of refiting outfits for various races/bodytypes for use in Baldur's Gate 3 easier.",
    "author": "Volno",
    "version": (0, 1, 2),
    "blender": (4, 0, 0),
    "location": "Scene > Properties > BG3LazyTailor Tools tab",
    "warning": "baby's first Blender addon",
    "wiki_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Meshes"
    }

class LT_PT_LazyPanelMain(bpy.types.Panel):
    bl_label = "BG3 Lazy Talior"
    bl_idname = "LT_PT_LazyPanelMain"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_category = "Lazy Talior"

    def draw(self, context):
        layout = self.layout
        props = context.scene.tailor_props
        row = layout.row(align=True)
        if props.InitBool == False:
            row.label(text="Lazy Talior Status: NOT READY ", icon='RADIOBUT_OFF')
            layout.operator("lt.initialise",
                text="Initialise")
        else:
            row.label(text="Lazy Talior Status: READY ", icon='RADIOBUT_ON')
            layout.prop(props, "from_body")
            layout.operator("lt.set_base_tailor")
            layout.prop(props, "to_body")
            layout.operator("lt.defualt_preset_tailor")
            layout.operator("lt.mannequin_reset")
            # layout.prop_search(props, "user_action", context.blend_data, "actions") #figure out a way to search for specifc names


class LT_PT_mannequin_vis(bpy.types.Panel):
    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BG3 LT"
    bl_label = 'Mannequin'
    bl_context = 'posemode'

    def draw(self, context):
        # tailor_props = bpy.context.scene.tailor_props
        # lt_obj = context.active_object
        # if lt_obj is bpy.data.objects[tailor_props.mannequin_form]:
        #     if context.mode == 'EDIT_ARMATURE':

        layout = self.layout
        row = layout.row(align=True)
        row.label(text="Fuck Bitches Get Money", icon='RADIOBUT_ON')

# class VIEW3D_PT_view3d_properties(Panel):
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'UI'
#     bl_category = "View"
#     bl_label = "View"

classes = (
    
    LT_PT_LazyPanelMain,
    LT_OT_initialise,
    LT_OT_defualt_preset_tailor,
    tailor_props,
    LT_OT_mannequin_reset,
    LT_OT_set_base_tailor,
    LT_PT_mannequin_vis,

    )

def register():


    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.tailor_props = bpy.props.PointerProperty(type=tailor_props)

def unregister():

    del bpy.types.Scene.tailor_props
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()

