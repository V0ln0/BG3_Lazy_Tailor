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

from . LazyTalior_Manager import *
from . LazyTalior_Closet import *
from . LazyTalior_Prop import *
from . LazyTalior_utils import *


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

class tailor_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = __name__

    user_lib_path: bpy.props.StringProperty(
        name="User Library Path",
        subtype='FILE_PATH',
        default='',
        description="Location of a Blend file that you wish to store custom pre-sets in."
    )

    volno_debug: bpy.props.BoolProperty(
        name="Volno's debug Tools",
        default=False,
        description="Enables debuging tools, HANDS OFF UNLESS YOU KNOW WHAT YOU'RE DOING"
    )
    
    def draw(self, context):
        
        layout = self.layout
        layout.label(text="BG3 Lazy Tailor AddonPreferences")
        layout.prop(self, "user_lib_path")
        layout.prop(self, "volno_debug")



class LT_scene_master_panel:
    
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Lazy Talior"
    bl_context = "scene"

class LT_PT_lazy_panel_parent(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "BG3 Lazy Talior"
    bl_idname = "LT_PT_lazy_panel_parent"
    bl_category = "Lazy Talior"

    def draw(self, context):
        
        layout = self.layout

        tailor_props = bpy.context.scene.tailor_props #there's gotta be a better way than writting this out constantly
        
        box = layout.box()
        
        if tailor_props.InitBool == False: 
            row = box.row()
            row.label(text="Lazy Talior Status: NOT READY", icon='RADIOBUT_OFF')
            row.operator("lt.initialise", text="Initialise")
        else:
            row = box.row()
            row.label(text="Lazy Talior Status: READY", icon='RADIOBUT_ON') 

        col = layout.column()
        col.enabled = tailor_props.InitBool
        col.label(text="Mannequin Options")
        col.separator(type='LINE')
        col.separator(factor=0.5)
    
        split = col.split(factor=0.65)
        
        prop_col = split.column()
        prop_col.prop(tailor_props, "from_body")
        prop_col.prop(tailor_props, "to_body")
        
        op_col = split.column()
        op_col.operator("lt.set_base_tailor")
        op_col.operator("lt.defualt_preset_tailor", text="Apply")
        op_col.operator("lt.mannequin_reset", text="Reset")
        row = col.row()
        row.alignment = 'LEFT'
        row.operator("wm.call_menu", text="Finalise").name = "LT_MT_mass_apply_menu"
        col.separator(type='LINE')
        col.prop(context.scene, "lt_actions")


        
class LT_PT_utility_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "Utility"
    bl_idname = "LT_PT_utility_panel"
    bl_parent_id = "LT_PT_lazy_panel_parent"
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        
        tailor_props = bpy.context.scene.tailor_props

        layout = self.layout
        layout.enabled = tailor_props.InitBool
        layout.label(text="Mesh Options")
        layout.operator("wm.call_menu", text="Set Export Order").name = "LT_MT_export_order_menu"
        layout.operator("lt.so_no_head", text="Create Head_M")
        layout.prop_search(bpy.context.scene,)
  

class LT_PT_lod_factory_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "LOD factory"
    bl_idname = "LT_PT_lod_factory_panel"
    bl_parent_id = "LT_PT_lazy_panel_parent"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
            
        tailor_props = bpy.context.scene.tailor_props
        layout = self.layout
        layout.enabled = tailor_props.InitBool
        
        col = layout.column()
        col.operator("wm.call_menu", text="Create LODs").name = "LT_MT_create_lod_menu"
        col.operator("wm.call_menu", text="Set LODs").name = "LT_MT_set_lod_menu"


class LT_PT_mannequin_vis(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BG3 LT"
    bl_label = 'Mannequin'
    bl_context = 'posemode'

    def draw(self, context):

        layout = self.layout
        mannequin_obj = bpy.data.objects['Local_Mannequin']
        mannequin_data = bpy.data.armatures['Local_Mannequin']

        if context.active_object is not mannequin_obj:
            pass

        else:
            row = layout.row(align=True)
            row.label(text="Control Visibility")
            box = layout.box()
            grid = box.grid_flow(row_major=True, columns=2, even_columns=True)

            grid.prop(mannequin_data.collections["CTRL_Torso"], "is_visible", text="Torso Main", toggle=True)
            grid.prop(mannequin_data.collections["CTRL_Arms"], "is_visible", text="Arms Main", toggle=True)            
            grid.prop(mannequin_data.collections["CTRL_Hands"], "is_visible", text="Hands Main", toggle=True)            
            grid.prop(mannequin_data.collections["CTRL_Legs"], "is_visible", text="Legs Main", toggle=True)



classes = (

    LT_PT_lazy_panel_parent,
    LT_OT_initialise,
    LT_OT_defualt_preset_tailor,
    tailor_props,
    tailor_AddonPreferences,
    LT_OT_mannequin_reset,
    LT_OT_set_base_tailor,
    LT_PT_mannequin_vis,
    LT_PT_utility_panel,
    LT_OT_export_order_setter,
    LT_OT_mass_apply_modifier,
    LT_MT_mass_apply_menu,
    LT_MT_export_order_menu,
    LT_OT_create_lod,
    LT_PT_lod_factory_panel,
    LT_MT_create_lod_menu,
    LT_MT_set_lod_menu,
    LT_OT_so_no_head,
    LT_OT_save_user_presets,


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

