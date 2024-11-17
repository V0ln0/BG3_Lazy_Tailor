
# THIS SHIT IS FOR GETTING ASSTES INTO THE CURRENT BLEND FILE + ORGANISIG IT
import bpy
import os
from os import path

LT_LibPath = os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor\Library\LazyTalior_Assets.blend")


# this file used to be so much longer....
# anyway, these functions load the needed armatures + actions into the current Blend file via an instanced collection + loads the actions required
# couldn't do it all at once because the link function wasn't playing nice with Actions, those have to use libraries.load
# this keeps the whole file much cleaner, but in order for the user to actualy use the anything we have linked over, it has to get "unpacked"
# as in moved out of the insanced folder, and added to the current scene

def LT_LinkCol(ColName):
    
    bpy.ops.wm.link(
        filepath=os.path.join(LT_LibPath, 'Collection', ColName),
        directory=os.path.join(LT_LibPath, 'Collection'),
        filename=ColName,
        do_reuse_local_id=True,
        instance_collections=True
        )

# links actions, done this way because using the Link function was not playing nice with actions.
def LT_LinkAction():

    with bpy.data.libraries.load(LT_LibPath) as (data_from, data_to):
        data_to.actions = data_from.actions

# sets the conrtoll bones in the Mannequin to visable and hides the deform bones.
# hacky as all hell but this was dne just so it dosen't clutter up the work space when you port it in
def LT_ArmColVis(ArmName):

    bpy.ops.armature.collection_show_all()
    bpy.data.armatures[ArmName].collections_all["Deform_Bones"].is_visible = False

# drops an object into the scene by name, works on objects inside instanced collections
def LT_AssetDrop(AssetName):
    
    bpy.ops.object.add_named(name=AssetName)

def LT_MannequinInit(Mname):
    
    LT_AssetDrop(Mname)
    LT_ArmColVis(Mname)

class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.initialise"
    bl_label = "Initialise Lazy Talior"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."

    def execute(self, context):

        AssetCol = 'Lazy_Tailor_Assets'
        ArmRef = 'LT_Mannequin'
        LT_LinkAction()
        LT_LinkCol(AssetCol)
        LT_MannequinInit(ArmRef)
        return {'FINISHED'}

# possible to do: 
#   figure out how to add custom thumbnails to the actions
#   Add in a way for users to write their own actions into LazyTalior_Assets.blend? #pipedream
