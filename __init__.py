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
import os
import bpy.utils.previews

from . Skeleton_Manager import *
from . Skeleton_Closet import *
from . LazyTalior_Prop import *
from . LazyTalior_UI_Icons import *



bl_info = {
    "name": "BG3 Lazy Tailor",
    "description": "A tool aimed at making the proccsess of refiting outfits for various races/bodytypes for use in Baldur's Gate 3 easier.",
    "author": "Volno",
    "version": (1, 0, 0),
    "blender": (4, 2, 3),
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
        pcoll = preview_collections["main"]

        row = layout.row(align=True)
        my_icon = pcoll["my_icon"]
        # todo: bool that stops people from pressing this more than once. it is fine for now
        # LableText = ("Currently converting ") + (tailor_props.bc_from) + (", to ") + (tailor_props.bc_to) + (".")
        
        props = context.scene.tailor_props
        layout.prop(props, "from_body")
        layout.prop(props, "to_body")
        row = layout.row()
        layout.operator("lt.defualt_preset_tailor")
        layout.operator("lt.mannequin_reset")
class LT_PT_InitPanel(bpy.types.Panel):
    
    bl_label = "Lazy Talior Supply Closet"
    bl_idname = "LT_PT_InitPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_category = "Lazy Talior"

    def draw(self, context):
        tailor_props = bpy.context.scene.tailor_props
        
        layout = self.layout
        
        if tailor_props.InitBool == False:
            layout.operator("lt.initialise",
                text="Initialise Lazy Talior",
                icon='RADIOBUT_OFF')
        else:
            layout.operator("lt.initialise",
                text="Lazy Talior Initialised",
                icon='RADIOBUT_ON')


classes = (
    
    LT_PT_LazyPanelMain,
    LT_PT_InitPanel,
    LT_OT_initialise,
    LT_OT_defualt_preset_tailor,
    tailor_props,
    LT_OT_mannequin_reset,

    )

def register():

    LT_IconFactory(RegBool=True)
    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.tailor_props = bpy.props.PointerProperty(type=tailor_props)

def unregister():

    LT_IconFactory(RegBool=False)

    del bpy.types.Scene.tailor_props
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()

