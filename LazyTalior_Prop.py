import bpy
import os
from os import path


#BEHOLD... my enums
base_body = (
    
    ("HUM_F", "Human(Fem)", "Hu-mon feeeeeeeemale", 1),
    ("HUM_M", "Human(Masc)", "We're just normal men", 2)
)

base_preset_list = (

    ("GTY", "Githyanki", "space frogs", 1),
    ("DGB", "Dragonborn", "scalie fucker", 2),
    ("HUM_S", "Human(Strong)", "roids", 3),
    ("GNO", "Gnome", "you've been gnomed", 4),
    ("HFL", "Halfling", "fuck you tolkien", 5),
    ("DWR", "Dwarf", "Diggy Diggy Hole", 6),
    ("HRT", "FTM/MTF", "transes your gender", 7),
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
    ("ADD", "Addative", "This pre-set is addative, meaning that its intended to be combined/layerd with other pre-sets", 2)
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
    ("LT_WR_HRC_FS", "HRC_FS", "Reference for fem Half-Orcs", 15),
    ("LT_WR_HRC_MS", "HRC_MS", "Reference for masc Half-Orcs", 16),
    ("LT_WR_DGB_F", "DGB_F", "Reference for fem Dragonborn", 17),
    ("LT_WR_DGB_M", "DGB_M", "Reference for masc Dragonborn", 18),
    ("LT_WR_GNO_F", "GNO_F", "Reference for fem Gnomes", 19),
    ("LT_WR_GNO_M", "GNO_M", "Reference for masc Gnomes", 20),
    ("LT_WR_HFL_F", "HFL_F", "Reference for fem Halflings", 21),
    ("LT_WR_HFL_M", "HFL_M", "Reference for masc Halflings", 22),
    ("LT_WR_DWR_F", "DWR_F", "Reference for fem Dwarves", 23),
    ("LT_WR_DWR_M", "DWR_M", "Reference for masc Dwarves", 24),
)


# race_list = (
    
#     ("HUM", "Humans", "normies", 1),
#     ("ELF", "Elf", "Knife Ears", 2),
#     ("HEL", "Half-Elf", "Half Knife Ears", 3),
#     ("TIF", "Tiefling", "Horny", 4),
#     ("GTY", "Githyanki", "space frogs", 5),
#     ("DGB", "Dragonborn", "scalie fucker", 6),
#     ("HRC", "Half-Orc", "WAAAAAAAGH", 7),
#     ("GNO", "Gnome", "you've been gnomed", 8),
#     ("HFL", "Halfling", "fuck you tolkien", 9),
#     ("DWR", "Dwarf", "Diggy Diggy Hole", 10)
# )


class lt_util_props(bpy.types.PropertyGroup):

    LibPath: bpy.props.StringProperty(
        name="LibPath",
        subtype='FILE_PATH',
        default=(os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor", "library", "LazyTalior_Supply_Closet.blend")),
        description="names of actions imported into the file"
    )

    InitBool: bpy.props.BoolProperty(
        name="InitBool",
        default=False
        ) #stops the user from doubleing up assets, todo: add system to refresh blend file's assets
    
    #might need to move these into a panel prop if we wanna do custom icons
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
    # race_names: bpy.props.EnumProperty(
    #     name="Race",
    #     description="Names Of the BG3's playable races",
    #     items=race_list,
    #     default=(1)
    # )
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
    
    from_body_action: bpy.props.EnumProperty(
        name="From",
        description="Name of body that you are converting FROM",
        items=base_bones,
        default=(1)
    )

    to_body_action: bpy.props.EnumProperty(
        name="To",
        description="Name of body that you are converting TO",
        items=base_bones,
        default=(1)
    )
    
    type_action: bpy.props.EnumProperty(
        name="Type",
        description="What type of pre-set this is",
        items=preset_types,
        default=(1)
    )
    creator: bpy.props.StringProperty(
        name="Creator",
        default="Larry Anne",
        maxlen=64,
        )
    
    preset_desc: bpy.props.StringProperty(
        name="Description",
        default="",
        maxlen=128,
        )
