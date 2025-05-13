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

    def __init__(self, from_Arm='LT_Mannequin_Base', to_Arm='LT_Mannequin_Base', LMB='Local_Mannequin_Base', LM='Local_Mannequin'):

        self.from_Arm = bpy.data.armatures[from_Arm] #name(string) of the body armature that we're changing from, not always needed 
        self.to_Arm = bpy.data.armatures[to_Arm] # name(string) of the body armature that we're changing too, not always needed 
        self.LMB = bpy.data.objects[LMB]
        self.LMB_A = bpy.data.armatures[LMB]
        self.LM = bpy.data.objects[LM]
        self.LM_A = bpy.data.armatures[LM]
    
    # upon swapping armature data, the 'childof' constraints need to have their inverse set again, lest you wish to see some sort of demonic gibon
    def child_of_mass_invert(self):

        for b in self.LM.pose.bones:
            for c in b.constraints:
                if c.type == "CHILD_OF":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    self.LM.data.bones.active = b.bone                               
                    bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner="BONE")
    
    def stretch_to_mass_set(self): #NOTE: 99% sure that this is not actualy needed, but I'm keeping it as it was usefull as a debugging tool.

        for b in self.LM.pose.bones:
            for c in b.constraints:
                if c.type == "STRETCH_TO":
                    context_py = bpy.context.copy()
                    context_py["constraint"] = c
                    self.LM.data.bones.active = b.bone                               
                    bpy.ops.constraint.stretchto_reset(constraint="Stretch To", owner='BONE')

    # can't effect constraints on bones that are not visable in the viewport
    def BoneVis_Validator(self, stretch_To=False):
        
        CB = self.LM_A.collections["Deform_Bones"]
        if CB.is_visible == False:
            CB.is_visible = True
        
        self.child_of_mass_invert()
        
        if stretch_To == True: 
            self.stretch_to_mass_set() 
        
        CB.is_visible = False

    def ApplyPreSet(self, PreSet:str, Is_Addative=False): #"Is_Addative" for when applying a preset on top of existing deformations without clearing them
        
        bpy.ops.pose.select_all(action='SELECT')
        if Is_Addative == False:
            bpy.ops.pose.user_transforms_clear(only_selected=False)
        self.LM.pose.apply_pose_from_action(PreSet)


    def set_base(self, full_reset=False):
        
        base = self.from_Arm
        if full_reset == True: #used to completely reset the LMB back to its defualt
            base = self.LMB_A 
        
        bpy.ops.pose.user_transforms_clear(only_selected=False)
        self.LMB.data = base
        self.BoneVis_Validator()
        bpy.ops.pose.armature_apply(selected=False)
        #sets new rest pose, was originaly optional as its not always nessiscary but its better to just do it everytime than constantly check

    def change_base(self):

        bpy.ops.pose.user_transforms_clear(only_selected=False)
        self.LMB.data = self.to_Arm
        #LM then needs to be corrected
        self.BoneVis_Validator()


    # functions sperated out like this so that we are able to call on indvidual parts
    def BodySwap(self, PreSet): 
        
        self.set_base()                           
        self.change_base()
        bpy.ops.pose.select_all(action='SELECT')
        self.LM.pose.apply_pose_from_action(PreSet)


# norb's hell.
# tldr: many of blender's functions/operators are context dependent on what the selected and/or active object is and what mode it is in
# is great for the end user in the ui, but a nightmare coding wise

class active_check: 

    def force_active(ObjName='Local_Mannequin'): 
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        except RuntimeError:
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        
        bpy.ops.object.select_pattern(pattern=ObjName, extend=False)


# TODO: work out how to use blender's built in error messages for operators
def Error_Popup(pop_title: str, error_reason: str, suggestion: str):

    def draw(self, context):
       
        self.layout.label(text=error_reason)
        self.layout.label(text=suggestion)
        
    bpy.context.window_manager.popup_menu(draw, title = pop_title, icon = 'ERROR')

def check_linked(is_warning:bool):
    is_action = bool(bpy.data.objects["Local_Mannequin"].animation_data.action)
    is_valid = True
    if is_action == True:
        #blender gets pissy when trying to unlink an action from the scene menu.
        #TODO: try to find a less scuffed way of unlinking actions from the scene menu that dosen't involve telling the user to do it
        if is_warning == True: 
            Error_Popup(
                pop_title="Action Data Detected!",
                error_reason="An action data block has been found on Local_Mannequin, unable to apply pre-set.",
                suggestion="Please unlink the action and try again."
                )
            is_valid = False
        else:
            bpy.ops.action.unlink()
    return is_valid

