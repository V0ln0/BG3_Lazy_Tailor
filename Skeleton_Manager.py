import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       PointerProperty)

from bpy.types import PropertyGroup
        
def ChildSetInverter(TargetBone):
    ob = bpy.context.active_object
    for b in TargetBone.pose.bones:
        for c in b.constraints:
            if c.type == "CHILD_OF":
                context_py = bpy.context.copy()
                context_py["constraint"] = c
                TargetBone.data.bones.active = b.bone                               
                bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='BONE')

def ShowMeYourBones(TargetSkel, ColName):
    
    CB = TargetSkel.data.collections_all[ColName.name]
    if CB.is_visible == False:
        CB.is_visible = True
        ChildSetInverter(TargetSkel)
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