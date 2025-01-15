#stuff thats needed in multiple places

import bpy

class LT_active_check:

    def force_active(ObjName): # norb's hell
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        except RuntimeError:
            bpy.context.view_layer.objects.active = bpy.data.objects[ObjName]
        
        bpy.ops.object.select_pattern(pattern=ObjName, extend=False)

class LT_OT_export_order_setter(bpy.types.Operator):
    
    bl_idname = "lt.export_order_setter"
    bl_label = "Set Export Order"
    bl_description = "Sets the Export order of selected objects alphabeticaly"

    def execute(self, context):
        
        selected = context.selected_objects
        NameList = []

        for n in selected:
            if n.type == "MESH":
                NameList.append(n.data.name)
                
        for index, obj in enumerate(NameList, start=1):
            
            bpy.data.meshes[obj].ls_properties.export_order = index
            print(bpy.data.meshes[obj].ls_properties.export_order)
        
        
    
class LT_OT_apply_refit(bpy.types.Operator):
    
    bl_idname = "lt.apply_refit"
    bl_label = "Apply Refit"
    bl_description = "Applies the Armature modifer on all children of Local_Mannequin"

    as_shapekey: bpy.props.BoolProperty(
        name="as_shape key",
        default=False,
        description="When true, saves the refit as a shapekey rather than applying it. Used for when you are not ready to commit to the final shape"
        ) 

    def execute(self, context):
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass        
        # todo: add checker for when there are no children

        for C in bpy.data.objects["Local_Mannequin"].children:
            if C.type == "MESH":
                for M in C.modifiers:
                    if M.type == "ARMATURE":
                        if self.as_shapekey == True:
                            bpy.ops.object.modifier_apply_as_shapekey(keep_modifier=False, modifier=M.name)
                        else:
                            bpy.ops.object.modifier_apply(modifier=M.name)

        return {"FINISHED"}                    


#to do: opperator for corrective smooth



#print(dir(bpy.data.objects["Local_Mannequin"]))

#print(getattr(bpy.data.objects["Local_Mannequin"], 'children'))