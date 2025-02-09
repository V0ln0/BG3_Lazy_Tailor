#this file is for fetching assets and organising them inside the blend file
import bpy
import os
from . LazyTalior_utils import *

# this file used to be so much longer....
# anyway, these functions load the needed armatures + actions into the current Blend file via an instanced collection + loads the actions required
# couldn"t do it all at once because the link function wasn't playing nice with Actions, those have to use libraries.load
# this keeps the whole file much cleaner, but in order for the user to actualy use the anything we have linked over, it has to get "unpacked"
# as in moved out of the insanced folder, and added to the current scene

def LT_VersionCheck():

    if bpy.app.version < (4, 0, 0):
        return False
    else:
        return True

def LT_VersionError_Popup(): 

    def draw(self, context):
       self.layout.label(text="Lazy Tailor requires Blender 4.0.0 or above, please download the latest version from Blender.org.")
       self.layout.label(text="Remember: you can have more than one copy of Blender instaled!")
        
    bpy.context.window_manager.popup_menu(draw, title = "Warning: Incompatible Version of Blender detected", icon = 'ERROR')

def LT_loadActions(Path):
        
        with bpy.data.libraries.load(Path) as (data_from, data_to):
            data_to.actions = data_from.actions #todo: store list of appended files to for cleaning up later

        for A in data_to.actions:
            A.use_fake_user = True

# filter to prevent the user from selecting the defualt actuion presets in the ui

def lt_base_action_poll(self, action): 

    if not action.name.startswith("LT_"):
        return action 

class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."
    
    def LT_LoadCol(self, AssetCol, AssetPath):
    
        bpy.ops.wm.link(
            
            filepath=os.path.join(AssetPath, "Collection", AssetCol),
            directory=os.path.join(AssetPath, "Collection"),
            filename=AssetCol,
            do_reuse_local_id=True,
            instance_collections=True
            
            ) 

    def LT_MannequinInit(self):
        
        LibPath = bpy.context.scene.tailor_props.LibPath
        
        EnsuredCol = LT_ensure_collection("Lazy Tailor Assets") #will also make the collection active
        self.LT_LoadCol("LT_DontTouchIsBones", LibPath)
        bpy.data.objects["LT_DontTouchIsBones"].hide_viewport = True
        
        LT_loadActions(LibPath)
        
        Mannequins = []
        for M in bpy.data.objects:
            if M.name.startswith("LT_Mannequin"):
                bpy.data.collections[EnsuredCol.name].objects.link(M)
                Mannequins.append(M.name)
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='ARMATURE')
        bpy.ops.object.make_local(type='SELECT_OBDATA')
        
        for N in bpy.context.selected_objects: #this crap is literaly just to make sure that blender dosen't try to effect the linked data with similar names ffs
            N.data.use_fake_user = True
            N.data.name = "Local_" + ( N.name.replace('LT_',''))
            N.name = "Local_" + ( N.name.replace('LT_',''))


    def execute(self, context):

        if LT_VersionCheck() == False:
            LT_VersionError_Popup()
            
        else:
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
            self.LT_MannequinInit()
            bpy.context.view_layer.objects.active = bpy.data.objects['Local_Mannequin']
            bpy.context.scene.tailor_props.InitBool = True
        
        return {"FINISHED"}




class LT_OT_obj_dropper(bpy.types.Operator):
    
    bl_idname = "lt.obj_dropper"
    bl_label = "Get Object"
    bl_description = "Drops a specifc object into the scene."

    obj_name: bpy.props.StringProperty(
        name="obj_name",
        default="If you're reading this, I forgot to set it",
    )

    def execute(self, context):
        LibPath = bpy.context.scene.tailor_props.LibPath
        
        bpy.ops.wm.append(
            
            filepath=os.path.join(LibPath, "Object", self.obj_name),
            directory=os.path.join(LibPath, "Object"),
            filename=self.obj_name,
            set_fake=True,
            clear_asset_data=True
            )         

        return {"FINISHED"}
    

class LT_OT_load_user_presets(bpy.types.Operator):
    
    bl_idname = "lt.load_user_presets"
    bl_label = "load user presets"
    bl_description = "Loads all actions from the Blend file defined in the addon preferences."

    def execute(self, context):
        user_lib_path = bpy.context.preferences.addons[__package__].preferences.user_lib_path
        try:
            LT_loadActions(user_lib_path)
        except KeyError:
            
            LT_Error_Popup(
                pop_title="Error: Unable to load Pre-Sets",
                error_reason="No valid data found in the provided filepath. ",
                suggestion="Either the path is invalid, or there are no actions inside the Blend file."
                )
            
        return {"FINISHED"}
    

class LT_OT_save_user_presets(bpy.types.Operator):
    
    bl_idname = "lt.save_user_preset"
    bl_label = "Save User Pre-Sets"
    bl_description = "Saves all Actions created by the user to the Blend file defined in the addon preferences'"

    
    def execute(self, context):
        
        user_lib_path = bpy.context.preferences.addons[__package__].preferences.user_lib_path

        data_blocks = set(action for action in bpy.data.actions if not action.name.startswith("LT_"))

        bpy.data.libraries.write(user_lib_path, data_blocks, fake_user=True)
        
        return {"FINISHED"}



