# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions

import bpy


from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)

from bpy.types import PropertyGroup


# finds bones with the 'child of' constraint, treats them all as active, then runs 'set inverse' on all of them
# this is needed because swapping Target_B's data requires those conrstaints to be reset

def Childof_SawpManager(TargetBone):
    ob = bpy.context.active_object
    for b in TargetBone.pose.bones:
        for c in b.constraints:
            if c.type == "CHILD_OF":
                context_py = bpy.context.copy()
                context_py["constraint"] = c
                TargetBone.data.bones.active = b.bone                               
                bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='BONE')

# 'childof_set_inverse' can only run on bones that are visible. All bones in Target_A that have the 'child of' constraint are in the group 'Deform Bones'
# function checks to see if the bone collection is visible, and if its not makes it visible, runs the function, then sets it invisable again.

def BoneColVisCheck(TargetSkel, ColName):
    
    CB = TargetSkel.data.collections_all[ColName.name]
    if CB.is_visible == False:
        CB.is_visible = True
    
    Childof_SawpManager(TargetSkel)
    print("CHIDREN INVERTED")
    
    CB.is_visible = False


class LT_PG_settings(PropertyGroup):
    
        Targ_A: PointerProperty(
        type=bpy.types.Object, 
        name="Target A", 
        description="Select target A", 
        options={'ANIMATABLE'}, 
        update=None
        )