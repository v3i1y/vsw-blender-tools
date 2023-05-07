import bpy
import re
from bpy.props import PointerProperty
from . import utils

class ChangeCanvasOrientation(bpy.types.Operator):
    bl_idname = "vsw.canvas_ort"
    bl_label = "Diff Helper"
    bl_description = "Diff Helper"
    bl_options = { "REGISTER", "UNDO" }

    horizontal: bpy.props.BoolProperty()
    
    def execute(self, context):

        if self.horizontal:
            bpy.data.scenes["Scene"].render.resolution_x = 3000
            bpy.data.scenes["Scene"].render.resolution_y = 2000
        else:
            bpy.data.scenes["Scene"].render.resolution_x = 2000
            bpy.data.scenes["Scene"].render.resolution_y = 3000


        return { "FINISHED"}


class CanvasHelper_PT_Panel(bpy.types.Panel):
    bl_label = "Canvas Helper"
    bl_category = "View"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(self, context):
        return True
    
    def draw(self, context):
        row = self.layout.row()
        row.label(text="Camera Focal Length")
        row.prop(bpy.data.scenes["Scene"].camera.data, "lens")

        row = self.layout.row()
        ops = row.operator("vsw.canvas_ort", text="Landscape")
        ops.horizontal = True
        ops = row.operator("vsw.canvas_ort", text="Portrait")
        ops.horizontal = False

        

def register():
    # tools to link metarig to rigifyrig
    utils.register_quietly(CanvasHelper_PT_Panel)
    utils.register_quietly(ChangeCanvasOrientation)
    
def unregister():
    utils.unregister_quietly(CanvasHelper_PT_Panel)
    utils.unregister_quietly(ChangeCanvasOrientation)
