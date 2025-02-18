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


    #NOTE pretty sure I can just get rid of this and replace it with a "set_base"
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
        default=(1)
    )

    def execute(self, context):

        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = BodyShop(
            from_Arm=self.from_bones,
            )

        SewingPattern.set_base()
        # SewingPattern.change_base()
  
        return {"FINISHED"}
    
class LT_OT_set_to_tailor(bpy.types.Operator):

    bl_idname = "lt.set_to_tailor"
    bl_label = "Set To Body"
    bl_description = "Sets the body you are converting TO."
    
    to_bones: bpy.props.EnumProperty(
        name="Set To Body",
        items=base_bones,
        default=(1)
    )

    def execute(self, context):

        active_check.force_active()
        bpy.ops.object.mode_set(mode="POSE")
        
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = BodyShop(
            to_Arm=self.to_bones,
            )

        # SewingPattern.set_base()
        SewingPattern.change_base()
  
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


#TODO: this has not been tested fully
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
        active = bpy.context.scene.lt_actions
        user_props = bpy.context.scene.lt_user_props
        active_type = bpy.context.scene.lt_user_props.type_action
        
        active['LT_Type'] = active_type
        if active_type == "ADDATIVE":
            active['LT_From_Body'] = "N/A"
            active['LT_To_Body'] = "N/A"
        else:
            active['LT_From_Body'] = user_props.from_body_action
            active['LT_To_Body'] = user_props.to_body_action
            
        active['LT_Creator'] = user_props.creator
        active['LT_Description'] = user_props.desc

        return {"FINISHED"}



#this is hacky as fuck but I just don't care anymore
#this entire class is for appeasing the ui spirits
class preset_info:
    #fucking bpy.context restricted accsess ass
    @classmethod
    def is_lt_action(self):

        return bool(bpy.context.scene.lt_actions is not None)
    
    @classmethod
    def read_prop(self, propname: str, lt_action):
        #check if the prop exists and retruns a placehodler if it dosen't 
        if lt_action[propname] is not None:
            return lt_action[propname]
        else:
            return "N/A"
   
    @classmethod    
    def get_short_name(self, name:str):
        
        return (name.replace('LT_','')).replace('_BASE','')
    
    @classmethod 
    def is_not_defualt(self, lt_action):
        #check to stop people messing with the defualt presets
        return bool(lt_action.get('LT_Default') is None)
    
class preset_info_ui(preset_info):
    
    @classmethod
    def draw_preset_info(cls, self, context, layout, UI_action):
       
        lt_type = self.read_prop(propname='LT_Type', lt_action=UI_action)

        layout.label(text="Name: " + UI_action.name)
        layout.label(text="Type: " + lt_type)
        if lt_type == "FULL":
            layout.label(text="Converts From: " + self.get_short_name(self.read_prop(propname='LT_From_Body', lt_action=UI_action)))
            layout.label(text="Converts To: " + self.get_short_name(self.read_prop(propname='LT_To_Body', lt_action=UI_action)))
        layout.label(text="Creator: " + self.read_prop(propname='LT_Creator', lt_action=UI_action))
        layout.label(text="Description: " + self.read_prop(propname='LT_Description', lt_action=UI_action))


class LT_MT_about_preset_scene_menu(preset_info_ui, bpy.types.Menu):
    
    bl_idname = "LT_MT_about_preset_scene_menu"
    bl_label = "About Pre-Set"
    
    def draw(self, context):
        self.draw_preset_info(self, context, self.layout, bpy.context.scene.lt_actions)
        
# class LT_MT_about_preset_dropsheet_menu(preset_info_ui, bpy.types.Menu):
    
#     bl_idname = "LT_MT_about_preset_dropsheet_menu"
#     bl_label = "About Pre-Set"
    
#     def draw(self, context):
#         self.draw_preset_info(self, context, self.layout, bpy.context.scene.lt_actions)
        