class LT_OT_mannequin_reset(bpy.types.Operator):

    bl_idname = "lt.mannequin_reset"
    bl_label = "Mannequin Reset"
    bl_description = "Sets the Mannequin back to its defualt state"


    def execute(self, context):
        is_valid = check_linked(is_warning=True)
        if is_valid == True:
            active_check.force_active()
            bpy.ops.object.mode_set(mode="POSE")
            BodyShop().set_base(full_reset=True)
            bpy.context.scene.lt_user_props.to_body_action = 'LT_HUM_F_BASE'
            bpy.context.scene.lt_user_props.from_body_action = 'LT_HUM_F_BASE'
        return {"FINISHED"}

class LT_OT_constraints(bpy.types.Operator):

    bl_idname = "lt.constraints"
    bl_label = "BONE ZONE"
    bl_description = "Manual fix for stretch_to and child_of or stretch_to constaints when swaping armatures"
    
    stretch_to_bool: bpy.props.BoolProperty(
        name="stretch_to_bool",
        default=False
        )
    
    is_debug: bpy.props.BoolProperty(
    default=False
    )

    def execute(self, context):
        if self.is_debug == False:
            BodyShop().BoneVis_Validator(stretch_To=self.stretch_to_bool)
        else:
            BodyShop(LMB='LT_Mannequin_Base', LM='LT_Mannequin').BoneVis_Validator(stretch_To=self.stretch_to_bool)
        return {"FINISHED"}


base_bones= (
    
    ("LT_HUM_F_BASE", "HUM_F", "Fits body type 1(BT1) races & fem Githyanki.", 1),
    ("LT_HUM_M_BASE", "HUM_M", "Fits body type 2(BT2) races & masc Githyanki.", 2),
    ("LT_HUM_FS_BASE", "HUM_FS", "Fits body type 3(BT3) races + fem Dragonborn & Half-Orcs", 3),
    ("LT_HUM_MS_BASE", "HUM_MS", "Fits body type 4(BT4) races + masc Dragonborn & Half-Orcs", 4),
    ("LT_SHORT_F_BASE", "SHORT_F", "Fits fem Gnomes and Halflings", 5),
    ("LT_SHORT_M_BASE", "SHORT_M", "Fits masc Gnomes and Halflings", 6),
    ("LT_DWR_F_BASE", "DWR_F", "Fits fem Dwarves", 7),
    ("LT_DWR_M_BASE", "DWR_M", "Fits masc Dwarves", 8),
)    


class LT_OT_set_from_tailor(bpy.types.Operator):

    bl_idname = "lt.set_from_tailor"
    bl_label = "Set From Body"
    bl_description = "Sets the body you are converting FROM."
    
    from_bones: bpy.props.EnumProperty(
        name="Set From Body",
        items=base_bones,
        default=(1),
        description="Sets the 'From Body' of Local_Mannequin"
    )

    def execute(self, context):
        check_linked(is_warning=False)
        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        BodyShop(from_Arm=self.from_bones).set_base()
        bpy.context.scene.lt_user_props.from_body_action = self.from_bones
        return {"FINISHED"}
    
class LT_OT_set_to_tailor(bpy.types.Operator):

    bl_idname = "lt.set_to_tailor"
    bl_label = "Set To Body"
    bl_description = "Sets the body you are converting TO."
    
    to_bones: bpy.props.EnumProperty(
        name="Set To Body",
        items=base_bones,
        default=(1),
        description="Sets the 'To Body' of Local_Mannequin"
    )

    def execute(self, context):
        
        check_linked(is_warning=False)
        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        BodyShop(to_Arm=self.to_bones).change_base()
        bpy.context.scene.lt_user_props.to_body_action = self.to_bones
        return {"FINISHED"}


