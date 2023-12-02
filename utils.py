import traceback
import bpy

def register_quietly(clazz):
    try:
        bpy.utils.register_class(clazz)
    except:
        pass

def unregister_quietly(clazz):
    try:
        bpy.utils.unregister_class(clazz)
    except:
        traceback.print_exc()

def get_vertices_from_group(obj, group_name):
    return [v for v in obj.data.vertices if group_name in [g.group for g in v.groups]]