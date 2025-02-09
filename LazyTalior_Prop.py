import bpy
import os
from os import path


class tailor_props(bpy.types.PropertyGroup):

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
    
    skeleton_types = (
        
        ("LT_HUM_F", "HUM_F", "Fits body type 1(BT1) races & fem Githyanki.", 1),
        ("LT_HUM_M", "HUM_M", "Fits body type 2(BT2) races & masc Githyanki.", 2),
        ("LT_HUM_FS", "HUM_FS", "Fits body type 3(BT3) races + fem Dragonborn & Half-Orcs", 3),
        ("LT_HUM_MS", "HUM_MS", "Fits body type 4(BT4) races + masc Dragonborn & Half-Orcs", 4),
        ("LT_SHORT_F", "SHORT_F", "Fits fem Gnomes and Halflings", 5),
        ("LT_SHORT_M", "SHORT_M", "Fits masc Gnomes and Halflings", 6),
        ("LT_DWR_F", "DWR_F", "Fits fem Dwarves", 7),
        ("LT_DWR_M", "DWR_M", "Fits masc Dwarves", 8),
    )    

    race_list = (
        
        ("HUM", "Humans", "normies", 1),
        ("ELF", "Elf", "Knife Ears", 2),
        ("HEL", "Half-Elf", "Half Knife Ears", 3),
        ("TIF", "Tiefling", "Horny", 4),
        ("GTY", "Githyanki", "space frogs", 5),
        ("DGB", "Dragonborn", "scalie fucker", 6),
        ("HRC", "Half-Orc", "WAAAAAAAGH", 7),
        ("GNO", "Gnome", "you've been gnomed", 8),
        ("HFL", "Halfling", "fuck you tolkien", 9),
        ("DWR", "Dwarf", "Diggy Diggy Hole", 10)
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
    race_names: bpy.props.EnumProperty(
        name="Race",
        description="Names Of the BG3's playable races",
        items=race_list,
        default=(1)
    )
    
    gilf_bones: bpy.props.EnumProperty(
        name="GR2 skeleton",
        description="Export ready skeleton.",
        items=skeleton_types,
        default=(1)
    )

    LibPath: bpy.props.StringProperty(
        name="LibPath",
        subtype='FILE_PATH',
        default=(os.path.join(path.dirname(__file__), os.pardir, "BG3_Lazy_Tailor", "library", "LazyTalior_Supply_Closet.blend")),
        description="names of actions imported into the file"
    )






# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout
# https://blender.stackexchange.com/questions/160883/contextually-grey-out-panel-element-in-python-2-8
# https://www.programcreek.com/python/example/83073/bpy.props.EnumProperty
# https://blenderartists.org/t/add-remove-enumproperty-items/1305166


# "LT_HUM_MS_BDY"
# "LT_HUM_M_MTF"
# "LT_HUM_FS_BDY"
# "LT_HUM_F_FTM"
# "LT_HFL_M_BDY"
# "LT_HFL_F_BDY"
# "LT_GTY_M_BDY"
# "LT_GTY_F_BDY"
# "LT_GNO_M_BDY"
# "LT_GNO_F_BDY"
# "LT_DWR_M_BDY"
# "LT_DWR_F_BDY"
# "LT_DGB_M_BDY"
# "LT_DGB_F_BDY"