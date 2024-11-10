
# THIS SHIT IS FOR GETTING ASSTES INTO THE FILE
import bpy
import os
from os import path

class LT_OT_initialise(bpy.types.Operator):

    bl_idname = "lt.asset_grab"
    bl_label = "Asset Grabber"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."

# this file used to be so much longer....
# anyway, this function links all the needed armatures + actions into the current Blend file via an instanced collection + loads the actions required
# couldn't do it all at once because the link function wasn't playing nice with Actions, those have to use libraries.load
# this keeps the whole file much cleaner, but in order for the user to actualy use the data a new object has to be created in the scnene using the linked data
# will sort out later

    def execute(self, context):
        LT_LibPath = os.path.join(path.dirname(__file__), os.pardir, "LazyTalior_Assets.blend")
        LinkType = 'Collection'
        LinkName = 'Lazy Tailor Assets'
        bpy.ops.wm.link(
                filepath=os.path.join(LT_LibPath, LinkType, LinkName),
                directory=os.path.join(LT_LibPath, LinkType),
                filename=LinkName,
                do_reuse_local_id=True,
                instance_collections=True
                )
        with bpy.data.libraries.load(LT_LibPath) as (data_from, data_to):
            data_to.actions = data_from.actions
        
        return {'FINISHED'}


