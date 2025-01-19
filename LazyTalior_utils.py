#stuff thats needed in multiple places

import bpy
import enum
from enum import Enum

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


class LT_MT_export_order_menu(bpy.types.Menu):
    
    bl_idname = "LT_MT_export_order_menu"
    bl_label = "Set Export Order For..."

    def draw(self, context):
        layout = self.layout

        layout.operator("lt.export_order_setter", text="Mannequin Children").selected = False
        layout.operator("lt.export_order_setter", text="Selected Objects").selected = True
        # layout.operator("lt.export_order_setter", text="Of Children", description="Sets the export order of Local_Mannequin's children.").selected = False
        # layout.operator("lt.export_order_setter", text="Of Selected", description="Sets the export order of all selected mesh objects").selected = True

def LT_select_children(Parent):

    bpy.ops.object.select_all(action='DESELECT')
    offspring = Parent.children
    for O in offspring:
        O.select_set(True)
    bpy.context.view_layer.objects.active = offspring[0]
    return offspring


class LT_OT_mass_apply_modifier(bpy.types.Operator):
    
    bl_idname = "lt.mass_apply_modifier"
    bl_label = "Apply Modifier"
    bl_description = "Applies all modifiers of a specified type on all children of Local_Mannequin or all selected objects"


    modifier_type: bpy.props.StringProperty(
        name="modifier type",
        default="ARMATURE",
        )

    for_selected: bpy.props.BoolProperty(
        name="for selected only",
        default=False
    ) 
    
    def execute(self, context):
        
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass        
        
        tailor_props = context.scene.tailor_props
        meshes = bpy.context.selected_objects
        
        if self.for_selected == False:
           meshes = LT_select_children(bpy.data.objects[tailor_props.mannequin_form])

        for C in meshes:
            if C.type == "MESH":
                for M in C.modifiers:
                    if M.type == self.modifier_type:
                        context_py = bpy.context.copy()
                        context_py["modifier"] = M
                        bpy.context.view_layer.objects.active = C  
                        bpy.ops.object.modifier_apply(modifier=M.name)

        return {"FINISHED"}   

class LT_MT_mass_apply_menu(bpy.types.Menu):
    
    bl_idname = "LT_MT_mass_apply_menu"
    bl_label = "Appy Changes On..."

    def draw(self, context):
        layout = self.layout

        layout.operator("lt.mass_apply_modifier", text="Mannequin Children")
        layout.operator("lt.mass_apply_modifier", text="Selected Objects").for_selected = True

class lod_codebook():
    
    LOD_def = Enum('LOD_def', [('LOD0', 0), ('LOD1', 1), ('LOD2', 2), ('LOD3', 3), ('LOD4', 4)])

    LOD_dict = {
        #values taken of GTY_M_NKD_Body, hope they're universal lol
        #pattern for tuple (LOD Level, LOD Distance, Decimate ratio)
        "LOD0": (0, 6, 1.0),
        "LOD1": (1, 13, 0.75),
        "LOD2": (2, 23, 0.25),
        "LOD3": (3, 30, 0.1),
        "LOD4": (4, 0, 0.03),

    }

    def get_LOD(self, LOD_value):
       
       return self.LOD_dict[self.LOD_def(LOD_value).name]


class LT_OT_create_lod(bpy.types.Operator):
    # "Let's go. In and out. 20 minute operator" this was h e l l
    bl_idname = "lt.create_lod"
    bl_label = "create LOD"
    bl_description = "Creates a LOD of the selected mesh"

    level_int: bpy.props.IntProperty(
        name="level_int",
        default=0,
        min=0,
        max=4,
    )

    no_LOD: bpy.props.BoolProperty(
        name="no_LOD",
        default=False
    ) #sets the LOD level and distance without creating a new mesh 
    #TODO:  not working :<
    

    reset_LOD: bpy.props.BoolProperty(
        name="reset_LOD",
        default=False
    ) #just resets both the level and the distance to 0


    def set_LOD(self, obj, level, distance):
        
        obj.data.ls_properties.lod = level
        obj.data.ls_properties.lod_distance = distance

    def create_LOD(self, obj):
        
        LOD_name = lod_codebook.LOD_def(self.level_int).name
        
        newLODname = obj.name + "_" + LOD_name
        newLODdata = obj.data.copy()
        newLOD = bpy.data.objects.new(newLODname, newLODdata)
        newLOD.data.name = newLODname

        if obj.parent:
            newLOD.parent = obj.parent
            obj.parent.users_collection[0].objects.link(newLOD)
        else:
            bpy.context.scene.collection.objects.link(newLOD)
        
        bpy.context.view_layer.objects.active = newLOD
        
        return newLOD

    
    
    def execute(self, context):
        
        active_obj = bpy.context.view_layer.objects.active
        
        if active_obj.type == 'MESH':
            if self.reset_LOD == True: 
                self.set_LOD(active_obj, 0, 0)
            else:
                LOD = lod_codebook().get_LOD(LOD_value=self.level_int)
                
                if self.level_int == 0:
                    
                    self.set_LOD(active_obj, LOD[0], LOD[1])
                
                else:
                    
                    if self.no_LOD == True:
                        self.set_LOD(active_obj, LOD[0], LOD[1])
                        bpy.ops.object.modifier_add(type='DECIMATE')
                        active_obj.modifiers["Decimate"].ratio = LOD[2]
                    
                    else:
                        created_LOD = self.create_LOD(active_obj)
                        self.set_LOD(created_LOD, LOD[0], LOD[1])
                        bpy.ops.object.modifier_add(type='DECIMATE')
                        created_LOD.modifiers["Decimate"].ratio = LOD[2]
                        bpy.context.view_layer.objects.active = active_obj

        return {"FINISHED"}

# to do: opperator for corrective smooth



#print(dir(bpy.data.objects["Local_Mannequin"]))

#print(getattr(bpy.data.objects["Local_Mannequin"], 'children'))