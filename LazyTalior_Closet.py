#this file is for fetching assets and organising them inside the blend file
import bpy
import os


# this file used to be so much longer....
# anyway, these functions load the needed armatures + actions into the current Blend file via an instanced collection + loads the actions required
# couldn"t do it all at once because the link function wasn't playing nice with Actions, those have to use libraries.load
# this keeps the whole file much cleaner, but in order for the user to actualy use the anything we have linked over, it has to get "unpacked"
# as in moved out of the insanced folder, and added to the current scene


def VersionCheck():

    if bpy.app.version < (4, 0, 0):
        return False
    else:
        return True

def VersionError_Popup(): 

    def draw(self, context):
       self.layout.label(text="Lazy Tailor requires Blender 4.0.0 or above, please download the latest version from Blender.org.")
       self.layout.label(text="Remember: you can have more than one copy of Blender instaled!")
        
    bpy.context.window_manager.popup_menu(draw, title = "Warning: Incompatible Version of Blender detected", icon = 'ERROR')

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

class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."
    
    def MannequinInit(self):
        
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
        # local_Mannequins = self.link_mannequins(EnsuredCol)
        

        

        
        # bpy.ops.object.select_by_type(type='ARMATURE')
        # bpy.ops.object.make_local(type='SELECT_OBDATA')
        
        # for N in bpy.context.selected_objects:  
        #     N.data.use_fake_user = True
        #     N.data.name = "Local_" + (N.name.replace('LT_',''))
        #     N.name = "Local_" + (N.name.replace('LT_',''))
        


    def execute(self, context):

        if VersionCheck() == False:
            VersionError_Popup()
            
        else:
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except RuntimeError:
                pass
            self.MannequinInit()
            # bpy.context.view_layer.objects.active = bpy.data.objects['Local_Mannequin']
            bpy.context.scene.lt_util_props.InitBool = True
        
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
        LibPath = bpy.context.scene.lt_util_props.LibPath
        #this feels like a bad way of handling it
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
        bpy.ops.wm.append(
            
            filepath=os.path.join(LibPath, "Object", self.obj_name),
            directory=os.path.join(LibPath, "Object"),
            filename=self.obj_name,
            set_fake=True,
            clear_asset_data=True
            )         

        return {"FINISHED"}

class LT_OT_exterminatus(bpy.types.Operator):
    
    bl_idname = "lt.exterminatus"
    bl_label = "Restart Tailor"
    bl_description = "Removes all Lazy Tailor data from your file"


    def execute(self, context):


        bpy.data.libraries.remove(bpy.data.libraries["LazyTalior_Supply_Closet.blend"])
        
        for A in bpy.data.actions:
            if A.get("LT_Default") is not None:
                A.use_fake_user = False
                bpy.data.actions.remove(A)
        
        corpse_wagon = ("Local_Mannequin", "Local_Mannequin_Base")
        
        #what came first, the object or the data?
        #trick question, its data, so the object gets deleted first.
        for O in bpy.data.objects:
            if O.name in corpse_wagon:
                O.data.use_fake_user = False
                bpy.data.objects.remove(O)

        for ARM in bpy.data.armatures:
            if ARM .name in corpse_wagon:
                bpy.data.armatures.remove(ARM)

        bpy.data.objects.remove(bpy.data.objects["LT_DontTouchIsBones"])  
        bpy.context.scene.lt_util_props.InitBool = False
        return {"FINISHED"}