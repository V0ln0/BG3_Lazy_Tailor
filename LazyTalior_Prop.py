import bpy
import os
from os import path

# TODO: read up bitch https://blender.stackexchange.com/questions/280695/bpy-layout-difference-between-various-enum-methods

#BEHOLD... my enums
base_body = (
    
    ("HUM_F", "Human(Fem)", "Body Type 1 aka 'HUM_F' or 'BT1'", 1),
    ("HUM_M", "Human(Masc)", "Body Type 2 aka 'HUM_M' or 'BT2", 2)
)

base_preset_list = (

    ("GTY", "Githyanki", "Converts Humans to Githyanki", 1),
    ("DGB", "Dragonborn", "Converts Humans to DragonbornB", 2),
    ("HUM_S", "Human(Strong)", "Converts Humans(regular) to Humans(strong)", 3),
    ("GNO", "Gnome", "Converts Humans to Gnomes", 4),
    ("HFL", "Halfling", "Converts Humans to Halfling", 5),
    ("DWR", "Dwarf", "Converts Humans to Dwarves", 6),
    ("HRT", "FTM/MTF", "Converts BT1 to BT2 or vice versa", 7),
)

granny_bones= (
    
    ("LT_HUM_F", "HUM_F", "Fits body type 1(BT1) races & fem Githyanki.", 1),
    ("LT_HUM_M", "HUM_M", "Fits body type 2(BT2) races & masc Githyanki.", 2),
    ("LT_HUM_FS", "HUM_FS", "Fits body type 3(BT3) races + fem Dragonborn & Half-Orcs", 3),
    ("LT_HUM_MS", "HUM_MS", "Fits body type 4(BT4) races + masc Dragonborn & Half-Orcs", 4),
    ("LT_SHORT_F", "SHORT_F", "Fits fem Gnomes and Halflings", 5),
    ("LT_SHORT_M", "SHORT_M", "Fits masc Gnomes and Halflings", 6),
    ("LT_DWR_F", "DWR_F", "Fits fem Dwarves", 7),
    ("LT_DWR_M", "DWR_M", "Fits masc Dwarves", 8),
)    

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
preset_types= (

    ("FULL", "Full Body", "This pre-set is for converting from one body type to another. It will clear all existing transfroms.", 1),
    ("ADDATIVE", "Addative", "This pre-set is addative, meaning that its intended to be combined/layerd with other pre-sets", 2)
)
mesh_refs = (
    
    ("LT_WR_HUM_F", "HUM_F", "Reference for BT1", 1),
    ("LT_WR_HUM_M", "HUM_M", "Reference for BT2", 2),
    ("LT_WR_TIF_F_NO_TAIL", "TIF_F", "Reference for BT1 Tieflings (without tail)", 3),
    ("LT_WR_TIF_F_WITH_TAIL", "TIF_F(Tail)", "Reference for BT1 Tieflings (with tail)", 4),
    ("LT_WR_TIF_M_NO_TAIL", "TIF_M", "Reference for BT2 Tieflings(without tail)", 5),
    ("LT_WR_TIF_M_WITH_TAIL", "TIF_M(Tail)", "Reference for BT2 Tieflings (with tail)", 6),
    ("LT_WR_GTY_F", "GTY_F", "Reference for fem Githyanki.",7),
    ("LT_WR_GTY_M", "GTY_M", "Reference for Githyanki.", 8),
    ("LT_WR_HUM_FS", "HUM_FS", "Reference for BT3", 9),
    ("LT_WR_HUM_MS", "HUM_MS", "Reference for BT4", 10),
    ("LT_WR_TIF_FS_NO_TAIL", "TIF_FS", "Reference for BT3 Tieflings(without tail)", 11),
    ("LT_WR_TIF_FS_WITH_TAIL", "TIF_FS(Tail)", "Reference for BT3 Tieflings (with tail)", 12),
    ("LT_WR_TIF_MS_NO_TAIL", "TIF_MS", "Reference for BT4 Tieflings(without tail)", 13),
    ("LT_WR_TIF_MS_WITH_TAIL", "TIF_MS(Tail)", "Reference for BT4 Tieflings (with tail)", 14),
    ("LT_WR_HRC_F", "HRC_F", "Reference for fem Half-Orcs", 15),
    ("LT_WR_HRC_M", "HRC_M", "Reference for masc Half-Orcs", 16),
    ("LT_WR_DGB_F", "DGB_F", "Reference for fem Dragonborn", 17),
    ("LT_WR_DGB_M", "DGB_M", "Reference for masc Dragonborn", 18),
    ("LT_WR_GNO_F", "GNO_F", "Reference for fem Gnomes", 19),
    ("LT_WR_GNO_M", "GNO_M", "Reference for masc Gnomes", 20),
    ("LT_WR_HFL_F", "HFL_F", "Reference for fem Halflings", 21),
    ("LT_WR_HFL_M", "HFL_M", "Reference for masc Halflings", 22),
    ("LT_WR_DWR_F", "DWR_F", "Reference for fem Dwarves", 23),
    ("LT_WR_DWR_M", "DWR_M", "Reference for masc Dwarves", 24),
)


class lt_util_props(bpy.types.PropertyGroup):

    LibPath: bpy.props.StringProperty(
        name="LibPath",
        subtype='FILE_PATH',
        default=(os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor", "library", "LazyTalior_Supply_Closet.blend")),
    )

    InitBool: bpy.props.BoolProperty(
        name="InitBool",
        default=False
        ) #check to stop the user importing assets twice or attempting to run the addon while things aren't loaded
    
    from_body: bpy.props.EnumProperty(
        name="From",
        description="Name of body that you are converting FROM",
        items=base_body,
        default=(1),
    )
    to_body: bpy.props.EnumProperty(
        name="To",
        description="Name of the body that you are converting TO",
        items=base_preset_list,
        default=(3),
    )

    gilf_bones: bpy.props.EnumProperty(
        name="GR2 Armature",
        description="Export ready armature.",
        items=granny_bones,
        default=(1)
    )

    ref_bodies: bpy.props.EnumProperty(
        name="Reference Body",
        description="Body mesh to use as a reference and/or transfer weights from",
        items=mesh_refs,
        default=(1)
    )

    
class lt_user_props(bpy.types.PropertyGroup):


    from_body_action: bpy.props.StringProperty(
        name="From",
        description="Name of body that you are converting FROM",
        default=('LT_HUM_F_BASE')
    )

    to_body_action: bpy.props.StringProperty(
        name="To",
        description="Name of body that you are converting TO",
        default=('LT_HUM_F_BASE')
    )
    
    type_action: bpy.props.EnumProperty(
        name="Type",
        description="What type of pre-set this is",
        items=preset_types,
        default=(1)
    )
    creator: bpy.props.StringProperty(
        name="Creator",
        description="Who are you?",
        default="Larry Anne",
        maxlen=32,
        )
    
    desc: bpy.props.StringProperty(
        name="Description",
        description="Short description of what this pre-set does.",
        default="My Cool Pre-set :)",
        maxlen=128,
        )

