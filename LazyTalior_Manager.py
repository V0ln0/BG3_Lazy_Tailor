import bpy
import enum
from enum import Enum


'''
HOW THIS WORKS: MANNEQUINS ARE LIKE ONIONS
    
    LM = Local_Mannequin
    LMB = Local_Mannequin_Base

    ┌─────┐      ┌─────┐      ┌─────┐
    │ LM  │ ←――― │ LMB │ ←――― │ LMB │ ←―――→  POOL OF ARMATURE DATA 
    │(OBJ)│      │(OBJ)│      │(ARM)│       WITH SAME BONE HIERARCHY             
    └─────┘      └─────┘      └─────┘        BUT DIFFERNT LOCATIONS                          
      │ ↑
      │ └――――――― POSE APPLIED ON TOP OF LM (OBJ)     
      ↓          TO BETTER CONTROL DEFORMATION                 
    ┌─────┐
    │MESH │ 
    └─────┘
    
    bones in LM (OBJECT) copy bone postions in LMB (OBJECT) (!!SPECIFICALY OBJECT!!) using pose mode bone constraints/drivers
    LMB (DATA) is swapped with another data block with the same bone hierachy, but differnt locations. (ie, HUM_F to DWR_F)
    LMB (OBJECT)'s bones then change postion to match the new data
    LM (OBJECT)'s constraints make it match the updated postions in POSE SPACE (some constraints need to be reset when this happens)
    because this happens in POSE SPACE, it will deform meshes targeting LM (OBJECT) acordingly, thus "snapping" the mesh from one armature to another
    A "Pre-Set" (an Action), applied as a pose on LMB (OBJECT) to better controll the deformation, controll bones then allow futher tweaking of final result
    
'''
#step by step:
# clear all user transfroms -> deselect all other objects -> make LM avtive obj -> swap LMB(ARM) data -> set inverse on all "child of" constraints in LM -> apply action preset
# class contains functions needed to control the swapping of presets/armatures
class BodyShop:
    #TODO: ask Nav about cleaning this up
    def __init__(self, PreSet='', from_Arm='', to_Arm='', LMB='Local_Mannequin_Base', LM='Local_Mannequin'):
        
        self.PreSet = PreSet # name(string) of the action being called
        self.from_Arm = from_Arm #name(string) of the body armature that we're changing from, not always needed 
        self.to_Arm = to_Arm # name(string) of the body armature that we're changing too, not always needed 
        self.LMB = LMB
        self.LM = LM

    
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
    
    def stretch_to_mass_set(self): #NOTE: not sure if this is actualy needed
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

    def set_base(self):
        bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.from_Arm]
        
        #LM then needs to be corrected
        self.BoneVis_Validator()
        bpy.ops.pose.armature_apply(selected=False)
        #sets new rest pose, was originaly optional as its not always nessiscary but its better to just do it everytime than constantly check
    
    def change_base(self):

        bpy.ops.pose.user_transforms_clear(only_selected=False)
        bpy.data.objects[self.LMB].data = bpy.data.armatures[self.to_Arm]

        #LM then needs to be corrected
        self.BoneVis_Validator()


    # functions sperated out like this so that we are able to call on indvidual parts
    def BodySwap(self): 
        
        self.set_base()                           
        self.change_base()
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.objects[self.LM].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])


class active_check:

    def force_active(ObjName='Local_Mannequin'): # norb's hell
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        except RuntimeError:
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        
        bpy.ops.object.select_pattern(pattern=ObjName, extend=False)


class LT_OT_mannequin_reset(bpy.types.Operator):

    bl_idname = "lt.mannequin_reset"
    bl_label = "Mannequin Reset"
    bl_description = "Sets the Mannequin back to its defualt state or clears user changes"


    def execute(self, context):

        active_check.force_active()
        
        bpy.ops.object.mode_set(mode="POSE")
        BodyShop().FullReset()
        return {"FINISHED"}

