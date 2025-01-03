# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy
import enum
from enum import Enum



# workflow:
# "Local_Mannequin" (LM) copies bone postions from "Local_Mannequin_Base" (LMB) via bone constraints in pose space
# fully weighted mesh(s) has armature modifer targeting LM
# LM's bone constraints target OBJECT LMB(OBJ) NOT the ARMATURE DATA LMB(ARM)
# this allowes LMB(OBJ)'s armature data to be swapped with another armature with the same bone hirachy(ie HUM_M to HUM_MS)
# when this happens, LM constrained bones snap to the new postion of LMB(OBJ)'s bones
# because this happens in pose space, this in turn snaps the mesh into a new postion.
# LM has additional controll bones + constraints that allow the user to further form the mesh by armature defromation.
# after LMB(ARM) has been swapped, a preset action(pose) is applied on top of the existing deformations to tweak the end result. which action is user defined.
# user then applies the armature deformation modifer on the meesh to finalise the result.

#step by step:
# clear all user transfroms -> deselect all other objects -> make LM avtive obj -> swap LMB(ARM) data -> set inverse on all "child of" constraints in LM -> apply action preset

# class contains functions needed to control the swapping of presets/armatures
# current code/presets assume that you are either converting HUM_M/HUM_F to another body type.
# possible todo: come back and add a frame work to allow converting from other body types to HUM_M/HUM_F instead of just from
class LT_BodyShop:
    
    def __init__(self, PreSet, BodyArm):
        
        self.PreSet = PreSet # name(string) of the action being called
        self.BodyArm = BodyArm # name(string) of the body armature that we're changing too, not always needed 
    
    LMB = "Local_Mannequin_Base"
    LM = "Local_Mannequin"
    
    # upon swapping armature data, the 'childof' constraints need to have their inverse set again, lest you wish to see some sort of demonic gibon
    def Childof_MassInvert(self):
        PN = bpy.data.objects[self.LM]
        for b in PN.pose.bones:
            for c in b.constraints:
                if c.type == "CHILD_OF":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    PN.data.bones.active = b.bone                               
                    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    
    # can't effect constraints on bones that are not visable in the viewport
    def Childof_Validator(self):
        
        CB = bpy.data.armatures[self.LM].collections["Deform_Bones"]
        if CB.is_visible == False:
            CB.is_visible = True
        
        self.Childof_MassInvert()
        CB.is_visible = False

    def ApplyPreSet(self, Is_Addative=False): #"Is_Addative" for when applying a preset on top of existing deformations without clearing them
        
        bpy.ops.pose.select_all(action='DESELECT')
        if Is_Addative == False:
            bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LM].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])

    def FullReset(self): #used to completely reset the LMB back to its defualt
        
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.LMB]
        self.Childof_Validator()
        bpy.ops.pose.armature_apply(selected=False)

    def SwapSkeleton(self, Needs_Rest=False):

        bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.BodyArm]
        self.Childof_Validator()
        
        if Needs_Rest == True:
            bpy.ops.pose.armature_apply(selected=False)
            #"Needs_Rest" is for when a new rest pose needs to be appiled to the armatrue
            # rest pose is the defualt postion of bones, mainly needed for when converting an outfit that is not fitted to the current armature.
            # converting armour that was made to fit HUM_M, LM's rest pose needs to be HUM_M
            # if the armour was made to fit GNO_F, then the rest pose needs to be GNO_F
    
    # functions sperated out like this so that we are able to call on indvidual parts
    def BodySwap(self): 
                                    
        self.SwapSkeleton()
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.objects[self.LM].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])


def Active_Check(ObjName): # norb's hell
    
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
    except RuntimeError:
        bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
    
    bpy.ops.object.select_pattern(pattern=ObjName, extend=False)
    bpy.ops.object.mode_set(mode="POSE")

#pattern for tuple (PRESET_NAME, SKELENTON)
class F_PreSets(Enum):

    GTY = ("LT_GTY_F_BDY", "LT_HUM_F_BASE")
    HUM_S = ("LT_HUM_FS_BDY", "LT_HUM_FS_BASE")
    DGB = ("LT_DGB_F_BDY", "LT_HUM_FS_BASE")
    GNO = ("LT_GNO_F_BDY", "LT_SHORT_F_BASE")
    HFL = ("LT_HFL_F_BDY", "LT_SHORT_F_BASE")
    DWR = ("LT_DWR_F_BDY", "LT_DWR_F_BASE")
    HRT = ("LT_HUM_F_FTM", "LT_HUM_M_BASE")
    
