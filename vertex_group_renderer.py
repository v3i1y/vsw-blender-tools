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
import mathutils
import os
import tempfile
import math
from datetime import datetime

def get_centroid(vertices):
    if len(vertices) == 0:
        return mathutils.Vector((0, 0, 0))
    x = 0
    y = 0
    z = 0
    for vertex in vertices:
        # check if it has co property
        if hasattr(vertex, "co"):
            vertex = vertex.co
        x += vertex[0]
        y += vertex[1]
        z += vertex[2]
    return mathutils.Vector((x / len(vertices), y / len(vertices), z / len(vertices)))

def get_camera_zindex(location):
    camera = bpy.context.scene.camera
    if camera is None:
        return 0
    camera_space = camera.matrix_world.inverted() @ location
    return round(camera_space[2] * 1000)

def is_any_vertex_in_camera_view(vertices):
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    if camera is None:
        return False
    camera_matrix = camera.matrix_world.inverted()
    for vertex in vertices:
        local_coord = camera_matrix @ vertex

        # Ensure the point is in front of the camera
        if local_coord.z > 0:
            return False

        # Get camera parameters
        cam_data = camera.data
        aspect_ratio = cam_data.sensor_width / cam_data.sensor_height
        tan_fov = 2 * math.tan(cam_data.angle / 2)
        half_width = tan_fov * aspect_ratio
        half_height = tan_fov

        # Calculate the normalized device coordinate (NDC)
        ndc_x = local_coord.x / (-local_coord.z * half_width)
        ndc_y = local_coord.y / (-local_coord.z * half_height)

        # Check if the NDC is within [-1, 1] range for both x and y
        if not (-1 <= ndc_x <= 1 and -1 <= ndc_y <= 1):
            return True
    return False

class RENDER_OT_vertex_group(bpy.types.Operator):
    bl_idname = "render.by_vertex_group"
    bl_label = "Render by Vertex Group"
    bl_description = "Renders different parts of the mesh using vertex groups whose names start with 'render_group'"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # hide all the objects in render list and  then 
        # for each object in render list, show it and call render

        
        # Create the subfolder in the temp directory
        subfolder_name = "render_vertex_group"
        subfolder_path = os.path.join(os.path.dirname(bpy.data.filepath) if bpy.data.filepath else tempfile.gettempdir(), subfolder_name)
        subfolder_path = os.path.join(subfolder_path, datetime.now().strftime("%Y%m%d%H%M%S%f"))
        os.makedirs(subfolder_path, exist_ok=True)  # 'exist_ok=True' ensures the function doesn't raise an error if the directory already exists

        # make an render of the original frame
        bpy.context.scene.render.filepath = os.path.join(subfolder_path, "scene.png")
        bpy.ops.render.render(write_still=True)

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
            RENDER_OT_vertex_group.render(bpy.data.objects[obj.name], subfolder_path)
            bpy.data.objects[obj.name].hide_render = True
            bpy.context.window_manager.progress_update(progress)
        bpy.context.window_manager.progress_end()
        return {'FINISHED'}

    def render(obj, subfolder_path):
        
        is_mesh = obj.type == 'MESH'
        obj_center = (obj.matrix_world @ get_centroid(obj.data.vertices)) if is_mesh else obj.location
        obj_zindex = get_camera_zindex(obj_center)

        # Render the image without any modifications first
        original_render_path = os.path.join(subfolder_path, "z" + str(obj_zindex) + "." + obj.name + ".obj.png")
        bpy.context.scene.render.filepath = original_render_path
        bpy.ops.render.render(write_still=True)

        if not is_mesh:
            # no more things to render if it's not a mesh
            return
        subsubfolder_path = os.path.join(subfolder_path, obj.name + ".groups")
        for group in obj.vertex_groups:
            if group.name.startswith("render_group"):

                # include vertices with weight > 0.5
                vertices = []
                for v in obj.data.vertices:
                    for vg in v.groups:
                        if vg.weight > 0.5 and vg.group == group.index:
                            vertices.append(v.co @ obj.matrix_world)
                            break
                if not is_any_vertex_in_camera_view(vertices):
                    continue
            
                mod = obj.modifiers.new(name="Temp Mask", type='MASK')
                mod.vertex_group = group.name
                group_center = get_centroid(vertices)
                group_zindex = get_camera_zindex(group_center)
                # Update the scene so the modifier is applied
                bpy.context.view_layer.update()
                # remove render_group or render_group_ from the group name
                group_name_for_file = group.name.replace("render_group_", "").replace("render_group", "")
                os.makedirs(subsubfolder_path, exist_ok=True)
                render_path = os.path.join(subsubfolder_path, "z" + str(group_zindex) + "." + obj.name + "." + group_name_for_file + ".png")
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
