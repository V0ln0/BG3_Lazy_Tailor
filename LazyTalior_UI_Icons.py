# import bpy
# import os
# import bpy.utils.previews


# def LT_IconFactory(RegBool: bool):
    
#     if RegBool == True:
#         pcoll = bpy.utils.previews.new()
#         my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
#         pcoll.load("human_icon", os.path.join(my_icons_dir, "icon-human.png"), 'IMAGE')
#         preview_collections["main"] = pcoll
#     else:
#         for pcoll in preview_collections.values():
#             bpy.utils.previews.remove(pcoll)
#         preview_collections.clear()

# preview_collections = {}
