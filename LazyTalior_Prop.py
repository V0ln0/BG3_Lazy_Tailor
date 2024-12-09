import bpy

class LT_Props(bpy.types.PropertyGroup):

    bc_from: bpy.props.StringProperty(name='bc_from', default='LT_HUM_M') #defualt is HUM_M_BASE
    bc_to: bpy.props.StringProperty(name='bc_to', default='NOT_SET') #defualt is GTY_M_BASE
    InitBool: bpy.props.BoolProperty(name='InitBool', default=False)



# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout
# https://blender.stackexchange.com/questions/160883/contextually-grey-out-panel-element-in-python-2-8