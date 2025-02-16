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
import textwrap

from . LazyTalior_Manager import *
from . LazyTalior_Closet import *
from . LazyTalior_Prop import *
from . LazyTalior_Mesh import *



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

class LT_PT_tailor_AddonPreferences(bpy.types.AddonPreferences):
    
    bl_idname = __name__

    user_lib_path: bpy.props.StringProperty(
        name="User Library Path",
        subtype='FILE_PATH',
        default='set me!',
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

def is_action():
    if bpy.context.scene.lt_actions is not None:
        return True
    else:
        return False
class LT_scene_master_panel:
    
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Lazy Talior"
    bl_context = "scene"

    @classmethod
    def draw_lazy_init_panel(cls, _context, layout):


        lt_util_props = bpy.context.scene.lt_util_props 
        box = layout.box()
        
        if lt_util_props.InitBool == False: 
            row = box.row()
            row.label(text="Lazy Talior Status: NOT READY", icon='RADIOBUT_OFF')
            row.operator("lt.initialise", text="Initialise")
        else:
            row = box.row()
            row.label(text="Lazy Talior Status: READY", icon='RADIOBUT_ON') 

class LT_PT_lazy_panel_main(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "BG3 Lazy Talior"
    bl_idname = "LT_PT_lazy_panel_main"
    bl_category = "Lazy Talior"

# to whoever sees this: this is a mess and I am sorry
    def draw(self, context):
        
        lt_util_props = bpy.context.scene.lt_util_props      

        self.draw_lazy_init_panel(context, self.layout)
        layout = self.layout
        
        #pulling this shit purely to disable the ui when the assets aren't loaded
        sub_layout = layout.column()
        sub_layout.enabled = lt_util_props.InitBool
        
        col = sub_layout.column()

        col.label(text="Mannequin Options: Basic")
        col.separator(type='LINE')
        col.separator(factor=0.5)
    
        col.prop(lt_util_props, "from_body")
        col.prop(lt_util_props, "to_body")
        col.separator(factor=0.5)
        split = col.split(factor=0.65)
        split_left = split.row()
        split_right = split.column()
        # op_col.operator("lt.set_base_tailor")

        split_right.operator("lt.defualt_preset_tailor", text="Apply")
        col = sub_layout.column()
        col.separator(type='LINE')
        # col.separator(factor=0.25)
        col = sub_layout.column()
        split = col.split(factor=0.35)
        split_c = split.column()
        split_c.operator("wm.call_menu", text="Finalise").name = "LT_MT_mass_apply_menu"
        
        props = split_c.operator("lt.confirm_choice", text="Reset")
        props.the_thing = "reset Local_Mannequin"
        props.op_name = "lt.mannequin_reset"

        col.separator(type='LINE')



class LT_PT_user_action_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "Advanced Options"
    bl_idname = "LT_PT_user_action_panel"
    bl_parent_id = "LT_PT_lazy_panel_main"
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        lt_util_props = bpy.context.scene.lt_util_props
        lt_actions = bpy.context.scene.lt_actions
        # action_lock = is_action()
        layout = self.layout
        layout.enabled = lt_util_props.InitBool
        col = layout.column()
        split = col.split(factor=0.65)
        split_left = split.column()
        split_left.label(text="Custom Pre-Sets:")
        split_right = split.column()
        split_right.operator("lt.load_user_presets", text="Load")
        col.separator(type='LINE')
        col.prop(context.scene, "lt_actions", text="")


        split = col.split(factor=0.65)
        split_a = split.column()
        split_a.label(text="Pre-Set Info:")
        split_b = split.column()
        split_b.operator("lt.apply_user_preset", text="Apply")
        info = layout.row()
        info.enabled = is_action()
        info.operator("wm.call_menu", text="More Info").name = "LT_MT_about_preset_menu"

        


class LT_PT_utility_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "Utility"
    bl_idname = "LT_PT_utility_panel"
    bl_parent_id = "LT_PT_lazy_panel_main"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    

    def draw(self, context):
        
        lt_util_props = bpy.context.scene.lt_util_props
        tailor_prefs = bpy.context.preferences.addons[__name__].preferences

        layout = self.layout
        layout.enabled = lt_util_props.InitBool
        col = layout.column()
        col.label(text="Mesh Options:")
        
        col.operator("wm.call_menu", text="Set Export Order").name = "LT_MT_export_order_menu"
        col.operator("lt.so_no_head", text="Create Head_M")
        
        layout.separator(type='LINE')
        layout.label(text="LOD factory:")

        row = layout.row()
        row.operator("wm.call_menu", text="Create LODs").name = "LT_MT_create_lod_menu"
        row.operator("wm.call_menu", text="Set LODs").name = "LT_MT_set_lod_menu"
        layout.separator(type='LINE')


        if tailor_prefs.volno_debug == True:
            box = layout.box()
            box.label(text="Debug Tools")
            box.operator("lt.constraints", text="Child Of")
            props = box.operator("lt.constraints", text="Stretch To")
            props.stretch_to_bool = True
            check_start =  box.operator("lt.confirm_choice", text="Restart")
            check_start.the_thing = "restart Lazy Tailor"
            check_start.op_name = "lt.exterminatus"
            check_start.warn_extra = True
            check_start.warn_message = "WARNING: this will PURGE all Lazy Tailor data from the current file. Does not remove user pre-sets"


class LT_PT_export_helpers_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "Export Eelpers"
    bl_idname = "LT_PT_export_helpers_panel"
    bl_parent_id = "LT_PT_lazy_panel_main"
    bl_order = 2
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        
        lt_util_props = bpy.context.scene.lt_util_props
        
        layout = self.layout
        layout.enabled = lt_util_props.InitBool
        

        layout.label(text="Export Ready Armature:")
        col = layout.column()
        split = col.split(factor=0.65)
        split_a = split.column()
        split_a.prop(lt_util_props,"gilf_bones", text="") 
        split_b = split.column()
        split_b.operator("lt.obj_dropper", text="Append").obj_name= lt_util_props.gilf_bones

        layout.label(text="Body Reference:")
        col = layout.column()
        split = col.split(factor=0.65)
        split_a = split.column()
        split_a.prop(lt_util_props,"ref_bodies", text="")
        split_b = split.column()
        split_b.operator("lt.obj_dropper", text="Append").obj_name= lt_util_props.ref_bodies


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

#returns prop as string for use in ui
def get_lt_prop(preset, propname):

    if preset.get(propname) is not None:
        return preset[propname]

class LT_PT_user_preset_panel(bpy.types.Panel):

    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "BG3 LT"
    bl_label = 'Pre-Set Options'
    bl_context = "data"
    _context_path = "active_action"
    _property_type = bpy.types.Action




    #I still have no idea how classmethods work and at this point I am afraid to ask
    #I also have no idea how this is pulling the active action
    @classmethod
    def poll(cls, context):
        return bool(context.active_action)
    

    def draw(self, context):
        action = context.active_action
        lt_util_props = bpy.context.scene.lt_util_props

        
        layout = self.layout
        layout.enabled = lt_util_props.InitBool
        row = layout.row()
        row.alignment = 'CENTER'
        # row.label(text=action.name, icon='MOD_CLOTH')
        layout.label(text=action.name)
        layout.separator(type='LINE')
        col = layout.column()
        col.prop(lt_util_props, "from_body_action")
        col.prop(lt_util_props, "to_body_action")
        col.prop(lt_util_props, "type_action")
        col.prop(lt_util_props, "creator")
        check_save = layout.operator("lt.confirm_choice", text="Save")
        check_save.the_thing = "save ALL user pre-sets in this file"
        check_save.warn_extra = True
        check_save.warn_message = "Warning: This will overwrite all pre-sets with the same name."
        check_save.op_name = "lt.save_user_presets"

        layout.separator(type='LINE')


def confirm_Popup(do_that: str, op_name: str, extra: bool, extra_con: str): 

    def draw(self, context):
        self.layout.label(text=f"Are you sure that you wish to {do_that}?")
        if extra == True:
            self.layout.label(text=extra_con)
        self.layout.operator(op_name, text= "Yes, do it.")
            
    bpy.context.window_manager.popup_menu(draw, title = "Confirm Choice", icon = 'QUESTION')

class LT_OT_confirm_choice(bpy.types.Operator):
    
    bl_idname = "lt.confirm_choice"
    bl_label = "confirm_choice"
    bl_description = "*John Cena voice* are you sure about that?"
      
    the_thing: bpy.props.StringProperty(
        name="the_thing",
        default="If you're reading this, I forgot to set it",
    )

    op_name: bpy.props.StringProperty(
        name="op_name",
        default="",
    )

    warn_extra: bpy.props.BoolProperty(
        name="warn_extra",
        default=False
    )

    warn_message: bpy.props.StringProperty(
        name="op_name",
        default="If you're reading this, I forgot to set TWO things",
    )

    def execute(self, context):
        confirm_Popup((self.the_thing), (self.op_name), (self.warn_extra), (self.warn_message))
        return {"FINISHED"}


classes = (

    LT_PT_lazy_panel_main,
    LT_OT_initialise,
    LT_OT_defualt_preset_tailor,
    lt_util_props,
    LT_PT_tailor_AddonPreferences,
    LT_OT_mannequin_reset,
    LT_OT_set_base_tailor,
    LT_PT_mannequin_vis,
    LT_PT_user_action_panel,
    LT_PT_utility_panel,
    LT_PT_export_helpers_panel,
    LT_OT_export_order_setter,
    LT_OT_mass_apply_modifier,
    LT_MT_mass_apply_menu,
    LT_MT_export_order_menu,
    LT_OT_create_lod,
    LT_MT_create_lod_menu,
    LT_MT_set_lod_menu,
    LT_OT_so_no_head,
    LT_OT_apply_user_preset,
    LT_OT_load_user_presets,
    LT_OT_save_user_presets,
    LT_OT_constraints,
    LT_OT_confirm_choice,
    LT_OT_obj_dropper,
    LT_OT_exterminatus,
    LT_PT_user_preset_panel,
    LT_MT_about_preset_menu,

    )


# filter to prevent the user from selecting the defualt actuion presets in the ui
def lt_base_action_poll(self, action): 

    if action.get('LT_Default') is not None:
        return action


def register():

    bpy.types.Scene.lt_actions = bpy.props.PointerProperty(

        type=bpy.types.Action,
        poll=lt_base_action_poll
    )
    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.lt_util_props = bpy.props.PointerProperty(type=lt_util_props)

def unregister():

    del bpy.types.Scene.lt_util_props
    del bpy.types.Scene.lt_actions
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()

