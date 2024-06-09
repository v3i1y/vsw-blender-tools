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

def render_image(file_path, file_format="PNG"):
    bpy.context.scene.render.filepath = file_path
    bpy.context.scene.render.image_settings.file_format = file_format
    bpy.ops.render.render(write_still=True)

    # check if image is empty (all pixels are transparent) and delete it if it is
    # image = bpy.data.images.load(file_path)
    # image.scale(1, 1)
    # is_empty = image.pixels[0] == 0 and image.pixels[1] == 0 and image.pixels[2] == 0 and image.pixels[3] == 0

    # # delete image and file
    # if is_empty:
    #     bpy.data.images.remove(image)
    #     os.remove(file_path)

    # return is_empty


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


        # make render visibility consistenti with viewport visibility for ALL objects and collections
        for obj in bpy.data.objects:
            obj.hide_render = obj.hide or obj.hide_viewport

        for collection in bpy.data.collections:
            should_hide = collection.hide_viewport
            for view_layer in bpy.context.scene.view_layers:
                layer_collection = view_layer.layer_collection.children.get(collection.name)
                if layer_collection:
                    hide_viewport = should_hide or layer_collection.hide_viewport
            collection.hide_render = hide_viewport

        # make an render of the original frame
        render_image(os.path.join(subfolder_path, "scene.obj.png"))


        object_names_to_render_per_group = [item.name for item in context.scene.render_object_list]
        object_names_always_present = [item.name for item in context.scene.render_object_list_always]

        # Hide all objects except for those always present
        for obj in bpy.data.objects:
            bpy.data.objects[obj.name].hide_render = not obj.name in object_names_always_present

        # Group Objects By Render Groups
        render_groups = {}
        for name in object_names_to_render_per_group:
            if '#' in name:
                group_name = name.split('#')[0]
            else:
                group_name = name
            if group_name not in render_groups:
                render_groups[group_name] = []
            render_groups[group_name].append(bpy.data.objects[name])

        for (group_name, group_objects) in render_groups.items():
            for obj in group_objects:
                bpy.data.objects[obj.name].hide_render = False
            RENDER_OT_vertex_group.render(group_name, group_objects, subfolder_path)
            for obj in group_objects:
                bpy.data.objects[obj.name].hide_render = not obj.name in object_names_always_present
        return {'FINISHED'}

    def render(group_name, objs, subfolder_path):
        zindex = 0
        count = 0

        for obj in objs:
            is_mesh = obj.type == 'MESH'
            obj_center = (obj.matrix_world @ get_centroid(obj.data.vertices)) if is_mesh else obj.location
            count += 1
            obj_zindex = get_camera_zindex(obj_center)
            zindex += obj_zindex
            zindex /= count

        # Render the image without any modifications first
        original_render_path = os.path.join(subfolder_path, "z" + str(zindex) + "." + group_name + ".obj.png")
        render_image(original_render_path)
        subsubfolder_path = os.path.join(subfolder_path, group_name + ".groups")
        for obj in objs:
            for group in obj.vertex_groups:
                if group.name.startswith("render_group"):

                    # include vertices with weight > 0.5
                    vertices = []
                    for v in obj.data.vertices:
                        for vg in v.groups:
                            if vg.weight > 0.5 and vg.group == group.index:
                                vertices.append(v.co @ obj.matrix_world)
                                break
                    # if not is_any_vertex_in_camera_view(vertices):
                    #     continue
                
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
                    # bpy.context.scene.render.filepath = render_path
                    # bpy.ops.render.render(write_still=True)
                    render_image(render_path)
                    # Remove the temporary mask modifier
                    obj.modifiers.remove(mod)


class OBJECT_OT_add_object(bpy.types.Operator):
    bl_idname = "object.add_object_to_list"
    bl_label = "+"

    list_name: bpy.props.StringProperty()
    
    def execute(self, context):
        list = getattr(context.scene, self.list_name)
        for obj in context.selected_objects:
            item = list.add()
            item.name = obj.name
        return {'FINISHED'}

