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
        # hide all the objects in render list and  then 
        # for each object in render list, show it and call render

        progress = 0
        bpy.context.window_manager.progress_begin(0, len(context.scene.render_object_list))
        # hide all the objects in render list
        for obj in context.scene.render_object_list:
            progress += 1
            bpy.context.window_manager.progress_update(progress)
            bpy.data.objects[obj.name].hide_render = True
        bpy.context.window_manager.progress_end()

        progress = 0
        bpy.context.window_manager.progress_begin(0, len(context.scene.render_object_list))
        # for each object in render list, show it and call render
        for obj in context.scene.render_object_list:
            progress += 1
            bpy.data.objects[obj.name].hide_render = False
            RENDER_OT_vertex_group.render(bpy.data.objects[obj.name])
            bpy.data.objects[obj.name].hide_render = True
            bpy.context.window_manager.progress_update(progress)
        bpy.context.window_manager.progress_end()
        return {'FINISHED'}

    def render(obj):
        # Create the subfolder in the temp directory
        subfolder_name = "render_vertex_group"
        subfolder_path = os.path.join(tempfile.gettempdir(), subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)  # 'exist_ok=True' ensures the function doesn't raise an error if the directory already exists
        
        # Render the image without any modifications first
        original_render_path = os.path.join(subfolder_path, obj.name + ".original.png")
        bpy.context.scene.render.filepath = original_render_path
        bpy.ops.render.render(write_still=True)

        if obj.type != 'MESH':
            # no more things to render if it's not a mesh
            return
        
        for group in obj.vertex_groups:
            if group.name.startswith("render_group"):
                mod = obj.modifiers.new(name="Temp Mask", type='MASK')
                mod.vertex_group = group.name

                # Update the scene so the modifier is applied
                bpy.context.view_layer.update()

                render_path = os.path.join(subfolder_path, obj.name + "." + group.name + ".png")
                bpy.context.scene.render.filepath = render_path
                bpy.ops.render.render(write_still=True)

                # Remove the temporary mask modifier
                obj.modifiers.remove(mod)


class OBJECT_OT_add_object(bpy.types.Operator):
    bl_idname = "object.add_object_to_list"
    bl_label = "+"
    
    def execute(self, context):
        for obj in context.selected_objects:
            item = context.scene.render_object_list.add()
            item.name = obj.name
        return {'FINISHED'}

class OBJECT_OT_remove_object(bpy.types.Operator):
    bl_idname = "object.remove_object_from_list"
    bl_label = "-"
    
    def execute(self, context):
        list_index = context.scene.render_object_list_index
        context.scene.render_object_list.remove(list_index)
        return {'FINISHED'}

class OBJECT_UL_object_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)

class RENDER_PT_vertex_group_panel(bpy.types.Panel):
    bl_label = "Render by Vertex Group"
    bl_idname = "RENDER_PT_vertex_group_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Group"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.template_list("OBJECT_UL_object_list", "", scene, "render_object_list", scene, "render_object_list_index")
        row = layout.row()
        row.operator("object.add_object_to_list")
        row.operator("object.remove_object_from_list")

        layout.operator("render.by_vertex_group")

def register():
    bpy.utils.register_class(RENDER_OT_vertex_group)
    bpy.utils.register_class(RENDER_PT_vertex_group_panel)
    bpy.utils.register_class(OBJECT_UL_object_list)
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_class(OBJECT_OT_remove_object)

    bpy.types.Scene.render_object_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.render_object_list_index = bpy.props.IntProperty()


def unregister():
    bpy.utils.unregister_class(RENDER_OT_vertex_group)
    bpy.utils.unregister_class(RENDER_PT_vertex_group_panel)
    bpy.utils.unregister_class(OBJECT_UL_object_list)
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_class(OBJECT_OT_remove_object)

    del bpy.types.Scene.render_object_list
    del bpy.types.Scene.render_object_list_index

if __name__ == "__main__":
    register()
