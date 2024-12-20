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
    ("HRT", "trans", "transes your gender", 7),
)


class tailor_props(bpy.types.PropertyGroup):
    mannequin_base: bpy.props.StringProperty(name="mannequin_base", default="Local_Mannequin_Base")
    mannequin_form: bpy.props.StringProperty(name="mannequin_form", default="Local_Mannequin") 
    InitBool: bpy.props.BoolProperty(name="InitBool", default=False)
    from_body: bpy.props.EnumProperty(
        name="From",
        description="The target game. Currently determines the model format type",
        items=base_body,
        default=(1),
    )
    to_body: bpy.props.EnumProperty(
        name="To",
        description="The target game. Currently determines the model format type",
        items=base_preset_list,
        default=(1),
    )



# https://docs.blender.org/api/4.3/bpy.props.html#propertygroup-example
# https://docs.blender.org/api/4.3/bpy.types.UILayout.html#bpy.types.UILayout
# https://blender.stackexchange.com/questions/160883/contextually-grey-out-panel-element-in-python-2-8
# https://www.programcreek.com/python/example/83073/bpy.props.EnumProperty
# https://blenderartists.org/t/add-remove-enumproperty-items/1305166

