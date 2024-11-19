# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions

import bpy

# this thing is for finding the same of specific assets(armatures + actions) in the file
class LT_BodyManager:
    def __init__(self, RaceIndex, GenderIndex):
        
        self.RaceIndex = RaceIndex
        self.GenderIndex = GenderIndex

    # this is porbbly pretty hacky, but it beats typing out names a bunch of times
    # constructs the name of specific body types using indexs
    # example: the body preset for TIF_MS would be [3, 2]
    # for converting bodies form one to another we will loop back around read the indexs twice. 1st pass is the starting body, second pass is the target body
    # example: convert HUM_M to DGB_M would be [0, 0] then [8, 0].
    # not fesable to have a 'to' and 'from' for every combination, so we will instead always start with either HUM_M or HUM_F, and branch from there.
    # not a lot of room for user designed presets, might come up with something for that later\
    BodyDefine = {
        "Race": ["HUM", "ELF", "HEL", "TIF", "GTY", "DWR", "HFL", "GNO", "DGB", "HRC"], #0 - 9
        "Gender": ["M", "F", "MS", "FS"],
        "Part": ["BDY", "FOT", "HND", "TOR", "HED", "SPC"] #redundent for now
    }
    # Reads the inputed numbers and returns the names of the needed armature and action for that body as a list. [0] is the armature [1] is the action
    def LT_ReadBodyName(R, G):
        
        BodyCode = "lt_" + BodyDefine["Race"][R] + "_" + BodyDefine["Gender"][G]
        return BodyCode

    def LT_FindAssets(self):
       
        ReadBodyCode = LT_ReadBodyName(self.RaceIndex, self.GenderIndex)
        Paired = []
        try:
            Paired.append(bpy.data.armatures[ReadBodyCode])
            Paired.append(bpy.data.actions[ReadBodyCode])
        except KeyError:

            print("!!warning!! No matching data found. Reinitialise Lazy Tailor")
                
        return Paired
    

# finds bones with the "child of" constraint, treats them all as active, then runs "set inverse" on all of them
# this is needed because swapping Target_B"s data requires those conrstaints to be reset

def LT_Childof_MassInvert(TargetBone):
    for b in TargetBone.pose.bones:
        for c in b.constraints:
            if c.type == "CHILD_OF":
                context_py = bpy.context.copy()
                context_py["constraint"] = c
                TargetBone.data.bones.active = b.bone                               
                bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")

# "childof_set_inverse" can only run on bones that are visible. All bones in Target_A that have the "child of" constraint are in the group "Deform Bones"
# function checks to see if the bone collection is visible, and if its not makes it visible, runs the function, then sets it invisable again.

def LT_Childof_Validator(TargetSkel, ColName):
    
    CB = TargetSkel.data.collections_all[ColName.name]
    if CB.is_visible == False:
        CB.is_visible = True
    
    LT_Childof_MassInvert(TargetSkel)
    print("CHIDREN INVERTED")
    
    CB.is_visible = False

def LT_BaseRemap(OldBody, NewBody):
    bpy.data.armatures["OldBody"].user_remap(bpy.data.armatures["NewBody"])


class LT_OT_swap_body_type(bpy.types.Operator):
    bl_idname = "lt.swap_body_type"
    bl_label = "Swap Body Type"
    bl_description = "Swaps the Body Type That You Are Fitting too"

    def execute(self, context):
        TestBodyA = "LT_Mannequin_Base"
        TestBodyB = "LT_S_GNO_F"
        LT_BaseRemap(TestBodyA, TestBodyB)

        return {"FINISHED"}

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
        
        return {"FINISHED"}




        