# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy
import enum
from enum import Enum

# class contains functions needed to control the swapping of presets/armatures
# current code/presets assume that you are either converting HUM_M/HUM_F to another body type.

# possible todo: come back and add a frame work to allow converting from other body types to HUM_M/HUM_F instead of just from

# todo: merge LT_BodyShop and LT_OT_swap_body_type
class LT_BodyShop:
    
    def __init__(self, Base, Mannequin, PreSet, BodyArm):
        self.Base = Base
        self.Mannequin = Mannequin
        self.PreSet = PreSet # name(string) of the action being called
        self.BodyArm = BodyArm # name(string) of the body armature that we're changing too, not always needed 

    # upon swapping armature data, the 'childof' constraints need to have their inverse set again, lest you wish to see some sort of demonic gibon
    def Childof_MassInvert(self):
        PN = bpy.data.objects[self.Mannequin]
        for b in PN.pose.bones:
            for c in b.constraints:
                if c.type == "CHILD_OF":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    PN.data.bones.active = b.bone                               
                    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    
    # can't effect constraints on bones that are not visable in the viewport
    def Childof_Validator(self):
        
        CB = bpy.data.armatures[self.Mannequin].collections_all["Deform_Bones"]
        if CB.is_visible == False:
            CB.is_visible = True
        
        self.Childof_MassInvert()
        CB.is_visible = False

    def ApplyPreSet(self, Is_Addative: bool): #"Is_Addative" for when applying a preset on top of existing deformations without clearing them
        
        if Is_Addative == False:
            bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.Mannequin].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])

    def ResetBody(self): #for cleaing up the Mannequin
        
        bpy.data.objects[self.Base].data = bpy.data.armatures[self.BodyArm]
        bpy.ops.pose.user_transforms_clear(only_selected=False)

    def BodySwap(self, Needs_Bone_Swap=True, Needs_Rest=False): 
                                    
        if Needs_Bone_Swap == True:
            self.ResetBody()
        
        if Needs_Rest == True: 
            bpy.ops.pose.armature_apply(selected=False)
        #"Needs_Rest" is for when a new rest pose needs to be appiled to the armatrue
        # rest pose is the defualt postion of bones, mainly needed for when converting FROM HUM_M --> HUM_F or vice versa  
        # would also be need for converting something like GNO_M to HUM_M
        self.Childof_Validator()
        


def Active_Check(ObjName): # norb's hell
    
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
    bpy.ops.object.mode_set(mode="POSE")

class LT_OT_defualt_preset_tailor(bpy.types.Operator):

    bl_idname = "lt.defualt_preset_tailor"
    bl_label = "Apply Preset"
    bl_description = "Swaps the Body Type That You Are Fitting too"

    #pattern for tuple (PRESET_NAME, SKELENTON)
    class F_PreSets(Enum):
    
        GTY = ("LT_GTY_F_BDY", "LT_HUM_F")
        HUM_S = ("LT_HUM_FS_BDY", "LT_HUM_FS")
        DGB = ("LT_DGB_F_BDY", "LT_HUM_FS")
        GNO = ("LT_GNO_F_BDY", "LT_SHORT_F")
        HFL = ("LT_HFL_F_BDY", "LT_SHORT_F")
        DWR = ("LT_DWR_F_BDY", "LT_DWR_F")

    class M_PreSets(Enum):
        
        GTY = ("LT_GTY_M_BDY", "LT_HUM_M")
        HUM_S = ("LT_HUM_MS_BDY", "LT_HUM_MS")
        DGB = ("LT_DGB_M_BDY", "LT_HUM_MS")
        GNO = ("LT_GNO_M_BDY", "LT_SHORT_M")
        HFL = ("LT_HFL_M_BDY", "LT_SHORT_M")
        DWR = ("LT_DWR_M_BDY", "LT_DWR_M")
        
    def execute(self, context):
        
        tailor_props = bpy.context.scene.tailor_props
        Active_Check(tailor_props.mannequin_form)

        if tailor_props.from_body == "HUM_M":
            Codebook = self.M_PreSets[tailor_props.to_body]
        else:
            Codebook = self.F_PreSets[tailor_props.to_body]
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = LT_BodyShop(
            
            tailor_props.mannequin_base, 
            tailor_props.mannequin_form, 
            Codebook.value[0], 
            Codebook.value[1])
        
        SewingPattern.BodySwap()
        
        return {"FINISHED"}


class LT_OT_body_reset(bpy.types.Operator):
    
    bl_idname = "lt.body_reset"
    bl_label = "Mannequin Reset"
    bl_description = "Sets the Mannequin back to a nuteral state"
    

    Type_Bool: bpy.props.BoolProperty(
        name="Type_Bool",
        description='If true, sets the Mannequin to HUM_F, HUM_M if false ',
        default=False,
    )

    def execute(self, context):
        tailor_props = bpy.context.scene.tailor_props
        if self.Type_bool == False:
            SewingPattern = LT_BodyShop(tailor_props.mannequin_base, tailor_props.mannequin_form, "HUM_F")
        else:
            SewingPattern = LT_BodyShop(tailor_props.mannequin_base, tailor_props.mannequin_form, "HUM_M")
        
        SewingPattern.ResetBody()