class OBJECT_OT_remove_object(bpy.types.Operator):
    bl_idname = "object.remove_object_from_list"
    bl_label = "-"

    list_name: bpy.props.StringProperty()
    
    def execute(self, context):
        list = getattr(context.scene, self.list_name)
        list_index = getattr(context.scene, self.list_name + "_index")
        list.remove(list_index)
        return {'FINISHED'}

class OBJECT_UL_object_list(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)


class RENDER_OT_swap_width_height(bpy.types.Operator):
    bl_idname = "render.swap_width_height"
    bl_label = "Swap Width and Height"
    bl_description = "Swaps the width and height of the render"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        width = context.scene.render_groups_width
        height = context.scene.render_groups_height
        context.scene.render_groups_width = height
        context.scene.render_groups_height = width
        return {'FINISHED'}

    # bl_idname = "render.render_res_portrait"
    # bl_label = "Render Portrait"
    # bl_description = "Renders the scene in portrait mode"
    # bl_options = {'REGISTER', 'UNDO'}

    
    # portrait: bpy.props.BoolProperty(name="Portrait", default=True)

    # def execute(self, context):
    #     width = context.scene.render_groups_width
    #     height = context.scene.render_groups_height
    #     if self.portrait == width > height:
    #         context.scene.render_groups_width = height
    #         context.scene.render_groups_height = width
    #     return {'FINISHED'}

    

class RENDER_PT_vertex_group_panel(bpy.types.Panel):
    bl_label = "Render by Vertex Group"
    bl_idname = "RENDER_PT_vertex_group_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Render Group"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Always Present")
        layout.template_list("OBJECT_UL_object_list", "", scene, "render_object_list_always", scene, "render_object_list_always_index")
        row = layout.row()
        props = row.operator("object.add_object_to_list")
        props.list_name = "render_object_list_always"
        props = row.operator("object.remove_object_from_list")
        props.list_name = "render_object_list_always"

        layout.label(text="Render Groups")
        layout.template_list("OBJECT_UL_object_list", "", scene, "render_object_list", scene, "render_object_list_index")
        row = layout.row()
        props = row.operator("object.add_object_to_list")
        props.list_name = "render_object_list"
        props = row.operator("object.remove_object_from_list")
        props.list_name = "render_object_list"

        layout.label(text="Render Size")
        row = layout.row()
        row.prop(scene, "render_focal_length")
        row = layout.row()
        row.prop(scene, "render_focal_object")
        row = layout.row()
        row.prop(scene, "render_groups_width")
        row.prop(scene, "render_groups_height")
        row = layout.row()
        row.operator("render.swap_width_height")

        layout.label(text="")
        layout.operator("render.by_vertex_group")

class RENDER_PT_render_thumbnail(bpy.types.Panel):
    bl_label = "Render Thumbnail"
    bl_idname = "RENDER_PT_render_thumbnail"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"
    def draw(self, context):
        layout = self.layout
        layout.operator("render.render_thumbnail")

class RENDER_OT_render_thumbnail(bpy.types.Operator):
    bl_idname = "render.render_thumbnail"
    bl_label = "Render Thumbnail"
    bl_description = "Renders the scene as a thumbnail"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create the subfolder in the temp directory
        # make render visibility consistenti with viewport visibility for ALL objects and collections
        for obj in bpy.data.objects:
            obj.hide_render = obj.hide or obj.hide_viewport

        for collection in bpy.data.collections:
            should_hide = collection.hide_viewport
            for view_layer in bpy.context.scene.view_layers:
                layer_collection = view_layer.layer_collection.children.get(collection.name)
                if layer_collection:
                    hide_viewport = should_hide or layer_collection.hide_viewport
            collection.hide_render = hide_viewport

        # make an render of the original frame
        render_image(os.path.join(os.path.dirname(bpy.data.filepath), "folder.jpg"), "JPEG")
        return {'FINISHED'}


