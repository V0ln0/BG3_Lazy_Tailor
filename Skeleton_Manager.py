# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions

import bpy

# finds bones with the 'child of' constraint, treats them all as active, then runs 'set inverse' on all of them
# this is needed because swapping Target_B's data requires those conrstaints to be reset

def LT_Childof_MassInvert(TargetBone):
    for b in TargetBone.pose.bones:
        for c in b.constraints:
            if c.type == "CHILD_OF":
                context_py = bpy.context.copy()
                context_py["constraint"] = c
                TargetBone.data.bones.active = b.bone                               
                bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='BONE')

# 'childof_set_inverse' can only run on bones that are visible. All bones in Target_A that have the 'child of' constraint are in the group 'Deform Bones'
# function checks to see if the bone collection is visible, and if its not makes it visible, runs the function, then sets it invisable again.

def LT_Childof_Validator(TargetSkel, ColName):
    
    CB = TargetSkel.data.collections_all[ColName.name]
    if CB.is_visible == False:
        CB.is_visible = True
    
    LT_Childof_MassInvert(TargetSkel)
    print("CHIDREN INVERTED")
    
    CB.is_visible = False




class LT_OT_set_rest_pose(bpy.types.Operator):
    
    bl_idname = "lt.set_rest_pose"
    bl_label = "Set New Rest Pose"
    bl_description = "Sets the current pose of the active armature as its new Rest Pose AKA 'defualt postion'."


    #  sets the current postion of bones as the new rest pose 
    #  used for changing what the starting body type is

    def execute(self, context):
        current_mode = bpy.context.object.mode
        ACT_OB = bpy.context.active_object
        
        if ACT_OB.name == ("Mannequin_BT1") and current_mode == "POSE":
            bpy.ops.pose.armature_apply(selected=False)
        
        return {'FINISHED'}




        