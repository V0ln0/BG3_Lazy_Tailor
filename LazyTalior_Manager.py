# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy
import enum
from enum import Enum
from . LazyTalior_utils import *




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
    
    def __init__(self, PreSet='', BodyArm='', LMB='Local_Mannequin_Base', LM='Local_Mannequin', Needs_Rest=False):
        
        self.PreSet = PreSet # name(string) of the action being called
        self.BodyArm = BodyArm # name(string) of the body armature that we're changing too, not always needed 
        self.LMB = LMB
        self.LM = LM
        self.Needs_Rest = Needs_Rest
    # upon swapping armature data, the 'childof' constraints need to have their inverse set again, lest you wish to see some sort of demonic gibon
    def child_of_mass_invert(self):
        PN = bpy.data.objects[self.LM]
        for b in PN.pose.bones:
            for c in b.constraints:
                if c.type == "CHILD_OF":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    PN.data.bones.active = b.bone                               
                    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    
    def stretch_to_mass_set(self): #todo: merge this and the above into one
        PN = bpy.data.objects[self.LM]
        for b in PN.pose.bones:
            for c in b.constraints:
                if c.type == "STRETCH_TO":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    PN.data.bones.active = b.bone                               
                    bpy.ops.constraint.stretchto_reset(constraint="Stretch To", owner='BONE')

    # can't effect constraints on bones that are not visable in the viewport
    def BoneVis_Validator(self, stretch_To=False):
        
        CB = bpy.data.armatures[self.LM].collections["Deform_Bones"]
        if CB.is_visible == False:
            CB.is_visible = True
        
        self.child_of_mass_invert()
        
        if stretch_To == True: #only needs to be true when also applying a new rest pose
            self.stretch_to_mass_set() 
        
        CB.is_visible = False

    def ApplyPreSet(self, Is_Addative=False): #"Is_Addative" for when applying a preset on top of existing deformations without clearing them
        
        bpy.ops.pose.select_all(action='DESELECT')
        if Is_Addative == False:
            bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LM].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])

    def FullReset(self): #used to completely reset the LMB back to its defualt
        
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.LMB]
        self.BoneVis_Validator(stretch_To=True)
        bpy.ops.pose.armature_apply(selected=False)

    def SwapSkeleton(self):

        bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.BodyArm]
        self.BoneVis_Validator()
        
        if self.Needs_Rest == True:
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

        tailor_props = context.scene.tailor_props
        LT_active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = LT_BodyShop(
            BodyArm=("LT_" + (tailor_props.from_body) + "_BASE"),
            Needs_Rest=True
            )

        SewingPattern.SwapSkeleton()
  
        return {"FINISHED"}
    
class LT_OT_defualt_preset_tailor(bpy.types.Operator):

    bl_idname = "lt.defualt_preset_tailor"
    bl_label = "Apply Pre-Set"
    bl_description = "Applies the pre-set selected in 'To:' to the Mannequin. WARNING: will clear all user transforms"


    def execute(self, context):

        
        tailor_props = context.scene.tailor_props
        
        LT_active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")

        if tailor_props.from_body == "HUM_M":
            Codebook = M_PreSets[tailor_props.to_body]
        else:
            Codebook = F_PreSets[tailor_props.to_body]
        
        SewingPattern = LT_BodyShop(
            
            PreSet=Codebook.value[0], 
            BodyArm=Codebook.value[1])
        
        SewingPattern.BodySwap()
        
        return {"FINISHED"}


class LT_OT_mannequin_reset(bpy.types.Operator):

    bl_idname = "lt.mannequin_reset"
    bl_label = "Mannequin Reset"
    bl_description = "Sets the Mannequin back to its defualt state or clears user changes"


    def execute(self, context):

        
        LT_active_check.force_active()
        
        bpy.ops.object.mode_set(mode="POSE")
        LT_BodyShop(PreSet=("NONE"), BodyArm=("NONE")).FullReset()
        return {"FINISHED"}



def LT_Action_Error_Popup():

    def draw(self, context):
       
        self.layout.label(text="There is an issue with the Pre_Set identifier")
        self.layout.label(text="Please check the addon manual for vaild naming conventions, and try again")

    bpy.context.window_manager.popup_menu(draw, title = "Warning: Pre_Set identifier invalid", icon = 'ERROR')

# PRESET PATTERN EXAMPLE: 
# "TYPE INT" + "-"+ "FEM/MASC INT" + "SKELENTON INT" + "_" + "FEM/MASC INT" + "SKELENTON INT" + "_" + "USER DEFINED NAME"
#first skelenton is the FROM armature, second is the TO armature
# LT_GTY_F_BDY would be: A_AA_AA_GTY_F_BDY 

class LT_user_codebook:

    def __init__(self, ActionName):
        
        self.ActionName = ActionName

    def read_code(self, int_a, int_b,):
        
        Category = Enum('Category', [('Group_Fem', 0), ('Group_Masc', 1)])
        Types = Enum('Types', [('HUM', 0), ('HUM_S', 1), ('SHORT', 2), ('DWR', 3)])

        Armature_Groups = {
            
            Category.Group_Fem: {
                
                Types.HUM: "LT_HUM_F_BASE",
                Types.HUM_S: "LT_HUM_FS_BASE",
                Types.SHORT: "LT_SHORT_F_BASE",
                Types.DWR: "LT_DWR_F_BASE",    
            },

            Category.Group_Masc: {
                
                Types.HUM: "LT_HUM_M_BASE",
                Types.HUM_S: "LT_HUM_MS_BASE",
                Types.SHORT: "LT_SHORT_M_BASE",
                Types.DWR: "LT_DWR_M_BASE", 
            } 
        }
        
        try:
            return Armature_Groups[Category(int(int_a))][Types(int(int_b))]
        
        except ValueError:
            LT_Action_Error_Popup()
            pass

    def read(self):
        
        Code = self.ActionName[0:7].replace('_','')
        return tuple((self.read_code(int(Code[1]), int(Code[2])), self.read_code(int(Code[3]), int(Code[4]))))


class LT_OT_apply_user_preset(bpy.types.Operator):

    bl_idname = "lt.apply_user_preset"
    bl_label = "User Preset"
    bl_description = "Sets the Mannequin back to its defualt state or clears user changes"

    Action_Name: bpy.props.StringProperty(
        name="Action_Name",
        default="",
    )

    def execute(self, context):
        
        
        LT_active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")

        ReadCode = LT_user_codebook(self.Action_Name).read()

        if action_type == 1:

            LT_BodyShop(PreSet=self.Action_Name, BodyArm=ReadCode[0]).ApplyPreSet(Is_Addative=True)

        if action_type == 2:
            
            LT_BodyShop(PreSet=self.Action_Name, BodyArm=ReadCode[1]).SwapSkeleton(self, Needs_Rest=False)
            LT_BodyShop(PreSet=self.Action_Name, BodyArm=ReadCode[0]).ApplyPreSet()
            
        return {"FINISHED"}



