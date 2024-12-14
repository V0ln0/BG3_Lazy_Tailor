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

        row = layout.row()
        my_icon = pcoll["my_icon"]
        # todo: bool that stops people from pressing this more than once. it is fine for now
        # LableText = ("Currently converting ") + (lt_props.bc_from) + (", to ") + (lt_props.bc_to) + (".")
        row.label(text='they really just let you put anything here huh', icon_value=my_icon.icon_id)

        # props = self.layout.operator("lt.type_set", gotta figure out a better way of resetting this shit 
        #     text='RESET'
        #     )
        # props.Race_Index = 0
        # props.Skeleton_Index = 0
        # props.Type_Index = 0
        # props.Part_Index = 0
        
        props = self.layout.operator("lt.type_set",
            text='GTY_M'
            )
        props.Race_Index = 5
        props.Type_Index = 0
        props.Part_Index = 0
        props.Skeleton_Index = 1
        
        props = self.layout.operator("lt.type_set",
            text='HUM_MS'
            )
        props.Race_Index = 1
        props.Type_Index = 2
        props.Part_Index = 0
        props.Skeleton_Index = 3

        props = self.layout.operator("lt.type_set", #preset needs fixing
            text='DGB_M'
            )
        
        props.Race_Index = 9
        props.Type_Index = 0
        props.Part_Index = 0
        props.Skeleton_Index = 3

        props = self.layout.operator("lt.type_set", 
            text='HUM_M TO HUM_F'
            )
        
        props.Race_Index = 1
        props.Type_Index = 0
        props.Part_Index = 7
        props.Skeleton_Index = 2

        
        layout.operator("lt.swap_body_type")

class LT_PT_InitPanel(bpy.types.Panel):
    
    bl_label = "Lazy Talior Supply Closet"
    bl_idname = "LT_PT_InitPanel"
    bl_space_type = "PROPERTIES"
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_category = "Lazy Talior"

    def draw(self, context):
        lt_props = bpy.context.scene.lt_props
        
        layout = self.layout
        
        if lt_props.InitBool == False:
            layout.operator("lt.initialise",
                text="Initialise Lazy Talior",
                icon='RADIOBUT_OFF')
        else:
            layout.operator("lt.initialise",
                text="Lazy Talior Initialised",
                icon='RADIOBUT_ON')

def LT_IconFactory(RegBool: bool):
    
    if RegBool == True:
        pcoll = bpy.utils.previews.new()
        my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
        pcoll.load("my_icon", os.path.join(my_icons_dir, "icon-image.png"), 'IMAGE')
        preview_collections["main"] = pcoll
    else:
        for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)
        preview_collections.clear()

preview_collections = {}

classes = (
    LT_PT_LazyPanelMain,
    LT_PT_InitPanel,
    LT_OT_initialise,
    LT_OT_swap_body_type,
    LT_Props,
    LT_OT_type_set,
    )

def register():

    LT_IconFactory(RegBool=True)
    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.lt_props = bpy.props.PointerProperty(type=LT_Props)


def unregister():

    LT_IconFactory(RegBool=False)

    del bpy.types.Scene.lt_props
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()



