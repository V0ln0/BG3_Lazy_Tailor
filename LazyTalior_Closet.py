#this file is for fetching assets and organising them inside the blend file
import bpy
import os


def ensure_collection(Cname:str) -> bpy.types.Collection:

    try:
        link_to = bpy.context.scene.collection.children[Cname]
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]
    except KeyError:
        link_to = bpy.data.collections.new(Cname)
        bpy.context.scene.collection.children.link(link_to)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]

    return link_to

#same as ensure_collection but instead links to a specific collection instead of scene.collection
def ensure_collection_child(Cname:str, Pcol) -> bpy.types.Collection:

    try:
        link_to = bpy.data.collections[Cname]
        Pcol.children.link(link_to) 
    except KeyError:
        link_to = bpy.data.collections.new(Cname)
        Pcol.children.link(link_to)
    except RuntimeError:
        link_to = bpy.data.collections[Cname]
    return link_to



'''
addon is reliant on premade assets prseent in LazyTalior_Supply_Closet.blend
step by step
new collection called "Lazy Tailor Assets"(LTA) is created in user's current scene
the collection with the assets "LT_DontTouchIsBones" (isBones) is linked to LTA as an instanced collection
new subfolder in LTA is created(M) and objects LT_Mannequin and LT_Mannequin_Base are pulled out of LTA into it
LT_Mannequin + LT_Mannequin_Base are made made into local data (both the object AND the armature data), the given a fake user
bpy.context.scene.lt_util_props.InitBool is then set to True wich unlocks the ui
'''
class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."

    def execute(self, context):

        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
        
        LibPath = bpy.context.scene.lt_util_props.LibPath
        EnsuredCol = ensure_collection("Lazy Tailor Assets") #will also make the collection active
        
        isbones = "LT_DontTouchIsBones"
        bpy.ops.wm.link(
            
            filepath=os.path.join(LibPath, "Collection", isbones),
            directory=os.path.join(LibPath, "Collection"),
            filename=isbones,
            do_reuse_local_id=True,
            instance_collections=True
            
            ) 

        bpy.data.objects[isbones].hide_viewport = True
        MannequinCol = ensure_collection_child("Mannequins", EnsuredCol)
        Mannequins = [Mannequin for Mannequin in bpy.data.objects if Mannequin.name.startswith("LT_Mannequin")]
        
        for linked_M in Mannequins:

            MannequinCol.objects.link(linked_M)
            linked_M.make_local()
            linked_M.data.make_local()

        bpy.ops.object.select_all(action='DESELECT')
        for M in MannequinCol.objects:
            M.data.use_fake_user = True
            M.data.name = "Local_" + (M.name.replace('LT_','')) 
            M.name = M.data.name
            '''
            renaming both obj and data because Blender HAS and WILL get confused if there is linked data with the same name as local data in the file
            probbably dosen't help that these two idecialy names objects are in the same scene
            due to LT_DontTouchIsBones being an instanced collection
            '''

        bpy.context.scene.lt_util_props.InitBool = True
        
        return {"FINISHED"}


class LT_OT_asset_dropper(bpy.types.Operator):
    
    bl_idname = "lt.asset_dropper"
    bl_label = "Get Asset"
    bl_description = "Drops a specifc asset into the scene."

    asset_name: bpy.props.StringProperty(
        name="asset name",
        default=""
    )

    link_append: bpy.props.BoolProperty(
        name="link_append",
        default=False)
    
    def execute(self, context):
        LibPath = bpy.context.scene.lt_util_props.LibPath
        #this feels like a bad way of handling it
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
        
        if self.link_append:
            
            bpy.ops.wm.link(
                filepath=os.path.join(LibPath, "Object", self.asset_name),
                directory=os.path.join(LibPath, "Object"),
                filename=self.asset_name,
                do_reuse_local_id=True,
                instance_collections=True
                ) 
            obj = bpy.data.objects[self.asset_name]
            obj.make_local()
            obj.data.make_local()

        else:

            bpy.ops.wm.append(
                filepath=os.path.join(LibPath, "Object", self.asset_name),
                directory=os.path.join(LibPath, "Object"),
                filename=self.asset_name,
                set_fake=True,
                clear_asset_data=True
                )  

        return {"FINISHED"}

class LT_OT_exterminatus(bpy.types.Operator):
    
    bl_idname = "lt.exterminatus"
    bl_label = "Restart Tailor"
    bl_description = "Removes all Lazy Tailor data from your file"

    def execute(self, context):
        #TODO: make the node groups local before resetting the addon
        bpy.data.libraries.remove(bpy.data.libraries["LazyTalior_Supply_Closet.blend"])
        corpse_wagon = ("Local_Mannequin", "Local_Mannequin_Base")
        
        #what came first, the object or the data?
        #trick question, its data, so the object gets deleted first.
        for OBJ in bpy.data.objects:
            if OBJ.name in corpse_wagon:
                OBJ.data.use_fake_user = False
                bpy.data.objects.remove(OBJ)

        for ARM in bpy.data.armatures:
            if ARM .name in corpse_wagon:
                bpy.data.armatures.remove(ARM)

        bpy.data.objects.remove(bpy.data.objects["LT_DontTouchIsBones"])  
        bpy.context.scene.lt_util_props.InitBool = False
        return {"FINISHED"}
    