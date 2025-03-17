import bpy


class preset:
    
    @staticmethod
    def get_short_name(name:str, is_base=False):
        
        if is_base:
            return (name.replace('LT_','')).replace('_BASE','')
        else:    
            return name.replace('LT_','')
    @staticmethod
    def is_not_defualt(action):
        return bool(action.get('LT_Default') is None)
    #TODO: hyphonate this shit
    @classmethod
    def draw_preset_info(cls, self, context, layout, is_dopesheet: bool):

        if is_dopesheet:
            active_preset = bpy.data.objects["Local_Mannequin"].animation_data.action
        else:
            active_preset = bpy.context.scene.lt_actions
    
        for index, key, in enumerate(active_preset.items()):
            if key[0].startswith('LT_'):
                #removes 'LT_' from prop name and combines its value into a string
                #absolutely awful I know
                if key[0] in ('LT_From_Body', 'LT_To_Body'):

                    #turns "LT_To_Body', 'LT_HUM_MS_BASE'" into " To_Body: HUM_MS"
                    layout.label(text=f"{self.get_short_name(key[0])}: {(key[1].replace('LT_','')).replace('_BASE','')}")
                else:
                    #turns "LT_Creator', 'Volno'" into "Creator: Volno"
                    layout.label(text=f"{self.get_short_name(key[0])}: {key[1]}")


class LT_MT_about_preset_scene_menu(preset, bpy.types.Menu):
    
    bl_idname = "LT_MT_about_preset_scene_menu"
    bl_label = "About Pre-Set"
    
    def draw(self, context):
        self.draw_preset_info(self, context, self.layout, is_dopesheet=False)

def confirm_Popup(do_that: str, op_name: str, extra: bool, extra_con: str): 

    def draw(self, context):
        self.layout.label(text=f"Are you sure that you wish to {do_that}?")
        if extra == True:
            self.layout.label(text=extra_con)
        self.layout.operator(op_name, text= "Yes, do it.")
            
    bpy.context.window_manager.popup_menu(draw, title = "Confirm Choice", icon = 'QUESTION')

class LT_OT_confirm_choice(bpy.types.Operator):
    
    bl_idname = "lt.confirm_choice"
    bl_label = "confirm_choice"
    bl_description = "*John Cena voice* are you sure about that?"
      
    the_thing: bpy.props.StringProperty(
        name="the_thing",
        default="If you're reading this, I forgot to set it",
    )

    op_name: bpy.props.StringProperty(
        name="op_name",
        default="",
    )

    warn_extra: bpy.props.BoolProperty(
        name="warn_extra",
        default=False
    )

    warn_message: bpy.props.StringProperty(
        name="op_name",
        default="If you're reading this, I forgot to set TWO things",
    )

    def execute(self, context):
        confirm_Popup((self.the_thing), (self.op_name), (self.warn_extra), (self.warn_message))
        return {"FINISHED"}