class LT_OT_constraints(bpy.types.Operator):

    bl_idname = "lt.constraints"
    bl_label = "BONE ZONE"
    bl_description = "Manual fix for stretch_to and child_of constaints when swaping armatures"
    
    stretch_to_bool: bpy.props.BoolProperty(
        name="stretch_to_bool",
        default=False
        )

    def execute(self, context):

        BodyShop().BoneVis_Validator(stretch_To=self.stretch_to_bool)
        
        return {"FINISHED"}


#TODO: fix this
class LT_OT_set_base_tailor(bpy.types.Operator):

    bl_idname = "lt.set_base_tailor"
    bl_label = "Set Base"
    bl_description = "Changes the resting postion of the mannequin to the body type selected in 'From:'"


    
    def execute(self, context):

        lt_util_props = context.scene.lt_util_props
        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = BodyShop(
            to_Arm=("LT_" + (lt_util_props.from_body) + "_BASE"),
            )

        SewingPattern.set_base()
  
        return {"FINISHED"}
    



class LT_OT_defualt_preset_tailor(bpy.types.Operator):

    bl_idname = "lt.defualt_preset_tailor"
    bl_label = "Apply Pre-Set"
    bl_description = "Applies the pre-set selected in 'To:' to the Mannequin. WARNING: will clear all user transforms"

    #NOTE: this is dumb but I want the defualt presets to be as easy to use as possible for the enduser 
    #that means putting the training wheels on

    #god damn blender restricting bpy.data
    class F_PreSets(Enum):

        GTY ="LT_GTY_F_BDY"
        HUM_S = "LT_HUM_FS_BDY"
        DGB = "LT_DGB_F_BDY"
        GNO = "LT_GNO_F_BDY"
        HFL = "LT_HFL_F_BDY"
        DWR = "LT_DWR_F_BDY"
        HRT = "LT_HUM_F_FTM"
    
    class M_PreSets(Enum):
    
        GTY = "LT_GTY_M_BDY"
        HUM_S = "LT_HUM_MS_BDY"
        DGB = "LT_DGB_M_BDY"
        GNO = "LT_GNO_M_BDY"
        HFL = "LT_HFL_M_BDY"
        DWR = "LT_DWR_M_BDY"
        HRT = "LT_HUM_M_MTF"


    def execute(self, context):

        lt_util_props = context.scene.lt_util_props
        
        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")

        if lt_util_props.from_body == "HUM_F":
            Codebook = bpy.data.actions[self.F_PreSets[lt_util_props.to_body].value]
        else:
            Codebook = bpy.data.actions[self.M_PreSets[lt_util_props.to_body].value]
        
        SewingPattern = BodyShop(
            
            PreSet=Codebook.name,
            from_Arm=Codebook['LT_From_Body'], 
            to_Arm=Codebook['LT_To_Body']
            )
        
        SewingPattern.BodySwap()
        
        return {"FINISHED"}

def Error_Popup(pop_title: str, error_reason: str, suggestion: str):

    def draw(self, context):
       
        self.layout.label(text=error_reason)
        self.layout.label(text=suggestion)
        
    bpy.context.window_manager.popup_menu(draw, title = pop_title, icon = 'ERROR')


#TODO: this is not finished
class LT_OT_apply_user_preset(bpy.types.Operator):

    bl_idname = "lt.apply_user_preset"
    bl_label = "User Preset"
    bl_description = "Applies a user defined preset to Local_Mannequin"


    def execute(self, context):
        
        User_Action = bpy.context.scene.lt_actions
        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")

        if User_Action["LT_Type"] == 'FULL':

            BodyShop(PreSet=User_Action.name, from_Arm=User_Action['LT_From_Body'], to_Arm=User_Action['LT_To_Body']).BodySwap()

        if  User_Action["LT_Type"] == 'ADDITIVE':
            
            BodyShop(PreSet=User_Action.name).ApplyPreSet(Is_Addative=True)

        return {"FINISHED"}
     
