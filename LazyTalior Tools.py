# these are various scripts that I made while constructing the rig for this tool
# I've added them to the addon because they have some use and it beats copying and pasting them across files
# Thank you to Kit on Discord for the help with some of these

import bpy

class LT_Tools():
    def LT_ChildOfChain():
        armature = bpy.context.object

        if armature.mode != 'POSE':
            bpy.ops.object.posemode_toggle()

        # get selected and active bones

        selected_bones = bpy.context.selected_pose_bones
        active_bone = bpy.context.active_pose_bone

        if active_bone and len(selected_bones) > 1:
            for bone in selected_bones:
                # skip the active bone
                if bone == active_bone:
                    continue
                
                # add a Child Of constraint to all the selected bones and set target
                child_of_constraint = bone.constraints.new(type='CHILD_OF')
                
                child_of_constraint.target = armature
                child_of_constraint.subtarget = active_bone.name

                # here go through each bone to set it to active to set inverse
                
                bpy.context.view_layer.objects.active = armature
                bpy.context.object.data.bones.active = bone.bone

                # context update before setting inverse
                bpy.context.view_layer.update()
                
                # set inverse operator
                bpy.ops.constraint.childof_set_inverse(constraint=child_of_constraint.name, owner='BONE')