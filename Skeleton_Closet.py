
# THIS SHIT IS FOR GETTING ASSTES INTO THE FILE
import bpy
import os
from os import path



# class LT_Closet_Tools:





class LT_OT_asset_grab(bpy.types.Operator):

    bl_idname = "lt.asset_grab"
    bl_label = "Asset Grabber"
    bl_description = "Imports assets needed by the addon into your current Blend file. You only need to run this once."

    #gets the absolute path to the asset blend file
    LazyAssetPath = os.path.join(path.dirname(__file__), os.pardir, "LazyTalior_Assets.blend")


    # we're just gonna grab all armature objects via the master collection 'Lazy Tailor Assets' because its the path of least resitance
    # work smart not hard. That said this might not be working smart lol
    # Bone shapes getting draged in is annoying, fix later.
    def LT_Append(AppendType, AppendName):

        bpy.ops.wm.append(
            filepath=os.path.join(LazyAssetPath, AppendType, AppendName),
            directory=os.path.join(LazyAssetPath, AppendType),
            filename=AppendName,
            do_reuse_local_id=True,
            set_fake=True
            )

    def LT_LinkActions():
        with bpy.data.libraries.load(LazyAssetPath, assets_only=True) as (data_from, data_to):
            data_to.actions = data_from.actions

    # custom porp on action to link?
    def LT_LinkRefs(LinkType, LinkName):
        bpy.ops.wm.link(
                filepath=os.path.join(LazyAssetPath, LinkType, LinkName),
                directory=os.path.join(LazyAssetPath, LinkType),
                filename=LinkName,
                do_reuse_local_id=True,
                instance_collections=True
                )
    
    def execute(self, context):
        AssetType = 'Collection'
        scene = bpy.context.scene
        
        LT_Append(AssetType, 'Lazy Tailor Assets')
        LT_LinkActions()
        LT_LinkRefs(AssetType, 'LT_DontTouchIsBones')
        
        # also not thinking smart... too bad!
        for BS in scene.objects:
            if BS.startswith('LT_BS_'):
                bpy.ops.object.delete()
        
        return {'FINISHED'}
