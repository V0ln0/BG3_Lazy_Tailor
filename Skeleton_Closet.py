
# THIS SHIT IS FOR GETTING ASSTES INTO THE CURRENT BLEND FILE
import bpy
import os
from os import path

LT_LibPath = os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor\library\LazyTalior_Assets.blend")


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
   except KeyError:
       link_to = bpy.data.collections.new(Cname)
       scene.collection.children.link(link_to)

   return link_to

# drops an object into the scene by name, works on objects inside instanced collections
def LT_AssetDrop(AssetName):
    
    bpy.ops.object.add_named(name=AssetName)

# todo: this could be cleaned up, but its fine for now
def LT_LoadCol(AssetCol):
   
    bpy.ops.wm.link(
        filepath=os.path.join(LT_LibPath, "Collection", AssetCol),
        directory=os.path.join(LT_LibPath, "Collection"),
        filename=AssetCol,
        do_reuse_local_id=True,
        instance_collections=True
        )
    bpy.data.objects[AssetCol].hide_viewport = True
    with bpy.data.libraries.load(LT_LibPath) as (data_from, data_to):
        data_to.actions = data_from.actions #todo: store list of appended files to for cleaning up later

def LT_SelectMe(TheOneObj):
    bpy.context.view_layer

def LT_MannequinInit(mannequin_f, mannequin_b):
    
    EnsuredCol = LT_ensure_collection("Lazy Tailor Assets")
    
    view_layer = bpy.context.view_layer
    view_layer.active_layer_collection = view_layer.layer_collection.children[EnsuredCol.name] #easier to nest the loaded collection this way then trying to move it
    LT_LoadCol("LT_DontTouchIsBones")
    
    Mannequins = []
    
    for M in bpy.data.objects:
        if M.name == mannequin_f or M.name == mannequin_b:
            bpy.data.collections[EnsuredCol.name].objects.link(M)
            Mannequins.append(M)
            
    bpy.ops.object.select_pattern(pattern=(mannequin_f + "*"), extend=False)
    bpy.ops.object.make_local(type='SELECT_OBDATA')
    bpy.data.armatures[mannequin_f].use_fake_user = True
    bpy.data.armatures[mannequin_b].use_fake_user = True

    
class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."
    
    def execute(self, context):

        lt_props = bpy.context.scene.lt_props

        LT_MannequinInit(lt_props.mannequin_form, lt_props.mannequin_base)
        bpy.context.scene.lt_props.InitBool = True
        
        return {"FINISHED"}

# possible to do: 
#   figure out how to add custom thumbnails to the actions
#   Add in a way for users to write their own actions into LazyTalior_Assets.blend? #pipedream
#   could allow users to write their own assets into the original file or a seperate file to laod in 

