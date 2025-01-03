import bpy


base_body = (
    
    ("HUM_F", "Human(Fem)", "Hu-mon feeeeeeeemale", 1),
    ("HUM_M", "Human(Masc)", "We're just normal men", 2)
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
    
    ("LT_HUM_F", "Human(Fem)", "Fits body type 1(BT1) races & fem Githyanki.", 1),
    ("LT_HUM_M", "Human(Masc)", "Fits body type 2(BT2) races & masc Githyanki.", 2),
    ("LT_HUM_FS", "Human(Fem strong)", "Fits body type 3(BT3) races + fem Dragonborn & Half-Orcs", 3),
    ("LT_HUM_MS", "Human(Masc strong)", "Fits body type 4(BT4) races + masc Dragonborn & Half-Orcs", 4),
    ("LT_SHORT_F", "Short(Fem)", "Fits fem Gnomes and Halflings", 5),
    ("LT_SHORT_M", "Short(Masc)", "Fits masc Gnomes and Halflings", 6),
    ("LT_DWR_F", "Dwarf(Fem)", "Fits fem Dwarves", 7),
    ("LT_DWR_F", "Dwarf(Masc)", "Fits masc Dwarves", 8),
)

class tailor_props(bpy.types.PropertyGroup):
    

    #stoing the names here so that if they need to be changed I only have to update the name in once place
    mannequin_base: bpy.props.StringProperty(name="mannequin_base", default="Local_Mannequin_Base")
    mannequin_form: bpy.props.StringProperty(name="mannequin_form", default="Local_Mannequin") 
    InitBool: bpy.props.BoolProperty(name="InitBool", default=False) #stops the user from doubleing up assets, todo: add system to refresh blend file's assets
    
    from_body: bpy.props.EnumProperty(
        name="From",
        description="Name of body that you are converting FROM",
        items=base_body,
        default=(2),
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
    skeleton_name: bpy.props.EnumProperty(
        name="skeleton type",
        description="Type of skeleton to be added to your scene (Note, some races share a skelenton! Read the description for each type for details)",
        items=skeleton_types,
        default=(1)
    )

# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout
# https://blender.stackexchange.com/questions/160883/contextually-grey-out-panel-element-in-python-2-8
# https://www.programcreek.com/python/example/83073/bpy.props.EnumProperty
# https://blenderartists.org/t/add-remove-enumproperty-items/1305166

