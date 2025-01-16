#stuff thats needed in multiple places

import bpy


# checks for a collection, if it exists it returns the collection name. 
# if it dosen't exist, it creates a new collection with the desried name and returns the new collection
def LT_ensure_collection(Cname) -> bpy.types.Collection:

    scene = bpy.context.scene

    try:
        link_to = scene.collection.children[Cname]
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]
    except KeyError:
        link_to = bpy.data.collections.new(Cname)
        scene.collection.children.link(link_to)
        bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[link_to.name]

    return link_to


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
    bl_description = "Sets the Export order of mesh objects alphabetically"

    selected: bpy.props.BoolProperty(
        name="For Selected",
        default=False,
        description="If True, sets the export order of selected mesh objects rather than the children of Local_Mannequin."
    ) 
 
    def execute(self, context):
        
        if self.selected == False:
            con = bpy.data.objects["Local_Mannequin"].children
        else:
            con = context.selected_objects
        
        NameList = []

        for n in con:
            if n.type == "MESH":
                NameList.append(n.data.name)
                
        for index, obj in enumerate(NameList, start=1):

            bpy.data.meshes[obj].ls_properties.export_order = index
            print(bpy.data.meshes[obj].ls_properties.export_order)
        
        return {"FINISHED"}

class LT_OT_apply_refit(bpy.types.Operator):
    
    bl_idname = "lt.apply_refit"
    bl_label = "Apply Refit"
    bl_description = "Applies the Armature modifer on all children of Local_Mannequin"


    def execute(self, context):
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass        

        for C in bpy.data.objects["Local_Mannequin"].children:
            if C.type == "MESH":
                for M in C.modifiers:
                    if M.type == "ARMATURE":
                        bpy.ops.object.modifier_apply(modifier=M.name)

        return {"FINISHED"}                    

class LT_MT_export_order(bpy.types.Menu):
    
    bl_idname = "LT_MT_export_order"
    bl_label = "Set Export Order"

    def draw(self, context):
        layout = self.layout

        layout.operator("lt.export_order_setter", text="Of Children").selected = False
        layout.operator("lt.export_order_setter", text="Of Selected").selected = True
        # layout.operator("lt.export_order_setter", text="Of Children", description="Sets the export order of Local_Mannequin's children.").selected = False
        # layout.operator("lt.export_order_setter", text="Of Selected", description="Sets the export order of all selected mesh objects").selected = True


# class LT_OT_create_LOD(bpy.types.Operator):
    
#     bl_idname = "lt.create_LOD"
#     bl_label = "create LOD"
#     bl_description = "Creates an LOD of the selected mesh"

#     def execute(self, context):
#         newLOD = bpy.ops.object.duplicate
        
#         return {"FINISHED"}

#to do: opperator for corrective smooth



#print(dir(bpy.data.objects["Local_Mannequin"]))

#print(getattr(bpy.data.objects["Local_Mannequin"], 'children'))