class ViewportFlipOperator(bpy.types.Operator):
    """Flip the viewport view horizontally"""
    bl_idname = "view3d.flip_viewport_view"
    bl_label = "Flip Viewport View"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        # Get the active camera if exists
        cam = bpy.context.scene.camera 
        if cam:
            cam.scale.x = -cam.scale.x
        else:
            self.report({'WARNING'}, "No active camera found")
        return {'FINISHED'}

def raycast_camera():
    camera = bpy.context.scene.camera
    scene = bpy.context.scene
    camera_matrix = camera.matrix_world.normalized()
    ray_direction = camera_matrix.to_3x3() @ mathutils.Vector((0.0, 0.0, -1.0))
    ray_origin = camera_matrix.to_translation()
    result, location, normal, index, object, matrix = scene.ray_cast(
        bpy.context.view_layer.depsgraph, ray_origin, ray_direction)
    return location if result else mathutils.Vector((0.0, 0.0, 0.0))

def update_resolution(self, context):
    render = context.scene.render
    render.resolution_x = context.scene.render_groups_width
    render.resolution_y = context.scene.render_groups_height

    camera = bpy.context.scene.camera

    # before adjust focal length, adjust camera location so that the relative size of the subject is the about the same
    old_focal_length = camera.data.lens
    new_focal_length = context.scene.render_focal_length
    subject_location = raycast_camera() if context.scene.render_focal_object is None else context.scene.render_focal_object.location
    current_distance = (camera.location - subject_location).length
    new_distance = (new_focal_length * current_distance) / old_focal_length
    direction_vector = (subject_location - camera.location).normalized()
    new_camera_location = subject_location - direction_vector * new_distance

    camera.location = new_camera_location
    camera.data.lens = new_focal_length


def register():
    bpy.utils.register_class(RENDER_OT_vertex_group)
    bpy.utils.register_class(RENDER_PT_vertex_group_panel)
    bpy.utils.register_class(OBJECT_UL_object_list)
    bpy.utils.register_class(OBJECT_OT_add_object)
    bpy.utils.register_class(OBJECT_OT_remove_object)
    bpy.utils.register_class(RENDER_OT_swap_width_height)
    bpy.utils.register_class(ViewportFlipOperator)
    bpy.utils.register_class(RENDER_OT_render_thumbnail)
    bpy.utils.register_class(RENDER_PT_render_thumbnail)

    bpy.types.Scene.render_object_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.render_object_list_index = bpy.props.IntProperty()
    
    bpy.types.Scene.render_object_list_always = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.Scene.render_object_list_always_index = bpy.props.IntProperty()


    bpy.types.Scene.render_focal_object = bpy.props.PointerProperty(type=bpy.types.Object, name="Focal Point")

    bpy.types.Scene.render_focal_length = bpy.props.IntProperty(name="Focal Length", default=50, min=20, max=200, update=update_resolution)
    bpy.types.Scene.render_groups_width = bpy.props.IntProperty(name="Width", default=1080, update=update_resolution)
    bpy.types.Scene.render_groups_height = bpy.props.IntProperty(name="Height", default=1080, update=update_resolution)


def unregister():
    bpy.utils.unregister_class(RENDER_OT_vertex_group)
    bpy.utils.unregister_class(RENDER_PT_vertex_group_panel)
    bpy.utils.unregister_class(OBJECT_UL_object_list)
    bpy.utils.unregister_class(OBJECT_OT_add_object)
    bpy.utils.unregister_class(OBJECT_OT_remove_object)
    bpy.utils.unregister_class(RENDER_OT_swap_width_height)
    bpy.utils.unregister_class(ViewportFlipOperator)
    bpy.utils.unregister_class(RENDER_OT_render_thumbnail)
    bpy.utils.unregister_class(RENDER_PT_render_thumbnail)

    del bpy.types.Scene.render_object_list
    del bpy.types.Scene.render_object_list_index

    del bpy.types.Scene.render_object_list_always
    del bpy.types.Scene.render_object_list_always_index

    del bpy.types.Scene.render_groups_width
    del bpy.types.Scene.render_groups_height

if __name__ == "__main__":
    register()
