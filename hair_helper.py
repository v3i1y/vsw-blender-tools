import bpy
import bmesh

def add_hair_strand_prototype(self, context):
    mesh = bpy.data.meshes.new(name="Hair Strand Mesh")
    obj = bpy.data.objects.new("Hair Strand Prototype", mesh)

    # Move it to the cursor
    obj.location = bpy.context.scene.cursor.location

    # Link it to the scene
    bpy.context.collection.objects.link(obj)
    # bpy.context.view_layer.objects.active = obj
    # obj.select_set(True)

    # Set the active object as the parent, while keeping the current transform
    active_obj = bpy.context.view_layer.objects.active  # Get the currently active object

    if active_obj:
        active_obj.select_set(True)  # Select the active object
        obj.select_set(True)  # Select the new object
        bpy.context.view_layer.objects.active = active_obj  # Ensure the active object is set as active

        # Set the active object as the parent, while keeping the current transform
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # Create mesh data
    bm = bmesh.new()
    vert1 = bm.verts.new((-0.025, 0, 0))
    vert2 = bm.verts.new((0.025, 0, 0))
    edge = bm.edges.new((vert1, vert2))
    bm.to_mesh(mesh)
    bm.free()

    # Add vertex group "thickness"
    group = obj.vertex_groups.new(name="thickness")
    for vert in mesh.vertices:
        group.add([vert.index], 1.0, 'ADD')

    # Add Solidify Modifier
    solidify = obj.modifiers.new(name="Solidify", type='SOLIDIFY')
    solidify.thickness = 0.01
    solidify.offset = -1
    solidify.vertex_group = "thickness"
    solidify.thickness_vertex_group = 0.2

    # Add Subdivision Surface Modifier
    subdivision = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    subdivision.levels = 2
    subdivision.render_levels = 2

    return {'FINISHED'}

class OBJECT_OT_add_hair_strand_prototype(bpy.types.Operator):
    bl_idname = "mesh.add_hair_strand_prototype"
    bl_label = "Add Hair Strand Prototype"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return add_hair_strand_prototype(self, context)

def menu_func(self, context):
    self.layout.operator(OBJECT_OT_add_hair_strand_prototype.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_add_hair_strand_prototype)
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_hair_strand_prototype)
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)