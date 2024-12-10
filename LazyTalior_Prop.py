import bpy

class LT_Props(bpy.types.PropertyGroup):
    mannequin_base: bpy.props.StringProperty(name="bc_from", default="LT_Mannequin_Base")
    mannequin_form: bpy.props.StringProperty(name="bc_from", default="LT_Mannequin")
    body_type: bpy.props.StringProperty(name="bc_from", default="LT_HUM_M") 
    body_preset: bpy.props.StringProperty(name="bc_to", default="LT_HUM_MS_BDY") 
    InitBool: bpy.props.BoolProperty(name="InitBool", default=False)



# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout
# https://blender.stackexchange.com/questions/160883/contextually-grey-out-panel-element-in-python-2-8