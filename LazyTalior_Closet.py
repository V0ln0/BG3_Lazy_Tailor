#this file is for fetching assets and organising them inside the blend file
import bpy
import os



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

    def execute(self, context):

        if VersionCheck() == False:
            VersionError_Popup()
        else:
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

            bpy.context.scene.lt_util_props.InitBool = True
        
        return {"FINISHED"}





class LT_OT_obj_dropper(bpy.types.Operator):
    
    bl_idname = "lt.obj_dropper"
    bl_label = "Get Object"
    bl_description = "Drops a specifc object into the scene."

    obj_name: bpy.props.StringProperty(
        name="obj name",
        default=""
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