#TODO: could probabbly merge these two into one operator but its fine for now
class LT_OT_load_user_presets(bpy.types.Operator):
    
    bl_idname = "lt.load_user_presets"
    bl_label = "load user presets"
    bl_description = "Loads all actions from the Blend file defined in the addon preferences."

    def execute(self, context):
        user_lib_path = bpy.context.preferences.addons[__package__].preferences.user_lib_path
        if user_lib_path != 'set me!':
            try:
                with bpy.data.libraries.load(bpy.context.preferences.addons[__package__].preferences.user_lib_path) as (data_from, data_to):
                    data_to.actions = data_from.actions

            except KeyError:
                
                Error_Popup(
                    pop_title="Error: Unable to load pre-sets",
                    error_reason="No valid data found in the provided filepath.",
                    suggestion="Either the path is invalid, or there are no actions inside the Blend file."
                    )
        else:
            Error_Popup(
                pop_title="Error: File Path not set",
                error_reason="The user has not entered a filepath in the addon's preferences.",
                suggestion="The user should go do that."
                )
        
        return {"FINISHED"}
    

class LT_OT_save_user_presets(bpy.types.Operator):
    
    bl_idname = "lt.save_user_preset"
    bl_label = "Save User Pre-Sets"
    bl_description = "Saves all Actions created by the user to the Blend file defined in the addon preferences'"

    
    def execute(self, context):
        
        user_lib_path = bpy.context.preferences.addons[__package__].preferences.user_lib_path
        
        if user_lib_path != 'set me!':
            data_blocks = set(action for action in bpy.data.actions if not action.name.startswith("LT_"))
            bpy.data.libraries.write(user_lib_path, data_blocks, fake_user=True)
        
        else:
            Error_Popup(
                pop_title="Error: File Path not set",
                error_reason="The user has not entered a filepath in the addon's preferences.",
                suggestion="The user should go do that."
                )
        
        return {"FINISHED"}



class LT_MT_about_preset_menu(bpy.types.Menu):
    
    bl_idname = "LT_MT_about_preset_menu"
    bl_label = "About Pre-Set"

    dating_easter_egg = (
            
        "Long walks on the beach",
        "The smell of burnt toast",
        "The thrill of the kill",
        "Taylor Swift",
        "The colour purple",
        "Licking lamp posts in winter",
        "Being toxic on reddit",
        "Sending Volno $5",
        "Going on advantures",
        "Knitting",
        "Pirating Adobe products",
        "You",
        "Being in the cuck vent"
        )
            

    def get_short_name(self, propname):
        #this is awful

        return (bpy.context.scene.lt_actions[propname].replace('LT_','')).replace('_BASE','')
    

        
    def draw(self, context):
        import random
        egg_check = random.randint(1, 20)

        dating_easter_egg = (
            
            "Long walks on the beach",
            "The smell of burnt toast",
            "The thrill of the kill",
            "Taylor Swift",
            "The colour purple",
            "Licking lamp posts in winter",
            "Being toxic on reddit",
            "Sending Volno $5",
            "Going on advantures",
            "Knitting",
            "Pirating Adobe products",
            "You",
            "Being in the cuck vent"
        )
        
        lt_actions = bpy.context.scene.lt_actions
        lt_type = lt_actions['LT_Type']
        layout = self.layout

        layout.label(text="Name: " + lt_actions.name)
        layout.label(text="Type: " + lt_type)
        if lt_type == "FULL":
            layout.label(text="Converts From: " + self.get_short_name('LT_From_Body'))
            layout.label(text="Converts To: " + self.get_short_name('LT_To_Body'))
        layout.label(text="Creator: " + lt_actions['LT_Creator'])
        if egg_check == 20:
            layout.label(text="Likes: " + dating_easter_egg[random.randint(0, 12)])