class M_PreSets(Enum):
    
    GTY = ("LT_GTY_M_BDY", "LT_HUM_M_BASE")
    HUM_S = ("LT_HUM_MS_BDY", "LT_HUM_MS_BASE")
    DGB = ("LT_DGB_M_BDY", "LT_HUM_MS_BASE")
    GNO = ("LT_GNO_M_BDY", "LT_SHORT_M_BASE")
    HFL = ("LT_HFL_M_BDY", "LT_SHORT_M_BASE")
    DWR = ("LT_DWR_M_BDY", "LT_DWR_M_BASE")
    HRT = ("LT_HUM_M_MTF", "LT_HUM_F_BASE")


class LT_OT_set_base_tailor(bpy.types.Operator):

    bl_idname = "lt.set_base_tailor"
    bl_label = "Set Base"
    bl_description = "Changes the resting postion of the mannequin to the body type selected in 'From:'"

    def execute(self, context):
        
        tailor_props = bpy.context.scene.tailor_props
        Active_Check(tailor_props.mannequin_form)
        SewingPattern = LT_BodyShop(
            PreSet=("NONE"),
            BodyArm=("LT_" + (tailor_props.from_body) + "_BASE")
            )
        
        SewingPattern.SwapSkeleton(Needs_Rest=True)
  
        return {"FINISHED"}
    
class LT_OT_defualt_preset_tailor(bpy.types.Operator):

    bl_idname = "lt.defualt_preset_tailor"
    bl_label = "Apply Pre-Set"
    bl_description = "Applies the pre-set selected in 'To:' to the Mannequin. WARNING: will clear all user transforms"


    def execute(self, context):
        
        tailor_props = bpy.context.scene.tailor_props
        Active_Check(tailor_props.mannequin_form)

        if tailor_props.from_body == "HUM_M":
            Codebook = M_PreSets[tailor_props.to_body]
        else:
            Codebook = F_PreSets[tailor_props.to_body]
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = LT_BodyShop(
            
            PreSet=Codebook.value[0], 
            BodyArm=Codebook.value[1])
        
        SewingPattern.BodySwap()
        
        return {"FINISHED"}


class LT_OT_mannequin_reset(bpy.types.Operator):

    bl_idname = "lt.mannequin_reset"
    bl_label = "Mannequin Reset"
    bl_description = "Sets the Mannequin back to a nuteral state"

    def execute(self, context):

        Active_Check(bpy.context.scene.tailor_props.mannequin_form)

        LT_BodyShop(PreSet=("NONE"), BodyArm=("NONE")).FullReset()
        return {"FINISHED"}



# gonna use this for applying user defined presets
# instead of searching by name we're gonna add a short ID to the start of the action name, and use those numbers as instructions on how to apply the preset
# not sure how many numbers so far the pattern is 
# we playing fucking Enum Plinko here
class Preset_Type(Enum): 
    
    Body_Refit_no_rest = 1 #default type, swaps the body but dose not set a new rest postion
    Body_Refit_with_rest = 2 #swaps body and sets a new rest pose
    Layered = 3 # changes nothing about the armature and instead blends the preset with the existing deformations


class F_Skeletons(Enum): 
    
    LT_HUM_F = 1
    LT_HUM_FS = 2
    LT_SHORT_F = 3
    LT_DWR_F = 4

class M_Skeletons(Enum):
    
    LT_HUM_M = 1
    LT_HUM_MS = 2
    LT_SHORT_M = 3
    LT_DWR_M = 4


# class LT_OT_mannequin_reset(bpy.types.Operator):

#     bl_idname = "lt.apply_user_action"
#     bl_label = "apply_user_action"
#     bl_description = "Sets the Mannequin back to a nuteral state"


#     def execute(self, context):
        
#         return {"FINISHED"}
# #Action name is something like 1204_WHATEVERRRRRRRRRR
# class LT_ReadCode:

#     def __init__(self, ActionName):
#         self.ActionName = ActionName

#     def GetBones(self):
        
#         Bones = []
#         Code = self.ActionName[1:4]

#         if Code[0] == 0:
#             Bones.append(F_Skeletons(Code[1]).name)
#         else:
#             Bones.append(M_Skeletons(Code[1]).name)

#         if Code[2] == 0:
#             Bones.append(F_Skeletons(Code[3]).name)
#         else:
#             Bones.append(M_Skeletons(Code[3]).name)

#         return Bones
        


