#misc stuff to do with meshes

import bpy
import enum
from enum import Enum




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
            con = bpy.data.objects['Local_Mannequin'].children
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
        
        meshes = bpy.context.selected_objects
        if self.for_selected == False:
           meshes = LT_select_children(bpy.data.objects['Local_Mannequin'])

        for C in meshes:
            if C.type == "MESH":
                for M in C.modifiers:
                    if M.show_viewport == True and M.type == self.modifier_type:
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
    
    LOD_def = Enum('LOD_def', [('LOD0', 0), ('LOD1', 1), ('LOD2', 2), ('LOD3', 3), ('LOD4', 4), ('CLEAR', 5)])

    LOD_dict = {
        #values taken of GTY_M_NKD_Body, hope they're universal lol
        #pattern for tuple (LOD Level, LOD Distance, Decimate ratio)
        "LOD0": (0, 6, 1.0),
        "LOD1": (1, 13, 0.75),
        "LOD2": (2, 23, 0.25),
        "LOD3": (3, 30, 0.1),
        "LOD4": (4, 0, 0.03),
        "CLEAR": (0, 0, 0),
    }

    def get_LOD(self, LOD_value):
       
       return self.LOD_dict[self.LOD_def(LOD_value).name]


class LT_OT_create_lod(bpy.types.Operator):
    # "Let's go. In and out. 20 minute operator" this was h e l l
    bl_idname = "lt.create_lod"
    bl_label = "create LOD"
    bl_description = "Creates or sets the LOD of a selected mesh"

    level_int: bpy.props.IntProperty(
        name="level_int",
        default=0,
        min=0,
        max=5,
    )
    new_mesh: bpy.props.BoolProperty(
        name="new_mesh",
        default=True
    ) #sets the LOD level and distance without creating a new mesh 


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
            LOD = lod_codebook().get_LOD(LOD_value=self.level_int)
            
            if self.level_int in tuple((0, 5)):
                self.set_LOD(active_obj, LOD[0], LOD[1])
                #LOD0 never needs to create a new mesh, be decimated, or renamed. The same is true for clearing the LOD values
            else:               
                if self.new_mesh == False:
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

class LT_MT_create_lod_menu(bpy.types.Menu):
        
    bl_idname = "LT_MT_create_lod_menu"
    bl_label = "Create LOD..."
    
    def draw(self, context):
        
        layout = self.layout
        layout.operator('lt.create_lod', text="LOD1").level_int = 1
        layout.operator('lt.create_lod', text="LOD2").level_int = 2
        layout.operator('lt.create_lod', text="LOD3").level_int = 3
        layout.operator('lt.create_lod', text="LOD4").level_int = 4

class LT_MT_set_lod_menu(bpy.types.Menu):
        
    bl_idname = "LT_MT_set_lod_menu"
    bl_label = "Set LOD..."
    
    def draw(self, context):
        
        layout = self.layout

        layout.operator('lt.create_lod', text="LOD0").level_int = 0
        
        props = layout.operator('lt.create_lod', text="LOD1")
        props.level_int = 1
        props.new_mesh = False

        props = layout.operator('lt.create_lod', text="LOD2")
        props.level_int = 2
        props.new_mesh = False
        
        props = layout.operator('lt.create_lod', text="LOD3")
        props.level_int = 3
        props.new_mesh = False

        props = layout.operator('lt.create_lod', text="LOD4")
        props.level_int = 4
        props.new_mesh = False
        
        layout.operator('lt.create_lod', text="Reset LOD").level_int = 5

#this might be come redundent later
class LT_OT_so_no_head(bpy.types.Operator):
    
    bl_idname = "lt.so_no_head"
    bl_label = "create Head_M"
    bl_description = "Creates the 'Head_M' vertex group on the active object and sets it's weight to 1.0"


    def so_head(self):
        try:
            Head_M = bpy.context.active_object.vertex_groups["Head_M"]
            return Head_M
        except KeyError:
            Head_M = bpy.context.active_object.vertex_groups.new(name='Head_M')
            return Head_M

    def execute(self, context):

        if bpy.context.active_object.type == 'MESH':
            Head_M = self.so_head()
            Verts = [i.index for i in bpy.context.active_object.data.vertices]
            Head_M.add(Verts, 1.0, 'ADD')
        else:
            pass
        
        return {"FINISHED"}
    

class LT_OT_xflip_mesh(bpy.types.Operator):
    
    #this whole thing is nasty but "if it looks stupid but works, it ain't stupid"
    bl_idname = "lt.xflip_mesh"
    bl_label = "X Flip Mesh"
    bl_description = "Mirrors the active mesh on its X axis."


    def execute(self, context):

        #make sure it's all halal before we start
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except RuntimeError:
            pass
        
        obj = bpy.context.view_layer.objects.active
        
        if obj.type == 'MESH':
            bpy.ops.object.select_pattern(pattern=obj.name, extend=False)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            bpy.ops.transform.resize(value=(-1.0, 1.0, 1.0))
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            #"just flip 'em"
            for group in obj.vertex_groups:
                if group.name != "Dummy_Root":
                    print(group.name)
                    group.name = group.name.replace('_L','_X0')
                    group.name = group.name.replace('_R','_Y0')

            for group in obj.vertex_groups:
                group.name = group.name.replace('_X0','_R')
                group.name = group.name.replace('_Y0','_L')

            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.editmode_toggle()

        return {"FINISHED"}
