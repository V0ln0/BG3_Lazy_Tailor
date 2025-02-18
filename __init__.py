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


class LT_scene_master_panel:
    
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Lazy Talior"
    bl_context = "scene"

    # @classmethod
    # def draw_init_header(cls, context, layout):
    #     lt_util_props = bpy.context.scene.lt_util_props
    #     box = layout.box()

    #     if lt_util_props.InitBool == False: 
    #         row = box.row()
    #         row.alignment = 'CENTER'
    #         row.label(text="Lazy Talior Status: NOT READY", icon='RADIOBUT_OFF')
    #         row = box.row()
    #         row.alignment = 'CENTER'
    #         row.operator("lt.initialise", text="Initialise")

    #     else:
    #         row = box.row()
    #         row.label(text="Lazy Talior Status: READY", icon='RADIOBUT_ON')
    #         row.alignment = 'CENTER'
    #         row = box.row()
    #         row.alignment = 'CENTER'
    #         row.enabled = False
    #         row.operator("lt.initialise", text="Initialise")


class LT_PT_lazy_panel_main(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = ""
    bl_idname = "LT_PT_lazy_panel_main"
    bl_category = "Lazy Talior"


    def draw_header(self, context):
        
        layout = self.layout
        row = layout.row()
        row.label(text="BG3 Lazy Tailor")
        if bpy.context.scene.lt_util_props.InitBool == False:
            row.operator("lt.initialise", text="Initialise")


    def draw(self, context):
        
        lt_util_props = bpy.context.scene.lt_util_props
        layout = self.layout

       
        # #pulling this shit purely to disable the ui when the assets aren't loaded
        # sub_layout = layout.column()
        # sub_layout.enabled = lt_util_props.InitBool
        if bpy.context.scene.lt_util_props.InitBool == True:
            col = layout.column(align= True)
            col.label(text="Mannequin Options: Basic")
            col.separator(type='LINE')
            col.separator(factor=0.5)
        
            col.prop(lt_util_props, "from_body")
            col.prop(lt_util_props, "to_body")
            col.separator(factor=0.5)
            col.separator(type='LINE')
            split = col.split(factor=0.65)
            split_left = split.column(align= True)
            split_left.operator("wm.call_menu", text="Finalise").name = "LT_MT_mass_apply_menu"
            split_left.scale_y = 2.0
            split_right = split.column(align= True)
            split_right.operator("lt.defualt_preset_tailor", text="Apply")
            props = split_right.operator("lt.confirm_choice", text="Reset")
            props.the_thing = "reset Local_Mannequin"
            props.op_name = "lt.mannequin_reset"
            
            # col = layout.column()
            # col.separator(type='LINE')
            # col = layout.column()

            # col.operator("wm.call_menu", text="Finalise").name = "LT_MT_mass_apply_menu"
            


            col.separator(type='LINE')




class LT_PT_lazy_advanced_panel(LT_scene_master_panel, preset_info_ui, bpy.types.Panel):
    
    bl_label = "Mannequin Options: Custom"
    bl_idname = "LT_PT_lazy_advanced_panel"
    bl_parent_id = "LT_PT_lazy_panel_main"
    bl_order = 0
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return bool(context.scene.lt_util_props.InitBool)
    
    def draw(self, context):
        

        action_lock = self.is_lt_action()
        layout = self.layout
        layout.prop(context.scene, "lt_actions", text="Pre-Set")
        layout.separator(type='LINE')

        split = layout.split(factor=0.65)
        split_a = split.column()
        info = split_a.row()
        info.enabled = action_lock
        info.menu("LT_MT_about_preset_scene_menu")
        split_b = split.column()
        split_b.operator("lt.apply_user_preset", text="Apply")
        layout.separator(type='LINE')
        layout.operator("lt.load_user_presets", text="Load Pre-Sets")



class LT_PT_utility_panel(LT_scene_master_panel, bpy.types.Panel):
    
    bl_label = "Utility"
    bl_idname = "LT_PT_utility_panel"
    bl_parent_id = "LT_PT_lazy_panel_main"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return bool(context.scene.lt_util_props.InitBool)
    
    def draw(self, context):
        
        tailor_prefs = bpy.context.preferences.addons[__name__].preferences
        lt_util_props = bpy.context.scene.lt_util_props
        
        layout = self.layout
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
        
        layout.label(text="Helper Assets:")
        box = layout.box()
        col = box.column()
        
        col.label(text="Export Ready Armature:")
        split = col.split(factor=0.65)
        split_a = split.column()
        split_a.prop(lt_util_props,"gilf_bones", text="") 
        
        split_b = split.column()
        split_b.operator("lt.obj_dropper", text="Append").obj_name= lt_util_props.gilf_bones
        col = box.column()
        
        col.label(text="Body Reference:")
        split = col.split(factor=0.65)
        split_a = split.column()
        split_a.prop(lt_util_props,"ref_bodies", text="")
        
        split_b = split.column()
        split_b.operator("lt.obj_dropper", text="Append").obj_name= lt_util_props.ref_bodies
        box.separator(factor=0.1)
        
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


class LT_PT_mannequin_vis(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BG3 LT"
    bl_label = 'Mannequin'
    bl_context = 'posemode'
    
    @classmethod
    def poll(cls, context):
        return bool(context.active_object.name == 'Local_Mannequin')
    
    def draw(self, context):

        layout = self.layout
        mannequin_data = bpy.data.armatures['Local_Mannequin']
        
        row = layout.row(align=True)
        row.label(text="Control Visibility")
        box = layout.box()
        grid = box.grid_flow(row_major=True, columns=2, even_columns=True)

        grid.prop(mannequin_data.collections["CTRL_Torso"], "is_visible", text="Torso Main", toggle=True)
        grid.prop(mannequin_data.collections["CTRL_Arms"], "is_visible", text="Arms Main", toggle=True)            
        grid.prop(mannequin_data.collections["CTRL_Hands"], "is_visible", text="Hands Main", toggle=True)            
        grid.prop(mannequin_data.collections["CTRL_Legs"], "is_visible", text="Legs Main", toggle=True)


class LT_action_master_panel:
    
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "BG3 LT"
    bl_context = "data"
    _context_path = "active_action"
    _property_type = bpy.types.Action
    
    #I still have no idea how classmethods work and at this point I am afraid to ask
    #I also have no idea how this is pulling the active action
    @classmethod
    def poll(cls, context):
        return bool(context.active_action)

class LT_PT_edit_preset_main_panel(LT_action_master_panel, preset_info, bpy.types.Panel):

    bl_label = "Pre-Set Editor"
    bl_idname = "LT_PT_edit_preset_main_panel"
    bl_category = "BG3 LT"
    
    # @classmethod
    # def poll(cls, context):
    #     return bool(context.scene.lt_util_props.InitBool)
    
    def draw(self, context):
        action = context.active_action
        layout = self.layout

        layout.label(text=action.name)
        # layout.operator("wm.call_menu", text="About This Pre-Set").name = "LT_MT_about_preset_scene_menu"
        layout.operator_menu_enum("lt.set_from_tailor", "from_bones")
        layout.operator_menu_enum("lt.set_to_tailor", "to_bones")
        layout.separator(type='LINE')
        
    #I still have no idea how classmethods work and at this point I am afraid to ask
    #I also have no idea how this is pulling the active action


# class LT_PT_edit_preset_sub_panel(LT_action_master_panel, preset_info_ui, bpy.types.Panel):
    
#     bl_label = "Pre-Set Info"
#     bl_idname = "LT_PT_edit_preset_sub_panel"
#     bl_parent_id = "LT_PT_edit_preset_main_panel"
#     bl_order = 0
#     bl_options = {'DEFAULT_CLOSED'}

#     @classmethod
#     def poll(cls, context):
#         return bool(context.scene.lt_util_props.InitBool)
    
#     def draw(self, context):
#         action = context.active_action
#         layout = self.layout
#         self.draw_preset_info(self, context, layout, action)
        



class LT_PT_edit_preset_edit_panel(LT_action_master_panel, preset_info, bpy.types.Panel):
    
    bl_label = "Edit Pre-Set Info"
    bl_idname = "LT_PT_edit_preset_edit_panel"
    bl_parent_id = "LT_PT_edit_preset_main_panel"
    bl_order = 1
    bl_options = {'DEFAULT_CLOSED'}

    # @classmethod
    # def poll(cls, context):
    #     return bool(context.scene.lt_util_props.InitBool)
    
    def draw(self, context):
        action = context.active_action
        lt_user_props = bpy.context.scene.lt_user_props
        hands_off = self.is_not_defualt(action)
        
        
        layout = self.layout
        if hands_off == False:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text="Warning: Defualt Pre-Sets can not be edited.")
            layout.separator(type='LINE')

        lock_col = layout.column()
        lock_col.enabled = hands_off
        lock_col.label(text="Edit Pre-Set Info:")
        box = lock_col.box()

        col = box.column()
        col.prop(lt_user_props, "type_action")
        col.prop(lt_user_props, "from_body_action")
        col.prop(lt_user_props, "to_body_action")
        col.prop(lt_user_props, "creator")
        col.prop(lt_user_props, "desc")
        row = box.row()
        row.alignment = 'RIGHT'
        row.operator("lt.set_preset_info", text="Set Info")


        check_save =  lock_col.operator("lt.confirm_choice", text="Save to File")
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
    lt_user_props,
    LT_PT_tailor_AddonPreferences,
    LT_OT_mannequin_reset,
    LT_OT_set_from_tailor,
    LT_OT_set_to_tailor,
    LT_PT_mannequin_vis,
    LT_PT_lazy_advanced_panel,
    LT_PT_utility_panel,
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
    LT_PT_edit_preset_main_panel,
    LT_MT_about_preset_scene_menu,
    # LT_PT_edit_preset_sub_panel,
    LT_PT_edit_preset_edit_panel,
    LT_OT_set_preset_info,
    

    )


# filter to prevent the user from selecting the defualt actuion presets in the ui
def lt_base_action_poll(self, action): 

    if action.get('LT_Default') is None:
        return action


def register():

    bpy.types.Scene.lt_actions = bpy.props.PointerProperty(

        type=bpy.types.Action,
        poll=lt_base_action_poll
    )
    for _class in classes: 
        bpy.utils.register_class(_class)
    
    bpy.types.Scene.lt_util_props = bpy.props.PointerProperty(type=lt_util_props)
    bpy.types.Scene.lt_user_props = bpy.props.PointerProperty(type=lt_user_props)

def unregister():

    del bpy.types.Scene.lt_util_props
    del bpy.types.Scene.lt_user_props
    del bpy.types.Scene.lt_actions
    for _class in classes: 
        bpy.utils.unregister_class(_class)  

if __name__ == "__main__":
    register()