class LT_OT_defualt_preset_tailor(bpy.types.Operator):

    bl_idname = "lt.defualt_preset_tailor"
    bl_label = "Apply Pre-Set"
    bl_description = "Applies the pre-set selected in 'To:' to the Mannequin. WARNING: will clear all user transforms"

    #NOTE: this is dumb but I want the defualt presets to be as easy to use as possible for the enduser 
    #that means putting the training wheels on

    def execute(self, context):

        lt_util_props = context.scene.lt_util_props
        
        #god damn blender restricting bpy.data
        F_PreSets = Enum('F_PreSets', [
            ('GTY', bpy.data.actions['LT_GTY_F_BDY']),
            ('HUM_S', bpy.data.actions['LT_HUM_FS_BDY']),
            ('DGB', bpy.data.actions['LT_DGB_F_BDY']),
            ('GNO', bpy.data.actions['LT_GNO_F_BDY']),
            ('HFL', bpy.data.actions['LT_HFL_F_BDY']),
            ('DWR', bpy.data.actions['LT_DWR_F_BDY']), 
            ('HRT', bpy.data.actions['LT_HUM_F_FTM']), 
            ])
                
        M_PreSets = Enum('M_PreSets', [
            ('GTY', bpy.data.actions['LT_GTY_M_BDY']),
            ('HUM_S', bpy.data.actions['LT_HUM_MS_BDY']),
            ('DGB', bpy.data.actions['LT_DGB_M_BDY']),
            ('GNO', bpy.data.actions['LT_GNO_M_BDY']),
            ('HFL', bpy.data.actions['LT_HFL_M_BDY']),
            ('DWR', bpy.data.actions['LT_DWR_M_BDY']), 
            ('HRT', bpy.data.actions['LT_HUM_M_MTF']), 
            ])
        
        is_valid = check_linked(is_warning=True)
        if is_valid == True:
            
            active_check.force_active()
            bpy.ops.object.mode_set(mode="POSE")
            if lt_util_props.from_body == "HUM_F":
                action = F_PreSets[lt_util_props.to_body].value
            else:
                action = M_PreSets[lt_util_props.to_body].value
            
            SewingPattern = BodyShop(
                from_Arm=action['LT_From_Body'], 
                to_Arm=action['LT_To_Body']
                )
            
            SewingPattern.BodySwap(PreSet=action)
            bpy.context.scene.lt_user_props.to_body_action = action['LT_To_Body']
            bpy.context.scene.lt_user_props.from_body_action = action['LT_From_Body']        
            
        return {"FINISHED"}




#TODO: this has not been tested fully
class LT_OT_apply_user_preset(bpy.types.Operator):

    bl_idname = "lt.apply_user_preset"
    bl_label = "User Preset"
    bl_description = "Applies a user defined preset to Local_Mannequin"


    def execute(self, context):
        
        is_valid = check_linked(is_warning=True)
        if is_valid == True:        
            
            User_Action = bpy.context.scene.lt_actions
            active_check.force_active()
            bpy.ops.object.mode_set(mode="POSE")
            if User_Action["LT_Type"] == 'FULL':

                BodyShop(from_Arm=User_Action['LT_From_Body'], to_Arm=User_Action['LT_To_Body']).BodySwap(PreSet=User_Action)

            if  User_Action["LT_Type"] == 'ADDITIVE':
                
                BodyShop().ApplyPreSet(PreSet=User_Action, Is_Addative=True)

        return {"FINISHED"}
     

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
    bl_description = "Saves all Actions created by the user to the Blend file defined in the addon preferences."

    
    def execute(self, context):
        
        user_lib_path = bpy.context.preferences.addons[__package__].preferences.user_lib_path
       
        if user_lib_path != 'set me!':
            data_blocks = set(action for action in bpy.data.actions if action.get('LT_Default') is None)
            bpy.data.libraries.write(user_lib_path, data_blocks, fake_user=True)
        
        else:
            Error_Popup(
                pop_title="Error: File Path not set",
                error_reason="The user has not entered a filepath in the addon's preferences.",
                suggestion="The user should go do that."
                )
        
        return {"FINISHED"}


       
class LT_OT_set_preset_info(bpy.types.Operator):
    
    bl_idname = "lt.set_preset_info"
    bl_label = "Set Info"
    bl_description = "Sets custom porperties on the active action so that Lazy Tailor knows how to apply your Pre-Set."

    def execute(self, context):
        active = bpy.data.objects["Local_Mannequin"].animation_data.action
        user_props = bpy.context.scene.lt_user_props
        active_type = bpy.context.scene.lt_user_props.type_action
        
        
        if active_type == "ADDATIVE":
            active['LT_Type'] = active_type
            active['LT_From_Body'] = "N/A"
            active['LT_To_Body'] = "N/A"
        else:
            active['LT_Type'] = active_type
            active['LT_From_Body'] = user_props.from_body_action
            active['LT_To_Body'] = user_props.to_body_action
            
        active['LT_Creator'] = user_props.creator
        active['LT_Description'] = user_props.desc

        return {"FINISHED"}



