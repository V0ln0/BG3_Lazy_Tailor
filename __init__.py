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
        
        lt_props = bpy.context.scene.lt_props
        
        layout = self.layout
        row = layout.row()
        # todo: bool that stops people from pressing this more than once. it is fine for now
        # LableText = ("Currently converting ") + (lt_props.bc_from) + (", to ") + (lt_props.bc_to) + (".")
        row.label(text='LableText', icon='WORLD_DATA')

        if lt_props.InitBool == False:
            layout.operator("lt.initialise",
                text="Initialise Lazy Talior",
                icon='RADIOBUT_OFF')
        else:
            layout.operator("lt.initialise",
                text="Lazy Talior Initialised",
                icon='RADIOBUT_ON')

        layout.operator("lt.swap_body_type")

# we're gonna have to learn how to use an enum, sorry lol



classes = (
    LT_PT_LazyPanelMain,
    LT_OT_initialise,
    LT_OT_swap_body_type,
    LT_Props,
    )

def register():

    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.lt_props = bpy.props.PointerProperty(type=LT_Props)


def unregister():
    del bpy.types.Scene.lt_props
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()



