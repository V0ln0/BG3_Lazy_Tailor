# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy



#     LT_Mannequin_Base = bpy.data.objects["LT_Mannequin_Base"]
#     LT_Mannequin = bpy.data.objects["LT_Mannequin"]
#     LT_Mannequin_Base.data = ArmatureFishing(BodyName)
#     Childof_Validator(LT_Mannequin)
#     LT_Mannequin.pose.apply_pose_from_action(ActionFishing(ActionName))

# this class controls what we're converting too
# all current code/presets assume that you are either converting HUM_M/HUM_F to another body type.
# to do: add a way to layer presets ontop of each other
# possible todo: come back and add a frame work to allow converting from other body types to HUM_M/HUM_F instead of just from
class LT_BodyShop:
    
    def __init__(self, Base, Mannequin, BodyArm, PreSet):
        
        self.Base = Base # LT_Mannequin_Base
        self.Mannequin = Mannequin # LT_Mannequin
        self.BodyArm = BodyArm # name(string) of the body armature that we're changing too, not always needed 
        self.PreSet = PreSet # name(string) of the action being called


    def Childof_MassInvert(self, ParentName):
        PN = bpy.data.objects[ParentName]
        for b in PN.pose.bones:
            for c in b.constraints:
                if c.type == "CHILD_OF":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    PN.data.bones.active = b.bone                               
                    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    
    # can't effect constraings on bones that are not visable in the viewport
    def Childof_Validator(self):
        
        CB = bpy.data.armatures[self.Mannequin].collections_all["Deform_Bones"]
        if CB.is_visible == False:
            CB.is_visible = True
        
        self.Childof_MassInvert(self.Mannequin)
        CB.is_visible = False

    def ArmatureFishing(self):
        for A in bpy.data.armatures:
            if A.name == self.BodyArm:
                return A

    def ActionFishing(self):
        for A in bpy.data.actions:
            if A.name == self.PreSet:
                return A

    # def LT_ModeValidator(self):

    #     if bpy.context.active_object.name == self.Mannequin and bpy.context.object.mode == "POSE":
    #         return True
    #     else:
    #         return False

    # def LT_PoseClear(self, CheckBool: bool):
    #     if CheckBool == True:
    #         bpy.ops.pose.user_transforms_clear(only_selected=False)
    #     else:
    #         pass
    
    # def LT_SetBody(self, RestBool: bool):
    #     if RestBool == False:
    #         bpy.data.objects[self.Base].data = self.ArmatureFishing(self.BodyArm)
    #         self.Childof_Validator()
    # def LT_SwapBase(self, RestCheck: bool):
        
    #     if RestCheck == False
    #         bpy.data.objects[self.Base].data = self.ArmatureFishing(self.BodyArm)

    # def BodySwap(self, NeedsSwap=True, KeepPose=False, NeedsRest=False):


    def BodySwap(self):
        
        bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.Base].data = self.ArmatureFishing()
        self.Childof_Validator()
        bpy.data.objects[self.Mannequin].pose.apply_pose_from_action(self.ActionFishing())

        

# bpy.ops.pose.user_transforms_clear(only_selected=False)


class LT_OT_swap_body_type(bpy.types.Operator):
    bl_idname = "lt.swap_body_type"
    bl_label = "Swap Body Type"
    bl_description = "Swaps the Body Type That You Are Fitting too"

    def execute(self, context):



        GTY_M = LT_BodyShop("LT_Mannequin_Base", "LT_Mannequin", "LT_HUM_M", "LT_GTY_M_BDY")
        GTY_M.BodySwap()
        return {"FINISHED"}





# class LT_OT_set_rest_pose(bpy.types.Operator):
    
#     bl_idname = "lt.set_rest_pose"
#     bl_label = "Set New Rest Pose"
#     bl_description = "Sets the current pose of the active armature as its new Rest Pose AKA 'defualt postion'."


#     #  sets the current postion of bones as the new rest pose 
#     #  used for changing what the starting body type is

#     def execute(self, context):
#         current_mode = bpy.context.object.mode
#         ACT_OB = bpy.context.active_object
        
#         if ACT_OB.name == ("Mannequin_BT1") and current_mode == "POSE":
#             bpy.ops.pose.armature_apply(selected=False)
        
#         return {"FINISHED"}





# WE SCRAPPING THIS FOR NOW. May come in handy later
# this thing is for finding the same of specific assets(armatures + actions) in the file
# class LT_BodyManager:
#     def __init__(self, RaceIndex, GenderIndex, HRTIndex):
        
#         self.RaceIndex = RaceIndex
#         self.GenderIndex = GenderIndex
#         self.HRTIndex = HRTIndex

#     # this is porbbly pretty hacky, but it beats typing out names a bunch of times
#     # constructs the name of specific body types using indexs
#     # example: the body preset for TIF_MS would be [3, 2, 0]
#     # for converting bodies form one to another we will loop back around read the indexs twice. 1st pass is the starting body, second pass is the target body
#     # example: convert HUM_M to DGB_M would be [0, 0, 0] then [8, 0, 0].
#     # not feasible//. to have a 'to' and 'from' for every combination, so we will instead always start with either HUM_M or HUM_F, and branch from there.
#     # not a lot of room for user designed presets, might come up with something for that later\
#     BodyDefine = {
#         "Race": ["HUM", "ELF", "HEL", "TIF", "GTY", "DWR", "HFL", "GNO", "DGB", "HRC"], #0 - 9
#         "Gender": ["M", "F", "MS", "FS"],
#         "HRT": ["CIS", "FTM", "MTF"],
#         "Part": ["BDY", "FOT", "HND", "TOR", "HED", "SPC"] 
#     }
#     # Reads the inputed numbers and returns the names of the needed armature and action for that body as a list. [0] is the armature [1] is the action
#     def LT_ReadBodyName(R, G, H, P):
        
#         if H == 0:
#             BodyCode = "lt_" + BodyDefine["Race"][R] + "_" + BodyDefine["Gender"][G] + BodyDefine["Part"][P]
#         else:
#             BodyCode = "lt_" + BodyDefine["Race"][R] + "_" + BodyDefine["Gender"][G] + "_" + BodyDefine["HRT"][H]
#         return BodyCode

#     def LT_FindAssets(self):
         
#         ReadBodyCode = LT_ReadBodyName(self.RaceIndex, self.GenderIndex, self.HRTIndex)
#         Paired = []

#         try:
#             Paired.append(bpy.data.armatures[ReadBodyCode])
#             Paired.append(bpy.data.actions[ReadBodyCode])
#         except KeyError:

#             print("!!warning!! No matching data found. Reinitialise Lazy Tailor")
#         return Paired
