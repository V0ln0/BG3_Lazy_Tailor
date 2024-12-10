# this is for swapping around what body we're fitting too
# collections_all does not exist in prior to 4.1, will need to make a patch for earlior verions


import bpy

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

    # def BodySwap(self, NeedsSwap=True, KeepPose=False, NeedsRest=False):

    def BodySwap(self):
   
        bpy.data.objects[self.Base].data = bpy.data.armatures[self.BodyArm]
        bpy.ops.pose.user_transforms_clear(only_selected=False)
        self.Childof_Validator()
        bpy.data.objects[self.Mannequin].pose.apply_pose_from_action(bpy.data.actions[self.PreSet])

        


class LT_OT_swap_body_type(bpy.types.Operator):

    bl_idname = "lt.swap_body_type"
    bl_label = "Swap Body Type"
    bl_description = "Swaps the Body Type That You Are Fitting too"

    def execute(self, context):
        
        lt_props = bpy.context.scene.lt_props
        bpy.ops.object.mode_set(mode="POSE")
        bpy.context.view_layer.objects.active = bpy.data.objects[lt_props.mannequin_form]

        # Uses the string props from LazyTalior_Prop.py as an input 
        # probbably a dumb idea to call it "SewingPattern" but I couldn't think of a better name for it
        SewingPattern = LT_BodyShop(lt_props.mannequin_base, lt_props.mannequin_form, lt_props.body_type, lt_props.body_preset)
        SewingPattern.BodySwap()
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





