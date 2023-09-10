bl_info = {
    "name": "Render by Vertex Group",
    "description": "Renders different parts of the mesh using vertex groups",
    "author": "ChatGPT",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "3D View > Sidebar > My Tab",
    "category": "Render",
}

import bpy
import os
import tempfile

class RENDER_OT_vertex_group(bpy.types.Operator):
    bl_idname = "render.by_vertex_group"
    bl_label = "Render by Vertex Group"
    bl_description = "Renders different parts of the mesh using vertex groups whose names start with 'render_group'"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh!")
            return {'CANCELLED'}
        
        # Create the subfolder in the temp directory
        subfolder_name = "render_vertex_group"
        subfolder_path = os.path.join(tempfile.gettempdir(), subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)  # 'exist_ok=True' ensures the function doesn't raise an error if the directory already exists
        
        # Render the image without any modifications first
        original_render_path = os.path.join(subfolder_path, "original.png")
        bpy.context.scene.render.filepath = original_render_path
        bpy.ops.render.render(write_still=True)

        for group in obj.vertex_groups:
            if group.name.startswith("render_group"):
                mod = obj.modifiers.new(name="Temp Mask", type='MASK')
                mod.vertex_group = group.name

                # Update the scene so the modifier is applied
                bpy.context.view_layer.update()

                render_path = os.path.join(subfolder_path, group.name + ".png")
                bpy.context.scene.render.filepath = render_path
                bpy.ops.render.render(write_still=True)

                # Remove the temporary mask modifier
                obj.modifiers.remove(mod)

        self.report({'INFO'}, "Rendering Complete!")
        return {'FINISHED'}

class RENDER_PT_vertex_group_panel(bpy.types.Panel):
    bl_label = "Render by Vertex Group"
    bl_idname = "RENDER_PT_vertex_group_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Group"

    def draw(self, context):
        layout = self.layout
        layout.operator("render.by_vertex_group")

def register():
    bpy.utils.register_class(RENDER_OT_vertex_group)
    bpy.utils.register_class(RENDER_PT_vertex_group_panel)

def unregister():
    bpy.utils.unregister_class(RENDER_OT_vertex_group)
    bpy.utils.unregister_class(RENDER_PT_vertex_group_panel)

if __name__ == "__main__":
    register()
