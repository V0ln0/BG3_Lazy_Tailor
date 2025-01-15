
#this file is for fetching assets and organising them inside the blend file
import bpy
import os
from os import path

LT_LibPath = os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor", "library", "LazyTalior_Assets.blend")


# this file used to be so much longer....
# anyway, these functions load the needed armatures + actions into the current Blend file via an instanced collection + loads the actions required
# couldn"t do it all at once because the link function wasn't playing nice with Actions, those have to use libraries.load
# this keeps the whole file much cleaner, but in order for the user to actualy use the anything we have linked over, it has to get "unpacked"
# as in moved out of the insanced folder, and added to the current scene


# checks for a collection, if it exists it returns the collection name. 
# if it dosen't exist, it creates a new collection with the desried name and returns the new collection
def LT_ensure_collection(Cname) -> bpy.types.Collection:

    scene = bpy.context.scene

    try:
        link_to = scene.collection.children[Cname]
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]
    except KeyError:
        link_to = bpy.data.collections.new(Cname)
        scene.collection.children.link(link_to)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]

    return link_to


def LT_LoadCol(AssetCol):
   
    bpy.ops.wm.link(
        
        filepath=os.path.join(LT_LibPath, "Collection", AssetCol),
        directory=os.path.join(LT_LibPath, "Collection"),
        filename=AssetCol,
        do_reuse_local_id=True,
        instance_collections=True
        
        )


def LT_MannequinInit():
    
    EnsuredCol = LT_ensure_collection("Lazy Tailor Assets") #will also make the collection active
    LT_LoadCol("LT_DontTouchIsBones")
    bpy.data.objects["LT_DontTouchIsBones"].hide_viewport = True
    
    with bpy.data.libraries.load(LT_LibPath) as (data_from, data_to):
        data_to.actions = data_from.actions #todo: store list of appended files to for cleaning up later
    
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


def LT_VersionCheck():

    if bpy.app.version < (4, 0, 0):
        return False
    else:
        return True

def LT_ErrorPopup():

    def draw(self, context):
       self.layout.label(text="Lazy Tailor requires Blender 4.0.0 or above, please download the latest version from Blender.org.")
       self.layout.label(text="Remember: you can have more than one copy of Blender instaled!")
        
    bpy.context.window_manager.popup_menu(draw, title = "Warning: Incompatible Version of Blender detected", icon = 'ERROR')

class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."
    
    def execute(self, context):
        
        if LT_VersionCheck() == False:
            LT_ErrorPopup()
            
        else:
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
            LT_MannequinInit()
            bpy.context.view_layer.objects.active = bpy.data.objects[bpy.context.scene.tailor_props.mannequin_form]
            bpy.context.scene.tailor_props.InitBool = True
        
        return {"FINISHED"}


class LT_OT_object_drop(bpy.types.Operator):

    bl_idname = "lt.object_drop"
    bl_label = "object drop"
    bl_description = "Imports an armature that is suitable to be exported in a GR2 file"

    objname: bpy.props.StringProperty(
        name="Asset Name",
        default="",
        )
    
    def execute(self, context):

        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
        
        bpy.ops.object.add_named(name=self.objname)

        return {"FINISHED"}


# possible to do: 
#   figure out how to add custom thumbnails to the actions
#   Add in a way for users to write their own actions into LazyTalior_Assets.blend? #pipedream
#   could allow users to write their own assets into the original file or a seperate file to laod in 
