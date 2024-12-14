# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy
import enum
# this class controls what we're converting too
# all current code/presets assume that you are either converting HUM_M/HUM_F to another body type.
# to do: add a way to layer presets ontop of each other
# possible todo: come back and add a frame work to allow converting from other body types to HUM_M/HUM_F instead of just from

# todo: merge LT_BodyShop and LT_OT_swap_body_type
class LT_BodyShop:
    
    def __init__(self, Base, Mannequin, BodyArm, PreSet):
        
        self.Base = Base # LT_Mannequin_Base
        self.Mannequin = Mannequin # LT_Mannequin
        self.BodyArm = BodyArm # name(string) of the body armature that we're changing too, not always needed 
        self.PreSet = PreSet # name(string) of the action being called

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

 
    def BodySwap(self, Clear: bool):
   
        bpy.data.objects[self.Base].data = bpy.data.armatures[self.BodyArm]
        if Clear == True:
            bpy.ops.pose.user_transforms_clear(only_selected=False)
        self.Childof_Validator()
        bpy.data.objects[self.Mannequin].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])
        if self.PreSet.endswith("_MTF") or self.PreSet.endswith("_FTM"):
            bpy.ops.pose.armature_apply(selected=False)



# Uses the string props from LazyTalior_Prop.py as an input
# props stored outside of the opporator so that settings like the body type and preset can be displayed in the UI

class LT_OT_swap_body_type(bpy.types.Operator):

    bl_idname = "lt.swap_body_type"
    bl_label = "Apply Preset"
    bl_description = "Swaps the Body Type That You Are Fitting too"

    def execute(self, context):
        
        lt_props = bpy.context.scene.lt_props
        bpy.ops.object.select_pattern(pattern=(lt_props.mannequin_form), extend=False)
        bpy.context.view_layer.objects.active = bpy.data.objects[lt_props.mannequin_form]
        bpy.ops.object.mode_set(mode="POSE")


        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = LT_BodyShop(lt_props.mannequin_base, lt_props.mannequin_form, lt_props.body_type, lt_props.body_preset)
        SewingPattern.BodySwap()
        return {"FINISHED"}


# used to look up the names of assets with indexs instead of writting them out as individual strings
# Right now (v1.0.0), its a bit of an unnecessary and overengineered mess tbh 
# but my hope is that later on it will make it easier for users to add custom content to the addon, without having to manualy edit the code

# class RaceName(enum.Enum):
#     HUM = 1
#     ELF = 2
#     HEL = 3
#     TIF = 4
#     GTY = 5
#     DWR = 6
#     GNO = 7
#     HFL = 9
#     DGB = 10
#     HRC = 11


# class Base_Key(enum.Enum): #some races share armatures, whats using what is defined below
#     HUM_M = 1
#     HUM_F = 2
#     HUM_MS = 3
#     HUM_FS = 4
#     SHORT_M = 5
#     SHORT_F = 6
#     DWR_M = 7
#     DWR_F = 8


class LT_BodyDefine:

    def __init__(self, Race, Type, Part, Skeleton_Key):
        
        self.Race = Race
        self.Type = Type
        self.Part = Part
        self.Skeleton_Key = Skeleton_Key
    
    # I actualy have no idea why I typed this out or if its even helpfull,
    # Skeleton_Key = {
        
    #     Base_Key.HUM_M: ["HUM_M", "ELF_M", "HEL_M", "TIF_M", "GTY_M"],
    #     Base_Key.HUM_F: ["HUM_F", "ELF_F", "HEL_F", "TIF_F", "GTY_F"],
    #     Base_Key.HUM_MS: ["HUM_MS", "ELF_MS", "HEL_MS", "TIF_MS", "DGB_M", "HRC_M"], 
    #     Base_Key.HUM_FS: ["HUM_FS", "ELF_FS", "HEL_FS", "TIF_FS", "DGB_F", "HRC_F"],
    #     Base_Key.SHORT_M: ["GNO_M", "HFL_M"],
    #     Base_Key.SHORT_F: ["GNO_F", "HFL_F"],
    #     Base_Key.DWR_M: ["DWR_M"],
    #     Base_Key.DWR_F: ["DWR_F"],
    # }

    CodeBook = {
        
        "Race": ["ANY", "HUM", "ELF", "HEL", "TIF", "GTY", "DWR", "GNO", "HFL", "DGB", "HRC"],
        "Type": ["M", "F", "MS", "FS"], 
        "Part": ["BDY", "FOT", "HND", "TOR", "HED", "SPC", "FTM", "MTF"],
        "Skeleton": ["USER", "HUM_M", "HUM_F", "HUM_MS", "HUM_FS", "DWR_M", "DWR_F", "GNO_M", "GNO_F"]
        # Skeleton_Key exists because some races share armatures
        # hacky as hell this was the easiest way to accomodate for it without a bunch of if statements
        # masc dragonborn being called "DGB_M" dispite using the "HUM_MS" armature was a pain in my ass
    }

    def ReadName(self):

        NameCode = self.CodeBook["Race"][self.Race] + "_" + self.CodeBook["Type"][self.Type]
        return NameCode
    
    def ReadBones(self):
        
        Bonescode = "LT_" + self.CodeBook["Skeleton"][self.Skeleton_Key]
        return Bonescode
    
    def ReadAction(self):
        
        ActionCode = "LT_" + self.CodeBook["Race"][self.Race] + "_" + self.CodeBook["Type"][self.Type] + "_" + self.CodeBook["Part"][self.Part]
        return ActionCode
    
    def ReadCode(self):
        
        PairedNames = []
        PairedNames.append(self.ReadName())
        PairedNames.append(self.ReadBones())
        PairedNames.append(self.ReadAction())
        return PairedNames 


# Takes indexs, feeds it through LT_BodyDefine, changes lt_props vaules.
# User then triggers lt.swap_body_type to apply the preset to LT_Mannequin
# set up this way to prevent the user from miscliking and undoing their work
class LT_OT_type_set(bpy.types.Operator):
   
    bl_idname = "lt.type_set"
    bl_label = "type_set"
    bl_description = "Description that shows in blender tooltips"

    Race_Index: bpy.props.IntProperty(
        name="Race_Index",
        description='Race',
        default=0,
        min=0,
        max=(len(LT_BodyDefine.CodeBook["Race"]))
    )

    Type_Index: bpy.props.IntProperty(
        name="Type_Index",
        description='Type',
        default=0,
        min=0,
        max=(len(LT_BodyDefine.CodeBook["Type"]))
    )

    Part_Index: bpy.props.IntProperty(
        name="Part_Index",
        description='Part',
        default=0,
        min=0,
        max=(len(LT_BodyDefine.CodeBook["Part"]))
    )

    Skeleton_Index: bpy.props.IntProperty(
        name="Skeleton_Index",
        description='Skeleton',
        default=0,
        min=0,
        max=(len(LT_BodyDefine.CodeBook["Race"]))
    )

    def execute(self, context):
        lt_props = bpy.context.scene.lt_props

        PropSet = LT_BodyDefine(self.Race_Index, self.Type_Index, self.Part_Index, self.Skeleton_Index)
        Codes = PropSet.ReadCode()
        
        lt_props.current_target =Codes[0] #currently dosen't account for FTM/MTF. I fucking programed missgenderng into Blender fml
        lt_props.body_type = Codes[1]
        lt_props.body_preset = Codes[2]
        

        return {"FINISHED"}



