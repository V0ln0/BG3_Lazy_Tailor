import bpy

class LT_PropsGroup(bpy.types.PropertyGroup):

    M_Target_A: bpy.props.StringProperty(name= 'M_Target_A', default='shits working') #LT_Mannequin
    M_Target_B: bpy.props.StringProperty() #LT_Mannequin_Base
    InitBool: bpy.props.BoolProperty(name='InitBool', default=False)



# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout