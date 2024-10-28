'''
Copyright (C) 2024 VOLNO
https://github.com/V0ln0

Created by Volno

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
from . Skeleton_Manager import *
from . Skeleton_Closet import *

bl_info = {
        "name": "BG3 Lazy Tailor",
        "description": "A tool aimed at making the proccsess of refiting outfits for various races/bodytypes for use in Baldur's Gate 3 easier.",
        "author": "Volno",
        "version": (1, 0, 0),
        "blender": (4, 2, 2),
        "location": "Pose Mode > Sidebar > BG3LazyTailor Tools tab",
        "warning": "baby's first Blender addon",
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "3D View"
        }


class LT_OT_LazyPanelMain(bpy.types.Panel):
    bl_label = "BG3 Lazy Talior"
    bl_idname = "lt.lazy_panel_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Lazy Talior"

    
    def draw(self, context):
        self.layout.operator('lt.asset_grab')
        self.layout.operator('lt.set_rest_pose')


def register():
    bpy.utils.register_class(LT_OT_LazyPanelMain)
    bpy.utils.register_class(LT_OT_set_rest_pose)
    bpy.utils.register_class(LT_OT_asset_grab)


def unregister():
    bpy.utils.unregister_class(LT_OT_LazyPanelMain)
    bpy.utils.unregister_class(LT_OT_set_rest_pose)
    bpy.utils.unregister_class(LT_OT_asset_grab)

if __name__ == "__main__":
    register()
